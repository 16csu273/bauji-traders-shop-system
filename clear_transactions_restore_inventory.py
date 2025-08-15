"""
🔄 CLEAR TRANSACTIONS & RESTORE INVENTORY
========================================
This script clears all sales transactions and restores the sold products back to inventory.

WARNING: This operation cannot be undone!
- All sales transactions will be deleted
- Products will be added back to inventory based on sales data
- Customer data and purchase history will be preserved
"""

import pandas as pd
import os
import json
from datetime import datetime
import shutil

def backup_data():
    """Create backup of current data before clearing"""
    print("📦 Creating backup of current data...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"backup_before_clear_{timestamp}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup files
        files_to_backup = [
            'data/sales_transactions.csv',
            'inventory_master.csv',
            'data/customers.json',
            'data/stock_movements.csv'
        ]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_dir)
                print(f"  ✓ Backed up: {file_path}")
        
        print(f"✅ Backup created: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def load_data():
    """Load current inventory and sales data"""
    print("📊 Loading current data...")
    
    try:
        # Load inventory
        if not os.path.exists('inventory_master.csv'):
            print("❌ Inventory file not found!")
            return None, None
        
        inventory_df = pd.read_csv('inventory_master.csv')
        print(f"  ✓ Loaded inventory: {len(inventory_df)} products")
        
        # Load sales
        sales_file = 'data/sales_transactions.csv'
        if not os.path.exists(sales_file):
            print("❌ No sales transactions found!")
            return inventory_df, None
        
        sales_df = pd.read_csv(sales_file)
        print(f"  ✓ Loaded sales: {len(sales_df)} transactions")
        
        return inventory_df, sales_df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, None

def calculate_restoration_summary(sales_df):
    """Calculate what will be restored to inventory"""
    print("\n📋 Calculating restoration summary...")
    
    try:
        # Group sales by product
        product_summary = sales_df.groupby('Product_Name').agg({
            'Quantity_Sold': 'sum',
            'Final_Amount': 'sum',
            'Transaction_ID': 'nunique'
        }).round(2)
        
        total_transactions = len(sales_df['Transaction_ID'].unique())
        total_revenue = sales_df['Final_Amount'].sum()
        total_items_sold = sales_df['Quantity_Sold'].sum()
        
        print(f"\n📈 RESTORATION SUMMARY:")
        print(f"  Total Transactions: {total_transactions:,}")
        print(f"  Total Revenue: ₹{total_revenue:,.2f}")
        print(f"  Total Items Sold: {total_items_sold:,}")
        print(f"  Unique Products: {len(product_summary):,}")
        
        print(f"\n🔝 TOP 10 PRODUCTS TO RESTORE:")
        top_products = product_summary.sort_values('Quantity_Sold', ascending=False).head(10)
        for product, data in top_products.iterrows():
            print(f"  {product[:40]:40} | Qty: {data['Quantity_Sold']:4.0f} | Revenue: ₹{data['Final_Amount']:8,.0f}")
        
        return product_summary
        
    except Exception as e:
        print(f"❌ Error calculating summary: {e}")
        return None

def restore_inventory(inventory_df, sales_df):
    """Restore sold products back to inventory"""
    print("\n🔄 Restoring products to inventory...")
    
    try:
        # Calculate total quantities sold per product
        sold_quantities = sales_df.groupby('Product_Name')['Quantity_Sold'].sum()
        
        restored_count = 0
        not_found_products = []
        
        for product_name, total_sold in sold_quantities.items():
            # Find product in inventory
            product_idx = inventory_df[inventory_df['Product_Name'] == product_name].index
            
            if len(product_idx) > 0:
                # Product found - restore quantity
                current_qty = inventory_df.loc[product_idx[0], 'Quantity']
                new_qty = current_qty + total_sold
                inventory_df.loc[product_idx[0], 'Quantity'] = new_qty
                
                print(f"  ✓ {product_name[:35]:35} | {current_qty:4.0f} → {new_qty:4.0f} (+{total_sold:3.0f})")
                restored_count += 1
            else:
                # Product not found in current inventory
                not_found_products.append((product_name, total_sold))
        
        print(f"\n✅ Restored {restored_count} products to inventory")
        
        if not_found_products:
            print(f"\n⚠️  Products not found in current inventory ({len(not_found_products)}):")
            for product_name, qty in not_found_products[:5]:  # Show first 5
                print(f"  - {product_name} (Qty: {qty})")
            if len(not_found_products) > 5:
                print(f"  ... and {len(not_found_products) - 5} more")
        
        return inventory_df, restored_count
        
    except Exception as e:
        print(f"❌ Error restoring inventory: {e}")
        return inventory_df, 0

def clear_sales_transactions():
    """Clear all sales transactions"""
    print("\n🗑️  Clearing sales transactions...")
    
    try:
        sales_file = 'data/sales_transactions.csv'
        
        # Create empty sales file with headers
        empty_sales = pd.DataFrame(columns=[
            'Transaction_ID', 'Date', 'Time', 'Customer_Name', 'Customer_Phone',
            'Product_Name', 'Quantity_Sold', 'Unit_Price', 'Total_Amount', 
            'Payment_Method', 'Discount', 'Final_Amount'
        ])
        
        empty_sales.to_csv(sales_file, index=False)
        print("  ✓ Sales transactions cleared")
        
        # Clear stock movements related to sales
        stock_movements_file = 'data/stock_movements.csv'
        if os.path.exists(stock_movements_file):
            movements_df = pd.read_csv(stock_movements_file)
            # Keep only non-sale movements (purchases, adjustments, etc.)
            non_sale_movements = movements_df[~movements_df['Movement_Type'].isin(['SALE', 'QUICK_SALE'])]
            non_sale_movements.to_csv(stock_movements_file, index=False)
            print("  ✓ Sale-related stock movements cleared")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing transactions: {e}")
        return False

def save_restoration_report(product_summary, backup_dir, restored_count):
    """Save detailed restoration report"""
    try:
        report_file = f"{backup_dir}/restoration_report.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("🔄 INVENTORY RESTORATION REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Products Restored: {restored_count}\n")
            f.write(f"Total Transactions Cleared: {len(product_summary)}\n\n")
            
            f.write("DETAILED RESTORATION:\n")
            f.write("-" * 50 + "\n")
            for product, data in product_summary.iterrows():
                f.write(f"{product:40} | Qty: {data['Quantity_Sold']:4.0f} | Revenue: ₹{data['Final_Amount']:8,.0f}\n")
        
        print(f"  ✓ Restoration report saved: {report_file}")
        
    except Exception as e:
        print(f"⚠️  Could not save report: {e}")

def main():
    """Main function to clear transactions and restore inventory"""
    print("🔄 CLEAR TRANSACTIONS & RESTORE INVENTORY")
    print("=" * 50)
    print("⚠️  WARNING: This operation cannot be undone!")
    print("   - All sales transactions will be deleted")
    print("   - Products will be restored to inventory")
    print("   - Customer data will be preserved")
    
    # Confirmation
    confirm = input("\n❓ Are you sure you want to continue? (type 'YES' to confirm): ").strip()
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return
    
    # Step 1: Create backup
    backup_dir = backup_data()
    if not backup_dir:
        print("❌ Cannot proceed without backup")
        return
    
    # Step 2: Load data
    inventory_df, sales_df = load_data()
    if inventory_df is None or sales_df is None:
        print("❌ Cannot load required data files")
        return
    
    if len(sales_df) == 0:
        print("ℹ️  No sales transactions to clear")
        return
    
    # Step 3: Show restoration summary
    product_summary = calculate_restoration_summary(sales_df)
    if product_summary is None:
        return
    
    # Final confirmation
    final_confirm = input(f"\n❓ Restore {len(product_summary)} products and clear {len(sales_df)} transactions? (type 'CONFIRM'): ").strip()
    if final_confirm != 'CONFIRM':
        print("❌ Operation cancelled")
        return
    
    print("\n🚀 Starting restoration process...")
    
    # Step 4: Restore inventory
    inventory_df, restored_count = restore_inventory(inventory_df, sales_df)
    
    # Step 5: Save updated inventory
    try:
        inventory_df.to_csv('inventory_master.csv', index=False)
        print("  ✓ Updated inventory saved")
    except Exception as e:
        print(f"❌ Error saving inventory: {e}")
        return
    
    # Step 6: Clear transactions
    if not clear_sales_transactions():
        print("❌ Error clearing transactions")
        return
    
    # Step 7: Save report
    save_restoration_report(product_summary, backup_dir, restored_count)
    
    # Final summary
    print("\n" + "=" * 50)
    print("✅ RESTORATION COMPLETED SUCCESSFULLY!")
    print(f"📦 Backup created: {backup_dir}")
    print(f"🔄 Products restored: {restored_count}")
    print(f"🗑️  Transactions cleared: {len(sales_df)}")
    print("=" * 50)
    print("\n💡 Tip: You can find backup files and restoration report in the backup folder")

if __name__ == "__main__":
    main()
