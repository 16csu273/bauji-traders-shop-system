# BAUJI TRADERS - Shop Management System v2.0

## 🏪 Complete Shop Management Solution

A professional-grade shop management system with barcode scanning, inventory management, customer database, and thermal receipt printing.

---

## 🚀 QUICK START

### 1. INSTALLATION
```
1. Double-click "INSTALL.bat"
2. Wait for installation to complete
3. Press any key when done
```

### 2. LAUNCH APPLICATION
```
1. Double-click "LAUNCH_SHOP.bat"
2. System will start automatically
```

---

## 📋 SYSTEM FEATURES

### 💳 Billing & Sales
- **Lightning-fast barcode scanning** - Auto-add products with quantity increment
- **Manual product selection** - Browse and add products with custom quantity
- **Editable shopping cart** - Double-click to edit quantity and price
- **Multiple payment methods** - Cash, Card, UPI support
- **Discount management** - Apply percentage discounts
- **Smart checkout** - Three options: Save & Print, Show Receipt, Cancel

### 📦 Inventory Management  
- **Complete product database** - Name, cost, MRP, stock, categories
- **Smart pricing** - Auto-calculate sell price with 40% profit margin
- **Stock tracking** - Real-time quantity updates
- **Category management** - Auto-categorization of products
- **Low stock alerts** - Monitor inventory levels

### 👥 Customer Management
- **Phone-based customer database** - Unique customer identification
- **Purchase history** - Track total purchases and visit frequency
- **Loyalty points** - Automatic point calculation
- **Customer profiles** - Name, phone, email, last visit

### 🏷️ Barcode Manager
- **Quick barcode assignment** - Click product → Scan → Done
- **Auto-advance** - Automatically select next product without barcode
- **Smart filtering** - Show all/with barcodes/without barcodes
- **Barcode validation** - Prevent duplicate assignments

### 📊 Reports & Analytics
- **Sales reports** - Daily, weekly, monthly summaries
- **Product analysis** - Best-selling items, stock movements
- **Customer insights** - Purchase patterns, loyalty tracking
- **Financial overview** - Revenue, profit, trends

### 🧾 Receipt Printing
- **Thermal printer support** - 3-inch (80mm) thermal receipts
- **Professional formatting** - 42-character width layout
- **Complete details** - Items, quantities, prices, totals, customer info
- **Direct printing** - No preview dialogs for fast checkout

### 📈 Transaction History
- **Complete audit trail** - All sales transactions logged
- **Search and filter** - Find transactions by date, customer, amount
- **Reprint receipts** - Access historical transaction details
- **Export capabilities** - CSV export for accounting

---

## 📁 FILE STRUCTURE

```
📁 BAUJI_TRADERS_ShopManagement_v2.0/
├── 🚀 INSTALL.bat                    # Installation script
├── 🏪 LAUNCH_SHOP.bat                # Application launcher
├── 📋 README.md                      # This file
├── 🎯 shop_gui.py                    # Main application
├── 📊 inventory_master.csv           # Product database
├── 🔧 sales_billing.py               # Sales module
├── 📦 stock_manager.py               # Inventory module  
├── 👥 customer_manager.py            # Customer module
├── 📈 reports_analytics.py           # Reports module
├── 🔄 restore_inventory_and_clear_transactions.py  # System reset
├── 👥 rebuild_customers.py           # Customer database rebuild
├── 📁 data/                          # Data directory
│   ├── customers.json                # Customer database
│   └── sales_transactions.csv        # Transaction history
└── 📁 backups/                       # Automatic backups
    ├── inventory_backup_*.csv
    ├── customers_backup_*.json
    └── transactions_backup_*.csv
```

---

## 🛠️ INSTALLATION REQUIREMENTS

### System Requirements
- **Operating System:** Windows 7/8/10/11
- **Python:** 3.7 or higher
- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 100MB free space
- **Display:** 1024x768 minimum resolution

### Dependencies (Auto-installed)
- `pandas` - Data manipulation and analysis
- `ttkthemes` - Enhanced GUI themes

---

## 🎯 USAGE GUIDE

### First Time Setup
1. Run `INSTALL.bat` - Sets up all dependencies
2. Ensure `inventory_master.csv` has your products
3. Run `LAUNCH_SHOP.bat` to start

### Daily Operations

#### Quick Barcode Sale
1. Open **Billing & Sales** tab
2. Scan barcode → Product automatically added
3. Scan same barcode → Quantity increases
4. Click **CHECKOUT** → Fill customer details
5. Click **Save & Print Receipt** → Done!

#### Manual Product Sale  
1. Browse products in left panel
2. Double-click product → Enter quantity
3. Product added to cart
4. Double-click cart items to edit if needed
5. Proceed with checkout

#### Barcode Assignment
1. Open **Barcode Manager** tab
2. Click product → Barcode field auto-focuses
3. Scan barcode → Automatically assigned
4. Auto-advances to next product

#### Customer Management
- Customers automatically saved during checkout
- View all customers in **Customer Management** tab
- Phone number is unique identifier
- Track purchase history and loyalty points

### System Maintenance

#### Daily Backups
- System automatically creates backups during operations
- Manual backup via **Settings** → **Backup Data**

#### System Reset (Testing/Development)
```bash
python restore_inventory_and_clear_transactions.py
```
- Restores inventory quantities
- Clears all transactions  
- Clears customer database
- Creates safety backups

#### Customer Database Rebuild
```bash
python rebuild_customers.py
```
- Rebuilds customer database from transaction history
- Useful for data recovery

---

## 🔧 TROUBLESHOOTING

### Common Issues

**"Python not found"**
- Install Python from https://www.python.org/downloads/
- Ensure "Add Python to PATH" is checked during installation
- Restart computer and try again

**"Module not found" errors**
- Run `INSTALL.bat` again
- Check internet connection for package downloads

**Barcode scanner not working**
- Ensure scanner is in keyboard emulation mode
- Test scanner in notepad first
- Check scanner manual for configuration

**Thermal printer issues**
- Verify printer is connected and powered on
- Install printer drivers
- Set as default printer in Windows
- Test with Notepad print

**Inventory not loading**
- Check `inventory_master.csv` exists
- Verify CSV format matches expected columns
- Ensure no special characters in file path

### Performance Optimization
- Keep inventory under 10,000 items for best performance
- Regular backup cleanup (monthly)
- Close unnecessary applications while running

---

## 📞 SUPPORT

### Self-Help Resources
1. Check this README for common solutions
2. Review error messages carefully
3. Test with sample data first

### File Issues
- Backup files located in `backups/` folder
- Transaction log in `data/sales_transactions.csv`
- Customer data in `data/customers.json`

### Data Recovery
- Use backup files from `backups/` folder
- Run `rebuild_customers.py` for customer data
- Restore inventory from backup CSV files

---

## 🔄 VERSION HISTORY

### v2.0 (Current)
- ✅ Integrated barcode manager
- ✅ Enhanced checkout with direct printing
- ✅ Editable shopping cart
- ✅ Phone-based customer management
- ✅ Smart barcode assignment workflow
- ✅ Comprehensive system restore
- ✅ Professional installation system

### Key Improvements
- 50% faster checkout process
- Unified interface for all operations
- Robust data handling and backups
- Professional deployment system

---

## 📜 LICENSE

© 2025 BAUJI TRADERS Shop Management System
Developed for internal business use.

---

**🎉 Thank you for choosing BAUJI TRADERS Shop Management System!**

*For the best experience, ensure your barcode scanner is configured for keyboard emulation and your thermal printer supports 80mm (3-inch) paper.*
