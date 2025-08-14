@echo off
:: ===============================================================
:: BAUJI TRADERS - Shop Management System Launcher
:: ===============================================================
:: This script launches the shop management system with proper
:: error handling and system checks.
:: ===============================================================

title BAUJI TRADERS - Shop Management System
color 0B

:: Get current directory
set SHOP_DIR=%~dp0
cd /d "%SHOP_DIR%"

echo.
echo ===============================================================
echo            BAUJI TRADERS - Shop Management System
echo                          Starting...
echo ===============================================================
echo.

:: Quick system check
echo [✓] Checking system...

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found!
    echo.
    echo Please run INSTALL.bat first to set up the system.
    echo.
    pause
    exit /b 1
)

:: Check if main application exists
if not exist "shop_gui.py" (
    echo ❌ ERROR: shop_gui.py not found!
    echo.
    echo Please ensure all application files are present.
    echo.
    pause
    exit /b 1
)

:: Check if inventory file exists
if not exist "inventory_master.csv" (
    echo ❌ WARNING: inventory_master.csv not found!
    echo.
    echo The application will start but you won't have any products.
    echo Please add your inventory file and restart.
    echo.
    echo Press any key to continue anyway...
    pause
)

echo [✓] System check completed
echo.
echo 🚀 Starting BAUJI TRADERS Shop Management System...
echo.

:: Launch the application
python shop_gui.py

:: Check exit code
if %errorlevel% neq 0 (
    echo.
    echo ===============================================================
    echo ❌ Application exited with errors
    echo ===============================================================
    echo.
    echo If you encounter issues:
    echo 1. Run INSTALL.bat to reinstall dependencies
    echo 2. Check that all files are present
    echo 3. Ensure inventory_master.csv has proper format
    echo.
    echo For support, check the log files in the application.
    echo.
) else (
    echo.
    echo ===============================================================
    echo ✅ Application closed normally
    echo ===============================================================
    echo.
    echo Thank you for using BAUJI TRADERS Shop Management System!
    echo.
)

echo Press any key to exit...
pause >nul
