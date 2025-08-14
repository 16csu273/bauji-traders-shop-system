#!/usr/bin/env python3
"""
Rebuild Customer Database from Transaction History
=================================================

This script will:
1. Read all transaction history
2. Extract customer information
3. Rebuild the customers.json file with phone as primary key
4. Calculate total purchases and visit history for each customer

Usage: python rebuild_customers.py
"""

import pandas as pd
import json
import os
from collections import defaultdict

def main():
    print("🔄 Rebuilding customer database from transaction history...")
    print("=" * 60)
    
    # File paths
    transactions_file = 'data/sales_transactions.csv'
    customers_file = 'data/customers.json'
    
    try:
        # Read transaction history
        if not os.path.exists(transactions_file):
            print("❌ No transaction history found!")
            return
            
        transactions_df = pd.read_csv(transactions_file)
        print(f"📊 Found {len(transactions_df)} transactions to process")
        
        if transactions_df.empty:
            print("⚠️ No transactions found in history")
            return
        
        # Process customer data
        customers = {}
        
        for _, transaction in transactions_df.iterrows():
            customer_name = transaction.get('Customer_Name', '').strip()
            customer_phone = str(transaction.get('Customer_Phone', '')).strip()
            final_amount = float(transaction.get('Final_Amount', 0))
            date = transaction.get('Date', '')
            
            if not customer_phone or customer_phone == 'nan':
                print(f"⚠️ Skipping transaction with no phone: {customer_name}")
                continue
            
            # Use phone as primary key
            if customer_phone in customers:
                # Update existing customer
                customers[customer_phone]['total_purchases'] += final_amount
                customers[customer_phone]['loyalty_points'] += 1
                # Update last visit if this date is more recent
                if date > customers[customer_phone]['last_visit']:
                    customers[customer_phone]['last_visit'] = date
            else:
                # Add new customer
                customers[customer_phone] = {
                    'name': customer_name,
                    'phone': customer_phone,
                    'email': '',  # Email not available in transaction history
                    'total_purchases': final_amount,
                    'last_visit': date,
                    'loyalty_points': 1
                }
        
        # Save customers file
        os.makedirs('data', exist_ok=True)
        with open(customers_file, 'w') as f:
            json.dump(customers, f, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ Customer database rebuilt successfully!")
        print("=" * 60)
        print(f"📊 Customers processed: {len(customers)}")
        
        # Show customer summary
        print("\n📋 Customer Summary:")
        print("-" * 40)
        for phone, data in customers.items():
            print(f"  • {data['name']} ({phone})")
            print(f"    Total Purchases: ₹{data['total_purchases']:.2f}")
            print(f"    Visits: {data['loyalty_points']}")
            print(f"    Last Visit: {data['last_visit']}")
            print()
        
    except Exception as e:
        print(f"❌ Error rebuilding customers: {e}")

if __name__ == "__main__":
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🏪 Customer Database Rebuild Tool")
    print("=" * 60)
    
    main()
