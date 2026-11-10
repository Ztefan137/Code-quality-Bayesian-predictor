@echo off
SETLOCAL

if "%~1"=="train" (
    if "%~2"=="" (
        python src\main.py --mode train
    ) else (
        python src\main.py --mode train --network-type "%~2"
    )
) else if "%~1"=="test" (
    if "%~2"=="" (
        python src\main.py --mode test
    ) else (
        python src\main.py --mode test --network-type "%~2"
    )
) else if "%~1"=="predict" (
    if "%~2"=="" (
        echo Error: --predict mode requires a file path.
        echo Example: run.bat predict data\source_files\sample_01.cpp
    ) else (
        if "%~3"=="" (
            python src\main.py --mode predict --file "%~2"
        ) else (
            python src\main.py --mode predict --file "%~2" --network-type "%~3"
        )
    )
) else (
    echo C++ Code Cleanliness Classifier
    echo ----------------------------------------
    echo Usage:
    echo   run.bat train [naive^|normal]
    echo   run.bat test [naive^|normal]
    echo   run.bat predict "path_to_cpp_file" [naive^|normal]
    echo ----------------------------------------
)