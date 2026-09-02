@echo off
echo ========================================
echo   Reed Mod - Deploy to Game
echo ========================================
echo.

set "GAME_DIR=E:\SteamLibrary\steamapps\common\Slay the Spire 2"
set "MODS_DIR=%GAME_DIR%\mods"
set "REED_DIR=%MODS_DIR%\Reed"
set "RITSU_DIR=%MODS_DIR%\STS2-RitsuLib"
set "SCRIPT_DIR=%~dp0"

echo Game: %GAME_DIR%
echo.

:: Create dirs
if not exist "%REED_DIR%" mkdir "%REED_DIR%"
if not exist "%RITSU_DIR%" mkdir "%RITSU_DIR%"

:: Clean old Reed files
echo Cleaning old Reed mod files...
del /q "%REED_DIR%\*.*" 2>nul

:: Copy Reed files
echo Copying Reed.dll...
copy /y "%SCRIPT_DIR%.godot\mono\temp\bin\Release\Reed.dll" "%REED_DIR%\Reed.dll"

echo Copying Reed.json...
copy /y "%SCRIPT_DIR%Reed.json" "%REED_DIR%\Reed.json"

echo Copying Reed.pck...
copy /y "%SCRIPT_DIR%Reed.pck" "%REED_DIR%\Reed.pck"

:: Copy RitsuLib
echo.
echo Copying RitsuLib...
set "RITSU_NUGET=C:\Users\Administrator\.nuget\packages\sts2.ritsulib\0.5.18"
copy /y "%RITSU_NUGET%\lib\net9.0\STS2-RitsuLib.dll" "%RITSU_DIR%\STS2-RitsuLib.dll"
copy /y "%RITSU_NUGET%\contentFiles\any\any\mod_manifest.json" "%RITSU_DIR%\STS2-RitsuLib.json"

echo.
echo ========================================
echo   Deploy Complete!
echo ========================================
echo.
echo Files deployed to:
echo   %REED_DIR%\Reed.dll
echo   %REED_DIR%\Reed.json
echo   %REED_DIR%\Reed.pck
echo   %RITSU_DIR%\STS2-RitsuLib.dll
echo   %RITSU_DIR%\STS2-RitsuLib.json
echo.
echo Launch the game to load the mod.
pause
