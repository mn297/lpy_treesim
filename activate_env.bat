@echo off
REM Activate .venv in the same folder as this script (Conda or Python venv).
REM Use: call activate_env.bat   (or call path\to\digital_orchard\activate_env.bat)
REM Works on Windows (cmd).

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"

if exist "%ROOT%\.venv\conda-meta" (
    call conda activate "%ROOT%\.venv"
    goto :done
)
if exist "%ROOT%\.venv\Scripts\activate.bat" (
    call "%ROOT%\.venv\Scripts\activate.bat"
    goto :done
)

echo activate_env: no .venv found at %ROOT%\.venv
exit /b 1

:done
