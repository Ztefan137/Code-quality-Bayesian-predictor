import argparse
import base64
import csv
import hashlib
import io
import json
import os
import re
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


API_ROOT = "https://api.github.com"
APPROVED_LICENSES = {"MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0"}
SOURCE_EXTENSIONS = {".cpp", ".cc", ".cxx"}
EXCLUDED_DIRECTORIES = {
    "build",
    "cmake-build-debug",
    "cmake-build-release",
    "generated",
    "node_modules",
    "third_party",
    "vendor",
}
DATASET_FIELDS = ["File Name", "Score", "Status"]


class DownloadTooLargeError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token=None):
        self.token = token

    def _read_url(self, url, accept, max_bytes=None):
        headers = {
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "code-quality-bayesian-predictor-data-collector",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(url, headers=headers)

        try:
            with urlopen(request, timeout=30) as response:
                if max_bytes is not None:
                    contents = response.read(max_bytes + 1)
                    if len(contents) > max_bytes:
                        raise DownloadTooLargeError(
                            f"Download from {url} exceeded the {max_bytes}-byte limit"
                        )
                    return contents
                return response.read()
        except HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"GitHub returned HTTP {error.code} for {url}: {details}"
            ) from error
        except URLError as error:
            raise RuntimeError(f"Could not reach GitHub at {url}: {error.reason}") from error

    def get_json(self, endpoint):
        response = self._read_url(f"{API_ROOT}{endpoint}", "application/vnd.github+json")
        try:
            return json.loads(response)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RuntimeError(f"GitHub returned invalid JSON for {endpoint}") from error

    def get_raw(self, url):
        return self._read_url(url, "application/vnd.github.raw+json")

    def get_archive(self, full_name, branch, max_bytes):
        repository_path = quote(full_name, safe="/")
        branch_path = quote(branch, safe="")
        url = (
            f"https://codeload.github.com/{repository_path}/zip/"
            f"refs/heads/{branch_path}"
        )
        return self._read_url(
            url, "application/vnd.github+json", max_bytes=max_bytes
        )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Collect permissively licensed C++ files for human quality review."
    )
    parser.add_argument(
        "--query",
        required=True,
        help='GitHub repository search query, for example: "language:C++ topic:algorithms"',
    )
    parser.add_argument("--max-repos", type=int, default=5)
    parser.add_argument("--max-files", type=int, default=20)
    parser.add_argument("--max-files-per-repo", type=int, default=20)
    parser.add_argument("--max-file-bytes", type=int, default=100_000)
    parser.add_argument("--max-archive-bytes", type=int, default=50_000_000)
    parser.add_argument("--dataset", type=Path, default=Path("data/dataset.csv"))
    parser.add_argument(
        "--source-dir", type=Path, default=Path("data/source_files")
    )
    return parser.parse_args()


def search_repositories(client, query, max_repos):
    repositories = []
    for page in range(1, (max_repos + 99) // 100 + 1):
        remaining = max_repos - len(repositories)
        parameters = urlencode(
            {
                "q": query,
                "per_page": min(remaining, 100),
                "page": page,
            }
        )
        response = client.get_json(f"/search/repositories?{parameters}")
        items = response.get("items", [])
        repositories.extend(items)
        if len(items) < min(remaining, 100):
            break
    return repositories[:max_repos]


def has_approved_license(repository):
    license_info = repository.get("license") or {}
    return license_info.get("spdx_id") in APPROVED_LICENSES


def get_license_file(client, full_name):
    response = client.get_json(f"/repos/{full_name}/license")
    content = response.get("content")
    if not content or response.get("encoding") != "base64":
        raise RuntimeError(f"Could not retrieve license text for {full_name}")

    try:
        return base64.b64decode(content)
    except ValueError as error:
        raise RuntimeError(f"Invalid license text returned for {full_name}") from error


def list_candidate_sources(archive, max_file_bytes, max_files=None):
    candidates = []
    try:
        zip_file = zipfile.ZipFile(io.BytesIO(archive))
    except zipfile.BadZipFile as error:
        raise RuntimeError("GitHub returned an invalid repository archive.") from error

    with zip_file:
        for entry in zip_file.infolist():
            archive_path = PurePosixPath(entry.filename)
            if entry.is_dir() or len(archive_path.parts) < 2:
                continue
            if stat.S_ISLNK(entry.external_attr >> 16):
                continue

            source_path = PurePosixPath(*archive_path.parts[1:])
            if ".." in source_path.parts:
                continue
            if source_path.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            if EXCLUDED_DIRECTORIES.intersection(
                part.lower() for part in source_path.parts[:-1]
            ):
                continue
            if entry.file_size > max_file_bytes:
                continue

            candidates.append((source_path, zip_file.read(entry)))
            if max_files is not None and len(candidates) >= max_files:
                break

    return candidates


def make_local_filename(full_name, source_path):
    components = [full_name, *source_path.parts]
    readable_name = re.sub(r"[^A-Za-z0-9._-]+", "_", "__".join(components))
    extension = source_path.suffix.lower()
    digest = hashlib.sha256(
        f"{full_name}:{source_path.as_posix()}".encode("utf-8")
    ).hexdigest()[:10]
    stem = Path(readable_name).stem[:160]
    return f"{stem}_{digest}{extension}"


def collect_repository(
    client, repository, source_dir, max_files, max_file_bytes, max_archive_bytes
):
    full_name = repository["full_name"]
    if not has_approved_license(repository):
        print(f"Skipping {full_name}: no approved explicit license.")
        return []

    branch = repository.get("default_branch")
    if not branch:
        print(f"Skipping {full_name}: default branch is unavailable.")
        return []

    archive = client.get_archive(full_name, branch, max_archive_bytes)
    candidates = list_candidate_sources(archive, max_file_bytes, max_files)
    if not candidates:
        print(f"No eligible C++ source files found in {full_name}.")
        return []

    license_contents = get_license_file(client, full_name)
    license_directory = source_dir / "licenses"
    license_directory.mkdir(parents=True, exist_ok=True)
    license_filename = make_local_filename(full_name, PurePosixPath("LICENSE"))
    license_path = license_directory / license_filename
    license_path.write_bytes(license_contents)

    rows = []
    for source_path, contents in candidates:
        file_name = make_local_filename(full_name, source_path)
        local_path = source_dir / file_name
        if local_path.exists():
            print(f"Using existing source file: {local_path}")
        else:
            local_path.write_bytes(contents)
        rows.append(
            {
                "File Name": file_name,
                "Score": "NaN",
                "Status": "review",
            }
        )
        print(f"Added {full_name}/{source_path} for review.")

    return rows


def append_dataset_rows(dataset_path, rows):
    existing_rows = []
    existing_fieldnames = []
    if dataset_path.exists():
        with dataset_path.open("r", encoding="utf-8", newline="") as dataset_file:
            reader = csv.DictReader(dataset_file)
            existing_fieldnames = reader.fieldnames or []
            existing_rows = [
                {field: row.get(field, "") for field in DATASET_FIELDS}
                for row in reader
            ]
    elif not rows:
        return 0

    existing_names = {row.get("File Name", "") for row in existing_rows}
    new_rows = []
    for row in rows:
        file_name = row["File Name"]
        if file_name in existing_names:
            continue
        new_rows.append({field: row.get(field, "") for field in DATASET_FIELDS})
        existing_names.add(file_name)
    if not new_rows and existing_fieldnames == DATASET_FIELDS:
        print("No new dataset rows to append.")
        return 0

    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="",
        dir=dataset_path.parent,
        delete=False,
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)
        writer = csv.DictWriter(temporary_file, fieldnames=DATASET_FIELDS)
        writer.writeheader()
        writer.writerows(existing_rows)
        writer.writerows(new_rows)

    os.replace(temporary_path, dataset_path)
    return len(new_rows)


def main():
    args = parse_arguments()
    if (
        args.max_repos < 1
        or args.max_repos > 1000
        or args.max_files < 1
        or args.max_files_per_repo < 1
        or args.max_file_bytes < 1
        or args.max_archive_bytes < 1
    ):
        print(
            "Limits must be positive; --max-repos cannot exceed GitHub's 1000-result search limit.",
            file=sys.stderr,
        )
        return 2

    client = GitHubClient(os.environ.get("GITHUB_TOKEN"))
    added_count = 0
    try:
        repositories = search_repositories(client, args.query, args.max_repos)
        for repository in repositories:
            remaining_files = args.max_files - added_count
            if remaining_files <= 0:
                break
            try:
                repository_rows = collect_repository(
                    client,
                    repository,
                    args.source_dir,
                    min(remaining_files, args.max_files_per_repo),
                    args.max_file_bytes,
                    args.max_archive_bytes,
                )
            except DownloadTooLargeError as error:
                print(f"Skipping {repository['full_name']}: {error}", file=sys.stderr)
                continue
            added_count += append_dataset_rows(args.dataset, repository_rows)
    except RuntimeError as error:
        print(f"Collection failed: {error}", file=sys.stderr)
        return 1

    print(f"Added {added_count} files to {args.dataset}; imported files are marked for review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
