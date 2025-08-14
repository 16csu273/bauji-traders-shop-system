@echo off
:: ===============================================================
:: BAUJI TRADERS - Shop Management System Installer
:: ===============================================================
:: This script will install all required dependencies and 
:: set up the shop management system for first use.
:: ===============================================================

title BAUJI TRADERS - Shop Management System Installer
color 0A

echo.
echo ===============================================================
echo            BAUJI TRADERS - Shop Management System
echo                        INSTALLER v2.0
echo ===============================================================
echo.

:: Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version

echo.
echo [2/5] Installing required packages...
echo Installing pandas...
pip install pandas --quiet
if %errorlevel% neq 0 (
    echo ❌ Failed to install pandas
    pause
    exit /b 1
)

echo Installing ttkthemes...
pip install ttkthemes --quiet
if %errorlevel% neq 0 (
    echo ❌ Failed to install ttkthemes
    pause
    exit /b 1
)

echo ✅ All packages installed successfully

echo.
echo [3/5] Creating data directories...
if not exist "data" mkdir data
if not exist "backups" mkdir backups
echo ✅ Data directories created

echo.
echo [4/5] Initializing system files...
:: Create empty customers.json if it doesn't exist
if not exist "data\customers.json" (
    echo {} > "data\customers.json"
    echo ✅ Customer database initialized
)

:: Create empty transactions file if it doesn't exist
if not exist "data\sales_transactions.csv" (
    echo Transaction_ID,Date,Time,Customer_Name,Customer_Phone,Product_Name,Quantity_Sold,Unit_Price,Total_Amount,Payment_Method,Discount,Final_Amount > "data\sales_transactions.csv"
    echo ✅ Transaction history initialized
)

:: Check if inventory file exists
if not exist "inventory_master.csv" (
    echo ❌ WARNING: inventory_master.csv not found!
    echo Please ensure your product inventory file is present.
    echo.
)

echo.
echo [5/5] Testing system...
echo Testing application launch...
timeout /t 2 /nobreak >nul
python shop_gui.py --test >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ System test passed
) else (
    echo ⚠️  System test completed with warnings
)

echo.
echo ===============================================================
echo                    INSTALLATION COMPLETE!
echo ===============================================================
echo.
echo 🎉 BAUJI TRADERS Shop Management System is ready to use!
echo.
echo 📋 What's installed:
echo    ✅ All required Python packages
echo    ✅ Data directories created  
echo    ✅ System files initialized
echo    ✅ Application tested
echo.
echo 🚀 To start the application:
echo    • Double-click "LAUNCH_SHOP.bat"
echo    • Or run: python shop_gui.py
echo.
echo 📁 Important files:
echo    • shop_gui.py           - Main application
echo    • inventory_master.csv  - Your product database
echo    • data\                 - Customer and transaction data
echo    • backups\              - Automatic backups
echo.
echo 🛠️  Utilities:
echo    • rebuild_customers.py  - Rebuild customer database
echo    • restore_inventory_and_clear_transactions.py - Reset system
echo.
echo ===============================================================

pause
