@echo off
setlocal enabledelayedexpansion

set NO_PAUSE=1
set PROMPT="Create a Python script to scrape a website and save to CSV"

echo ===================================================
echo COMPARISON TEST: Minimal vs Functional
echo ===================================================
echo.

REM ----------------------------------------------------
REM RUN 1: MINIMAL VERSION
REM ----------------------------------------------------
echo [TEST] Running MINIMAL Version (Thesis Demo)...
echo.

REM Hide functional version to force minimal
if exist langchain_agentfactory_functional.py (
    ren langchain_agentfactory_functional.py langchain_agentfactory_functional.py.bak
)

call run_metaflow.bat %PROMPT%

REM Restore functional version immediately
if exist langchain_agentfactory_functional.py.bak (
    ren langchain_agentfactory_functional.py.bak langchain_agentfactory_functional.py
)

REM Find and rename result
for /f "delims=" %%x in ('dir /b /o-d workflow_result_*.json') do (
    set "LATEST=%%x"
    goto :found_minimal
)
:found_minimal
copy "%LATEST%" result_minimal.json >nul
echo [SAVE] Saved result to result_minimal.json
echo.

REM ----------------------------------------------------
REM RUN 2: FUNCTIONAL VERSION
REM ----------------------------------------------------
echo [TEST] Running FUNCTIONAL Version (Production)...
echo.

REM Ensure functional version is present (already restored)
call run_metaflow.bat %PROMPT%

REM Find and rename result
for /f "delims=" %%x in ('dir /b /o-d workflow_result_*.json') do (
    set "LATEST=%%x"
    goto :found_functional
)
:found_functional
copy "%LATEST%" result_functional.json >nul
echo [SAVE] Saved result to result_functional.json
echo.

REM ----------------------------------------------------
REM COMPARISON
REM ----------------------------------------------------
echo ===================================================
echo RESULTS COMPARISON
echo ===================================================
echo.

python -c "import json; m=json.load(open('result_minimal.json')); f=json.load(open('result_functional.json')); print(f'METRIC                 MINIMAL      FUNCTIONAL'); print(f'----------------------------------------------'); print(f'Duration (s)           {m.get(\"duration_seconds\", 0):<12.2f} {f.get(\"duration_seconds\", 0):.2f}'); print(f'Agents Executed        {m.get(\"agents_executed\", 0):<12} {f.get(\"agents_executed\", 0)}'); print(f'Success Rate           {m.get(\"agents_succeeded\", 0)}/{m.get(\"agents_executed\", 0)}        {f.get(\"agents_succeeded\", 0)}/{f.get(\"agents_executed\", 0)}');"

echo.
echo Done.
pause
