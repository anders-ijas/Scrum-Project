@echo off
echo [*] Startar upp systemet...

call start-webpage.bat
echo [+] Webpage started

REM 1. Kolla om venv finns, annars skapa den
if not exist venv\Scripts\activate (
    echo [+] Hittade ingen venv. Skapar en ny virtuell miljö...
    python -m venv venv
)

REM 2. Aktivera venv
echo [*] Aktiverar venv...
call venv\Scripts\activate

REM 3. Installera dependencies
if exist requirements.txt (
    echo [*] Letar efter uppdateringar for dependencies...
    pip install -r requirements.txt --quiet
) else (
    echo [!] Ingen requirements.txt hittades. Hoppar over installation.
)

REM 4. Starta programmet
echo [+] Startar main_controller.py...
echo --------------------------------------------------
python MainLoop.py

REM Pausar rutan om programmet kraschar sa du kan lasa felmeddelandet
pause