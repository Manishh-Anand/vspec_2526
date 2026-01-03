@echo off
setlocal enabledelayedexpansion
color 0A

echo ============================================================
echo                    MetaFlow Pipeline
echo ============================================================
echo.

REM Get user prompt
if "%~1"=="" (
    set /p PROMPT="Enter your task: "
) else (
    set PROMPT=%~1
)

echo.
echo Task: !PROMPT!
echo Starting pipeline execution...
echo.

REM Navigate to project directory
cd /d D:\final_yr_project_2526\backend\v2.1\test_base_agent_4

REM Save prompt to file for processing
echo !PROMPT! > user_prompt.txt

REM Step 1: STAR Conversion (optional)
if exist system2starmethod.py (
    echo [1/5] STAR Conversion...
    python system2starmethod.py user_prompt.txt
    if !errorlevel! neq 0 (
        echo [ERROR] STAR conversion failed
        echo Check system2starmethod.py for issues
        pause
        exit /b 1
    )
    echo [1/5] Complete
) else (
    echo [1/5] STAR Conversion... SKIPPED (file not found)
)
echo.

REM Step 2: Workflow Generation
echo [2/5] Generating Workflow...
python base_agent_4.py
if !errorlevel! neq 0 (
    echo [ERROR] Workflow generation failed
    echo Check base_agent_4.py and LM Studio connection
    pause
    exit /b 1
)
if not exist BA_op.json (
    echo [ERROR] BA_op.json not created
    pause
    exit /b 1
)
echo [2/5] Complete - BA_op.json created
echo.

REM Step 3: Tool Mapping
echo [3/5] Mapping Tools...
python tool_mapper.py BA_op.json
if !errorlevel! neq 0 (
    echo [ERROR] Tool mapping failed
    echo Check tool_mapper.py
    pause
    exit /b 1
)
if not exist BA_enhanced.json (
    echo [ERROR] BA_enhanced.json not created
    pause
    exit /b 1
)
echo [3/5] Complete - BA_enhanced.json created
echo.

REM Step 4: Agent Creation (auto-detect version)
set FACTORY_FILE=

if exist langchain_agentfactory_functional.py goto :use_functional
if exist langchain_agentfactory_minimal.py goto :use_minimal
if exist langchain_agentfactory.py goto :use_standard
if exist langchain_agentfactory_original.py goto :use_original

goto :no_factory_found

:use_functional
set FACTORY_FILE=langchain_agentfactory_functional.py
echo [4/5] Creating Agents (Functional Version - Full Features)...
goto :run_factory

:use_minimal
set FACTORY_FILE=langchain_agentfactory_minimal.py
echo [4/5] Creating Agents (Minimal Version - Token Sentinel/Pruning/QC)...
goto :run_factory

:use_standard
set FACTORY_FILE=langchain_agentfactory.py
echo [4/5] Creating Agents (Standard Version)...
goto :run_factory

:use_original
set FACTORY_FILE=langchain_agentfactory_original.py
echo [4/5] Creating Agents (Original Version)...
goto :run_factory

:no_factory_found
echo [ERROR] No agent factory file found
echo Expected one of: langchain_agentfactory_functional.py, langchain_agentfactory_minimal.py, langchain_agentfactory.py
pause
exit /b 1

:run_factory
python !FACTORY_FILE! BA_enhanced.json
if !errorlevel! neq 0 (
    echo [ERROR] Agent creation failed
    echo Check !FACTORY_FILE!
    pause
    exit /b 1
)
echo [4/5] Complete - Agents created
echo.

REM Step 5: Workflow Execution
echo [5/5] Executing Workflow...
python langgraph_workflow_builder.py BA_enhanced.json
if !errorlevel! neq 0 (
    echo [ERROR] Workflow execution failed
    echo Check langgraph_workflow_builder.py and agent logs
    pause
    exit /b 1
)
echo [5/5] Complete - Workflow executed
echo.

echo ============================================================
echo                  Pipeline Complete!
echo ============================================================
echo.
echo Results saved to workflow_result_[timestamp].json
echo Check outputs folder for generated files
echo.
echo To view metrics: python aggregate_results.py
echo.
if "%NO_PAUSE%"=="" pause
