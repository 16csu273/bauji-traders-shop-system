#!/usr/bin/env python3
"""
Restore Inventory and Clear Transactions Script
===============================================

This script will:
1. Read all sales transactions from the test period
2. Calculate total quantities sold for each product
3. Restore those quantities back to the inventory
4. Clear the transaction history file
5. Clear customer database (test customers)
6. Update the inventory CSV file with restored quantities

Usage: python restore_inventory_and_clear_transactions.py
"""

import pandas as pd
import os
from datetime import datetime

def main():
    # File paths
    transactions_file = 'data/sales_transactions.csv'
    customers_file = 'data/customers.json'
    inventory_file = 'inventory_master.csv'
    backup_transactions_file = f'backups/transactions_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    backup_customers_file = f'backups/customers_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    print("🔄 Starting inventory restoration and transaction cleanup...")
    print("=" * 60)
    
    # Step 1: Read current transactions
    try:
        transactions_df = pd.read_csv(transactions_file)
        print(f"📊 Found {len(transactions_df)} transaction records to process")
        
        # Display transaction summary
        if not transactions_df.empty:
            print("\n📋 Transaction Summary:")
            print("-" * 40)
            product_sales = transactions_df.groupby('Product_Name')['Quantity_Sold'].sum().sort_values(ascending=False)
            for product, qty in product_sales.items():
                print(f"  • {product}: {qty} units sold")
        
    except FileNotFoundError:
        print("⚠️  No transactions file found. Nothing to restore.")
        return
    except Exception as e:
        print(f"❌ Error reading transactions: {e}")
        return
    
    # Step 2: Read current inventory
    try:
        inventory_df = pd.read_csv(inventory_file, dtype={'Barcode': str})
        
        # Clean up barcodes - ensure they're strings and remove any .0 suffixes
        if 'Barcode' in inventory_df.columns:
            inventory_df['Barcode'] = inventory_df['Barcode'].fillna('')
            # Remove .0 from barcodes that were stored as floats
            inventory_df['Barcode'] = inventory_df['Barcode'].astype(str).str.replace(r'\.0$', '', regex=True)
            # Replace 'nan' with empty string
            inventory_df['Barcode'] = inventory_df['Barcode'].replace('nan', '')
        
        print(f"\n📦 Loaded inventory with {len(inventory_df)} products")
        
    except FileNotFoundError:
        print("❌ Inventory file not found!")
        return
    except Exception as e:
        print(f"❌ Error reading inventory: {e}")
        return
    
    # Step 3: Create backup of transactions before clearing
    if not transactions_df.empty:
        try:
            os.makedirs('backups', exist_ok=True)
            transactions_df.to_csv(backup_transactions_file, index=False)
            print(f"💾 Transaction backup created: {backup_transactions_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
    
    # Step 3.5: Create backup of customers before clearing
    try:
        if os.path.exists(customers_file):
            import json
            with open(customers_file, 'r') as f:
                customers_data = json.load(f)
            
            if customers_data:  # Only backup if there's customer data
                os.makedirs('backups', exist_ok=True)
                with open(backup_customers_file, 'w') as f:
                    json.dump(customers_data, f, indent=2)
                print(f"💾 Customer backup created: {backup_customers_file}")
                print(f"📊 Backed up {len(customers_data)} customers")
            else:
                print("📊 No customer data to backup")
        else:
            print("📊 No customer file found to backup")
    except Exception as e:
        print(f"⚠️  Warning: Could not backup customers: {e}")
    
    # Step 4: Calculate quantities to restore
    restoration_summary = {}
    if not transactions_df.empty:
        print("\n🔧 Restoring inventory quantities...")
        print("-" * 40)
        
        # Group transactions by product and sum quantities
        product_sales = transactions_df.groupby('Product_Name')['Quantity_Sold'].sum()
        
        for product_name, total_sold in product_sales.items():
            # Find the product in inventory
            product_mask = inventory_df['Product_Name'] == product_name
            
            if product_mask.any():
                # Get current quantity
                current_qty = inventory_df.loc[product_mask, 'Quantity'].iloc[0]
                
                # Calculate restored quantity
                restored_qty = current_qty + total_sold
                
                # Update inventory
                inventory_df.loc[product_mask, 'Quantity'] = restored_qty
                
                restoration_summary[product_name] = {
                    'sold': total_sold,
                    'current': current_qty,
                    'restored': restored_qty
                }
                
                print(f"  ✅ {product_name}")
                print(f"     Current: {current_qty} → Restored: {restored_qty} (+{total_sold})")
            else:
                print(f"  ⚠️  Product not found in inventory: {product_name}")
    
    # Step 5: Save updated inventory
    try:
        # Create backup of current inventory
        inventory_backup = f'backups/inventory_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        pd.read_csv(inventory_file, dtype={'Barcode': str}).to_csv(inventory_backup, index=False)
        print(f"\n💾 Inventory backup created: {inventory_backup}")
        
        # Save updated inventory with proper barcode formatting
        inventory_df.to_csv(inventory_file, index=False)
        print("✅ Inventory updated successfully!")
        
    except Exception as e:
        print(f"❌ Error saving inventory: {e}")
        return
    
    # Step 6: Clear transactions file
    try:
        # Create empty transactions file with headers
        empty_transactions = pd.DataFrame(columns=[
            'Transaction_ID', 'Date', 'Time', 'Customer_Name', 'Customer_Phone',
            'Product_Name', 'Quantity_Sold', 'Unit_Price', 'Total_Amount',
            'Payment_Method', 'Discount', 'Final_Amount'
        ])
        empty_transactions.to_csv(transactions_file, index=False)
        print("🗑️  Transaction history cleared!")
        
    except Exception as e:
        print(f"❌ Error clearing transactions: {e}")
        return
    
    # Step 6.5: Clear customer database
    try:
        import json
        # Create empty customers file
        empty_customers = {}
        os.makedirs('data', exist_ok=True)
        with open(customers_file, 'w') as f:
            json.dump(empty_customers, f, indent=2)
        print("🗑️  Customer database cleared!")
        
    except Exception as e:
        print(f"❌ Error clearing customers: {e}")
        return
    
    # Step 7: Display final summary
    print("\n" + "=" * 60)
    print("🎉 RESTORATION COMPLETE!")
    print("=" * 60)
    
    if restoration_summary:
        print(f"📊 Summary:")
        print(f"  • Products restored: {len(restoration_summary)}")
        print(f"  • Total units restored: {sum(item['sold'] for item in restoration_summary.values())}")
        print(f"  • Transaction records cleared: {len(transactions_df) if not transactions_df.empty else 0}")
        print(f"  • Customer database cleared: ✅")
    else:
        print("📊 No transactions found to restore.")
        print("📊 Customer database cleared: ✅")
    
    print(f"\n📁 Backup files created:")
    if not transactions_df.empty:
        print(f"  • Transactions: {backup_transactions_file}")
    if os.path.exists(backup_customers_file):
        print(f"  • Customers: {backup_customers_file}")
    print(f"  • Inventory: {inventory_backup}")
    
    print("\n✨ Your inventory has been restored to pre-testing state!")
    print("✨ All test transactions and customers have been cleared!")

if __name__ == "__main__":
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🏪 Shop Management System - Inventory Restoration Tool")
    print("=" * 60)
    
    # Confirm before proceeding
    print("⚠️  This will:")
    print("   1. Restore inventory quantities by adding back sold items")
    print("   2. Clear ALL transaction history")
    print("   3. Clear ALL customer data")
    print("   4. Create backup files for safety")
    
    confirm = input("\n❓ Do you want to proceed? (yes/no): ").lower().strip()
    
    if confirm in ['yes', 'y']:
        main()
    else:
        print("❌ Operation cancelled by user.")
