@echo off
rem Chay toan bo quy trinh tren Windows:
rem   sinh du lieu -> kiem tra SHA-256 -> bien dich -> kiem thu -> benchmark -> phan tich
rem
rem   run_experiment.bat          cau hinh day du (3 warm-up, 11 lan do)
rem                               -> ghi results.csv va analysis\ (results.csv cu duoc sao luu)
rem   run_experiment.bat --quick  chay nhanh de thu (0 warm-up, 1 lan do)
rem                               -> ghi vao out\quick\, KHONG dung toi results.csv va analysis\
rem
rem Dat NO_PAUSE=1 de bo qua lenh pause o cuoi (huu ich khi chay tu dong).
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "QUICK=0"
if /i "%~1"=="--quick" set "QUICK=1"

where javac >nul 2>nul
if errorlevel 1 (
    echo Khong tim thay javac. Hay cai JDK 11 tro len va them vao PATH.
    goto error
)
where java >nul 2>nul
if errorlevel 1 (
    echo Khong tim thay java. Hay cai JDK 11 tro len va them vao PATH.
    goto error
)
set "PY=python"
where python >nul 2>nul
if errorlevel 1 set "PY=py -3"

echo [1/6] Sinh va kiem tra bo du lieu...
%PY% scripts\generate_data.py >nul
if errorlevel 1 goto error
%PY% scripts\generate_data.py --verify
if errorlevel 1 goto error

echo [2/6] Bien dich Java...
if not exist out mkdir out
javac -encoding UTF-8 -d out src\MergeSort.java src\Experiment.java test\MergeSortTest.java
if errorlevel 1 goto error

echo [3/6] Chay kiem thu...
java -cp out MergeSortTest
if errorlevel 1 goto error

if "%QUICK%"=="1" goto quick

if exist results.csv (
    copy /y results.csv results_old_backup.csv >nul
    echo       Da sao luu results.csv hien tai sang results_old_backup.csv
)

echo [4/6] Chay benchmark day du (mat vai phut)...
java -cp out Experiment datasets results.csv
if errorlevel 1 goto error

echo [5/6] Phan tich ket qua, ve bieu do, dong bo du lieu dashboard...
%PY% scripts\analyze_results.py --sync-docs
if errorlevel 1 goto error

echo [6/6] XONG! Mo results.csv va thu muc analysis de xem ket qua.
goto done

:quick
echo [4/6] Chay benchmark nhanh (0 warm-up, 1 lan do)...
java -cp out Experiment datasets out\quick\results.csv --warmups 0 --repeats 1
if errorlevel 1 goto error
echo [5/6] Phan tich ket qua nhanh...
%PY% scripts\analyze_results.py --input out\quick\results.csv --out out\quick\analysis --no-plots
if errorlevel 1 goto error
echo [6/6] Xong. Ket qua thu nam trong out\quick\ (khong anh huong results.csv).

:done
if not defined NO_PAUSE pause
exit /b 0

:error
echo.
echo Co loi. Hay kiem tra da cai JDK va Python (va "python -m pip install -r requirements.txt"), sau do doc README.md.
if not defined NO_PAUSE pause
exit /b 1
