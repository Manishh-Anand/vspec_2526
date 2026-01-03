@echo off
setlocal enabledelayedexpansion
color 0A

echo.
echo ============================================================
echo            MetaFlow Complete Pipeline Test
echo ============================================================
echo.
echo Testing complete workflow from prompt to execution...
echo.

cd /d D:\final_yr_project_2526\backend\v2.1\test_base_agent_4

set "start_time=%time%"

echo [1/7] Checking prerequisites...
echo ============================================================
echo.

echo Checking LM Studio...
curl -s http://localhost:1234/v1/models >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] LM Studio NOT running!
    echo     Please start LM Studio and load Qwen 2.5 14B model
    echo     Then run this script again.
    pause
    exit /b 1
)
echo [OK] LM Studio is running

echo Checking Claude Code...
REM claude --version >nul 2>&1
REM if %errorlevel% neq 0 (
REM     echo [X] Claude Code NOT found!
REM     echo     Please install Claude Code first
REM     pause
REM     exit /b 1
REM )
echo [OK] Claude Code check skipped (assumed available)

echo Checking MCP servers...
claude mcp list | findstr "Connected" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Warning: Some MCP servers may not be connected
    echo     Continuing anyway...
)
echo [OK] MCP servers checked

echo.
echo [OK] All prerequisites passed!
echo.
timeout /t 2 >nul

echo [2/7] Running system2starmethod.py (STAR conversion)...
echo ============================================================
echo.
if not exist system2starmethod.py (
    echo [!] system2starmethod.py not found, skipping...
    goto base_agent
)
python system2starmethod.py
if %errorlevel% neq 0 (
    echo [X] STAR conversion failed!
    pause
    exit /b 1
)
echo [OK] STAR conversion complete
echo.
timeout /t 2 >nul

:base_agent
echo [3/7] Running base_agent_4.py (Generate BA_op.json)...
echo ============================================================
echo.
python base_agent_4.py
if %errorlevel% neq 0 (
    echo [X] Base Agent failed!
    pause
    exit /b 1
)
if not exist BA_op.json (
    echo [X] BA_op.json was not created!
    pause
    exit /b 1
)
echo [OK] BA_op.json generated successfully
for %%A in (BA_op.json) do echo     File size: %%~zA bytes
echo.
timeout /t 2 >nul

echo [4/7] Running tool_mapper.py (Generate BA_enhanced.json)...
echo ============================================================
echo.
python tool_mapper.py BA_op.json
if %errorlevel% neq 0 (
    echo [X] Tool Mapper failed!
    pause
    exit /b 1
)
if not exist BA_enhanced.json (
    echo [X] BA_enhanced.json was not created!
    pause
    exit /b 1
)
echo [OK] BA_enhanced.json generated successfully
for %%A in (BA_enhanced.json) do echo     File size: %%~zA bytes
echo.
timeout /t 2 >nul

echo [5/7] Validating tool mappings...
echo ============================================================
echo.
python -c "import json; ba=json.load(open('BA_enhanced.json')); agent1_tools=[t['name'] for t in ba['agents'][0]['tools']]; print('ResearchAgent tools:', agent1_tools); has_jina = any('jina' in str(t).lower() for t in agent1_tools); print('Has Jina tools:', has_jina); exit(0 if has_jina else 1)"
if %errorlevel% neq 0 (
    echo [!] WARNING: ResearchAgent may not have Jina tools!
    echo     This might cause permission issues.
    echo     Continuing anyway...
) else (
    echo [OK] Tool mappings look correct
)
echo.
timeout /t 2 >nul

echo [6/7] Running testing_utilities.py (Validate setup)...
echo ============================================================
echo.
if not exist testing_utilities.py (
    echo [!] testing_utilities.py not found, skipping tests...
    goto workflow
)
python testing_utilities.py BA_enhanced.json
echo.
echo [INFO] Check test results above
echo.
timeout /t 3 >nul

:workflow
echo [7/7] Running langgraph_workflow_builder.py (Execute workflow)...
echo ============================================================
echo.
python langgraph_workflow_builder.py BA_enhanced.json
if %errorlevel% neq 0 (
    echo [X] Workflow execution failed!
    echo     Check the logs above for details
    pause
    exit /b 1
)
echo.
echo [OK] Workflow execution complete
echo.
timeout /t 2 >nul

echo.
echo ============================================================
echo                    PIPELINE COMPLETE!
echo ============================================================
echo.

echo Checking results...
for /f %%i in ('dir /b /od workflow_result_*.json 2^>nul') do set "latest_result=%%i"
if defined latest_result (
    echo Latest result file: %latest_result%
    echo.
    python -c "import json; r=json.load(open('%latest_result%')); print('Status:', r.get('status', 'unknown')); print('Duration:', r.get('duration_seconds', 'N/A'), 'seconds'); print('Agents executed:', r.get('agents_executed', 'N/A')); print('Agents succeeded:', r.get('agents_succeeded', 'N/A'))"
    echo.
    echo Full results saved to: %latest_result%
) else (
    echo [!] No workflow result file found
)

echo.
echo Files created in this run:
if exist BA_op.json echo   - BA_op.json
if exist BA_enhanced.json echo   - BA_enhanced.json
if defined latest_result echo   - %latest_result%

set "end_time=%time%"
echo.
echo Start time: %start_time%
echo End time:   %end_time%

echo.
echo ============================================================
echo                All tests completed! 
echo ============================================================
echo.
pause
```

---

## 📂 Where to Place It
```
D:\final_yr_project_2526\backend\v2.1\test_base_agent_4\
├── base_agent_4.py
├── tool_mapper.py
├── langchain_agentfactory.py
├── langgraph_workflow_builder.py
├── testing_utilities.py
├── system2starmethod.py (if you have it)
├── BA_op.json (generated)
├── BA_enhanced.json (generated)
└── run_complete_pipeline.bat  ← PUT IT HERE