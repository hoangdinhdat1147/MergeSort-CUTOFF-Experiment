@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if not exist datasets mkdir datasets
echo [1/3] Tao bo du lieu...
python scripts\generate_data.py
if errorlevel 1 goto error
echo [2/3] Bien dich Java...
if not exist out mkdir out
javac -encoding UTF-8 -d out src\MergeSort.java src\Experiment.java
if errorlevel 1 goto error
echo [3/3] Chay thi nghiem...
java -cp out Experiment datasets results.csv
if errorlevel 1 goto error
echo Hoan tat. Dang tong hop va ve bieu do...
python scripts\analyze_results.py
if errorlevel 1 goto error
echo.
echo XONG! Mo results.csv va thu muc analysis de xem ket qua.
pause
exit /b 0
:error
echo Co loi. Hay kiem tra da cai JDK va Python, sau do doc README.md.
pause
exit /b 1
