@echo off
echo [*] Startar Webapp Initialization...

REM -- 1. BEGÄR ADMINISTRATÖRSRÄTTIGHETER --
REM Kollar om vi har admin. Om inte, startar den om sig själv som Admin.
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [*] Begar administratorrattigheter for att kunna byta Node-version...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

REM När man kör som Admin startar Windows i fel mapp (System32). 
REM Denna rad tvingar skriptet att gå tillbaka till din Scrum-Proj mapp.
cd /d "%~dp0"

REM -- 2. KOLLA OM NVM FINNS --
nvm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] NVM hittades inte. Installerande NVM via winget...
    winget install -e --id CoreyButler.NVMforWindows --accept-source-agreements --accept-package-agreements
    echo [+] NVM installerat! Stang detta fonster och kor filen igen.
    pause
    exit /b
)

REM -- 3. GÅ IN I WEBSITE-MAPPEN --
if exist "..\website\" (
    echo [*] Navigerar till ./website...
    cd ..\website
) else (
    echo [!] FEL: Kunde inte hitta mappen 'website'. Ligger bat-filen bredvid mappen?
    pause
    exit /b
)

REM -- 4. AKTIVERA NODE OCH NPM --
echo [*] Konfigurerar Node.js (Version 22)...
call nvm install 22
call nvm use 22

REM -- 5. INSTALLERA OCH STARTA --
echo [*] Installerar dependencies (detta kan ta en liten stund)...
call npm install

echo [+] Startar utvecklingsservern...
echo --------------------------------------------------
call npm run dev

pause