import os
import clang.cindex

class FeatureExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        
        self.index = clang.cindex.Index.create()
        try:
            self.tu = self.index.parse(self.file_path, args=['-std=c++17'])
        except Exception as e:
            raise RuntimeError(f"Failed to parse C++ file with libclang: {e}")

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.content = f.read()
            self.lines = self.content.splitlines()

    def extract_all(self):
        """Extracts all metrics using libclang AST and token analysis."""
        return {
            "comment_percentage": self._get_comment_percentage(),
            "cyclomatic_complexity": self._get_cyclomatic_complexity(),
            "variable_counts": self._get_variable_counts(),
            "const_keyword_count": self._get_const_count(),
            "constant_count": self._get_magic_constants_count()
        }

    def _get_comment_percentage(self):
        """Calculates comment percentage using libclang token stream."""
        total_lines = len(self.lines)
        if total_lines == 0:
            return 0.0

        comment_lines = set()
        for token in self.tu.get_tokens(extent=self.tu.cursor.extent):
            if token.kind == clang.cindex.TokenKind.COMMENT:
                start_line = token.location.line
                end_line = token.extent.end.line
                for line_num in range(start_line, end_line + 1):
                    comment_lines.add(line_num)

        return round((len(comment_lines) / total_lines) * 100, 2)

    def _get_cyclomatic_complexity(self):
        """Calculates cyclomatic complexity for the user file only (ignoring headers)."""
        complexity = 1
        target_path = os.path.abspath(self.file_path)

        def traverse(node):
            nonlocal complexity
            
            if node.location.file:
                node_path = os.path.abspath(node.location.file.name)
                if node_path == target_path:
                    if node.kind in (
                        clang.cindex.CursorKind.IF_STMT,
                        clang.cindex.CursorKind.FOR_STMT,
                        clang.cindex.CursorKind.WHILE_STMT,
                        clang.cindex.CursorKind.SWITCH_STMT,
                        clang.cindex.CursorKind.CASE_STMT,
                        clang.cindex.CursorKind.CXX_FOR_RANGE_STMT
                    ):
                        complexity += 1

            for child in node.get_children():
                traverse(child)

        traverse(self.tu.cursor)
        return complexity

    def _get_variable_counts(self):
        """Counts how many times each variable identifier is referenced (user file only)."""
        counts = {}
        target_path = os.path.abspath(self.file_path)

        def traverse(node):
            if node.location.file:
                node_path = os.path.abspath(node.location.file.name)
                if node_path == target_path:
                    if node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                        name = node.spelling
                        if name:
                            counts[name] = counts.get(name, 0) + 1

            for child in node.get_children():
                traverse(child)

        traverse(self.tu.cursor)
        return counts

    def _get_const_count(self):
        """Counts occurrences of the 'const' keyword using tokens (user file only)."""
        count = 0
        target_path = os.path.abspath(self.file_path)

        for token in self.tu.get_tokens(extent=self.tu.cursor.extent):
            if token.location.file:
                token_path = os.path.abspath(token.location.file.name)
                if token_path == target_path:
                    if token.kind == clang.cindex.TokenKind.KEYWORD and token.spelling == 'const':
                        count += 1
        return count

    def _get_magic_constants_count(self):
        """Counts literal constants (numbers, characters, strings) in the AST (user file only)."""
        count = 0
        target_path = os.path.abspath(self.file_path)

        def traverse(node):
            nonlocal count
            if node.location.file:
                node_path = os.path.abspath(node.location.file.name)
                if node_path == target_path:
                    if node.kind in (
                        clang.cindex.CursorKind.INTEGER_LITERAL,
                        clang.cindex.CursorKind.FLOATING_LITERAL,
                        clang.cindex.CursorKind.CHARACTER_LITERAL,
                        clang.cindex.CursorKind.STRING_LITERAL
                    ):
                        count += 1

            for child in node.get_children():
                traverse(child)

        traverse(self.tu.cursor)
        return count