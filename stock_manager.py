"""
📦 BAUJI TRADERS - STOCK MANAGEMENT MODULE
=========================================
Complete inventory and stock management functionality
"""

import pandas as pd
import os
from datetime import datetime, date
import json

class StockManager:
    def __init__(self, shop_manager):
        self.shop = shop_manager
        
    def add_new_stock(self):
        """Add new stock/purchase"""
        print("\n📦 ADD NEW STOCK")
        print("=" * 30)
        
        # Supplier details
        supplier = input("Supplier name: ").strip()
        invoice_no = input("Invoice/Bill number: ").strip()
        
        # Purchase items
        purchase_items = []
        total_purchase_amount = 0
        
        print("\nAdding items to purchase...")
        print("Enter 'done' when finished")
        
        while True:
            product_name = input("\n📝 Product name (or 'done'): ").strip()
            
            if product_name.lower() == 'done':
                break
                
            if not product_name:
                continue
                
            try:
                quantity = int(input("Quantity purchased: "))
                if quantity <= 0:
                    print("❌ Quantity must be positive")
                    continue
                    
                total_amount = float(input("Total amount for this item: ₹"))
                if total_amount <= 0:
                    print("❌ Amount must be positive")
                    continue
                    
                # Calculate cost price per unit
                cost_per_unit = total_amount / quantity
                
                # Get MRP
                mrp = float(input(f"MRP per unit (suggested: ₹{cost_per_unit * 1.2:.2f}): "))
                
                purchase_item = {
                    'product_name': product_name,
                    'quantity': quantity,
                    'total_amount': total_amount,
                    'cost_per_unit': cost_per_unit,
                    'mrp': mrp
                }
                
                purchase_items.append(purchase_item)
                total_purchase_amount += total_amount
                
                print(f"✅ Added: {quantity} x {product_name} @ ₹{cost_per_unit:.2f} = ₹{total_amount:.2f}")
                
            except ValueError:
                print("❌ Please enter valid numbers")
                continue
                
        if not purchase_items:
            print("❌ No items added")
            return
            
        # Display purchase summary
        print(f"\n📋 PURCHASE SUMMARY")
        print("=" * 50)
        print(f"Supplier: {supplier}")
        print(f"Invoice: {invoice_no}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        print("-" * 50)
        
        for item in purchase_items:
            print(f"{item['product_name'][:25]:25} | {item['quantity']:3} @ ₹{item['cost_per_unit']:6.2f} = ₹{item['total_amount']:8.2f}")
            
        print("-" * 50)
        print(f"{'Total Purchase Amount:':35} ₹{total_purchase_amount:8.2f}")
        
        # Confirm purchase
        confirm = input("\n✅ Confirm purchase? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Purchase cancelled")
            return
            
        # Process purchase
        self.process_purchase(supplier, invoice_no, purchase_items, total_purchase_amount)
        
    def process_purchase(self, supplier, invoice_no, purchase_items, total_amount):
        """Process the purchase and update inventory"""
        current_time = datetime.now()
        purchase_id = f"PUR{current_time.strftime('%Y%m%d%H%M%S')}"
        
        # Update inventory
        for item in purchase_items:
            # Check if product exists
            existing_product = self.shop.inventory[self.shop.inventory['Product_Name'] == item['product_name']]
            
            if len(existing_product) > 0:
                # Update existing product
                product_index = existing_product.index[0]
                
                # Update quantity
                self.shop.inventory.loc[product_index, 'Quantity'] += item['quantity']
                
                # Update weighted average cost price
                old_qty = existing_product.iloc[0]['Quantity']
                old_cost = existing_product.iloc[0]['Cost_Price']
                new_qty = old_qty + item['quantity']
                
                if old_qty > 0:
                    weighted_cost = ((old_qty * old_cost) + (item['quantity'] * item['cost_per_unit'])) / new_qty
                else:
                    weighted_cost = item['cost_per_unit']
                    
                self.shop.inventory.loc[product_index, 'Cost_Price'] = weighted_cost
                self.shop.inventory.loc[product_index, 'MRP'] = item['mrp']
                
                # Recalculate selling prices
                self.shop.inventory.loc[product_index, 'SP_5_Percent'] = item['mrp'] * 0.95
                self.shop.inventory.loc[product_index, 'SP_10_Percent'] = item['mrp'] * 0.90
                
                print(f"✅ Updated: {item['product_name']} - New Qty: {new_qty}, Avg Cost: ₹{weighted_cost:.2f}")
                
            else:
                # Add new product
                new_product = {
                    'Sr_No': len(self.shop.inventory) + 1,
                    'Product_Name': item['product_name'],
                    'Category': 'General',
                    'Brand': '',
                    'Size': '',
                    'Quantity': item['quantity'],
                    'MRP': item['mrp'],
                    'Cost_Price': item['cost_per_unit'],
                    'SP_5_Percent': item['mrp'] * 0.95,
                    'SP_10_Percent': item['mrp'] * 0.90,
                    'Supplier': supplier,
                    'Last_Updated': current_time.strftime('%Y-%m-%d'),
                    'Status': 'Active'
                }
                
                self.shop.inventory = pd.concat([self.shop.inventory, pd.DataFrame([new_product])], ignore_index=True)
                print(f"✅ Added new product: {item['product_name']}")
                
            # Record stock movement
            self.record_stock_movement(item['product_name'], 'PURCHASE', item['quantity'], 
                                     purchase_id, f"Purchase from {supplier} - Invoice: {invoice_no}")
        
        # Save updated inventory
        self.shop.save_inventory()
        
        # Record purchase transaction
        self.record_purchase_transaction(purchase_id, supplier, invoice_no, purchase_items, total_amount)
        
        print(f"\n✅ Purchase completed! Purchase ID: {purchase_id}")
        
    def record_purchase_transaction(self, purchase_id, supplier, invoice_no, purchase_items, total_amount):
        """Record purchase transaction"""
        current_time = datetime.now()
        
        # Create purchases file if it doesn't exist
        purchases_file = os.path.join(self.shop.data_dir, 'purchases.csv')
        if not os.path.exists(purchases_file):
            purchases_df = pd.DataFrame(columns=[
                'Purchase_ID', 'Date', 'Time', 'Supplier', 'Invoice_No', 
                'Product_Name', 'Quantity', 'Cost_Per_Unit', 'Total_Amount', 'MRP'
            ])
            purchases_df.to_csv(purchases_file, index=False)
        
        # Add purchase records
        for item in purchase_items:
            purchase_record = {
                'Purchase_ID': purchase_id,
                'Date': current_time.strftime('%Y-%m-%d'),
                'Time': current_time.strftime('%H:%M:%S'),
                'Supplier': supplier,
                'Invoice_No': invoice_no,
                'Product_Name': item['product_name'],
                'Quantity': item['quantity'],
                'Cost_Per_Unit': item['cost_per_unit'],
                'Total_Amount': item['total_amount'],
                'MRP': item['mrp']
            }
            
            purchases_df = pd.read_csv(purchases_file)
            purchases_df = pd.concat([purchases_df, pd.DataFrame([purchase_record])], ignore_index=True)
            purchases_df.to_csv(purchases_file, index=False)
            
    def record_stock_movement(self, product_name, movement_type, quantity, reference, notes):
        """Record stock movement"""
        current_time = datetime.now()
        
        movement_record = {
            'Date': current_time.strftime('%Y-%m-%d'),
            'Time': current_time.strftime('%H:%M:%S'),
            'Product_Name': product_name,
            'Movement_Type': movement_type,
            'Quantity': quantity,
            'Reference': reference,
            'Notes': notes,
            'User': 'Admin'
        }
        
        stock_df = pd.read_csv(self.shop.stock_movements_file)
        stock_df = pd.concat([stock_df, pd.DataFrame([movement_record])], ignore_index=True)
        stock_df.to_csv(self.shop.stock_movements_file, index=False)
        
    def stock_adjustment(self):
        """Manual stock adjustment"""
        print("\n🔧 STOCK ADJUSTMENT")
        print("=" * 30)
        
        # Search product
        search_term = input("🔍 Search product: ").strip()
        
        if not search_term:
            return
            
        # Find matching products
        matches = self.shop.inventory[self.shop.inventory['Product_Name'].str.contains(search_term, case=False, na=False)]
        
        if len(matches) == 0:
            print("❌ No products found")
            return
        elif len(matches) == 1:
            product = matches.iloc[0]
            product_index = matches.index[0]
        else:
            print(f"\n📋 Found {len(matches)} products:")
            for idx, (_, row) in enumerate(matches.head(10).iterrows()):
                print(f"{idx+1}. {row['Product_Name']} - Current Stock: {row['Quantity']}")
            
            try:
                choice = int(input("\nSelect product: ")) - 1
                if 0 <= choice < len(matches):
                    product = matches.iloc[choice]
                    product_index = matches.index[choice]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid selection")
                return
        
        print(f"\n📦 Product: {product['Product_Name']}")
        print(f"📊 Current Stock: {product['Quantity']}")
        
        # Get adjustment details
        print("\nAdjustment Type:")
        print("1. Set exact quantity")
        print("2. Add quantity")
        print("3. Subtract quantity")
        
        adj_type = input("Select type (1-3): ").strip()
        
        try:
            if adj_type == '1':
                new_qty = int(input("Enter exact quantity: "))
                adjustment = new_qty - product['Quantity']
                final_qty = new_qty
            elif adj_type == '2':
                add_qty = int(input("Quantity to add: "))
                adjustment = add_qty
                final_qty = product['Quantity'] + add_qty
            elif adj_type == '3':
                sub_qty = int(input("Quantity to subtract: "))
                adjustment = -sub_qty
                final_qty = product['Quantity'] - sub_qty
                if final_qty < 0:
                    print("❌ Cannot have negative stock")
                    return
            else:
                print("❌ Invalid type")
                return
                
            reason = input("Reason for adjustment: ").strip() or "Manual adjustment"
            
            print(f"\n📋 Adjustment Summary:")
            print(f"Product: {product['Product_Name']}")
            print(f"Current Stock: {product['Quantity']}")
            print(f"Adjustment: {adjustment:+d}")
            print(f"Final Stock: {final_qty}")
            print(f"Reason: {reason}")
            
            confirm = input("\n✅ Confirm adjustment? (y/n): ").strip().lower()
            if confirm == 'y':
                # Update inventory
                self.shop.inventory.loc[product_index, 'Quantity'] = final_qty
                self.shop.save_inventory()
                
                # Record stock movement
                movement_type = 'ADJUSTMENT_IN' if adjustment > 0 else 'ADJUSTMENT_OUT'
                self.record_stock_movement(product['Product_Name'], movement_type, abs(adjustment), 
                                         f"ADJ{datetime.now().strftime('%Y%m%d%H%M%S')}", reason)
                
                print(f"✅ Stock adjusted successfully!")
                
        except ValueError:
            print("❌ Invalid quantity")
            
    def check_low_stock(self):
        """Check products with low stock"""
        print("\n⚠️  LOW STOCK ALERT")
        print("=" * 40)
        
        # Define low stock threshold
        try:
            threshold = int(input("Enter low stock threshold (default 10): ") or "10")
        except ValueError:
            threshold = 10
            
        low_stock = self.shop.inventory[self.shop.inventory['Quantity'] <= threshold]
        
        if len(low_stock) == 0:
            print(f"✅ No products below {threshold} units")
            return
            
        print(f"\n📊 Products with stock ≤ {threshold} units:")
        print("-" * 60)
        
        for _, product in low_stock.iterrows():
            status = "🔴 OUT OF STOCK" if product['Quantity'] == 0 else "🟡 LOW STOCK"
            print(f"{status} | {product['Product_Name'][:35]:35} | Stock: {product['Quantity']:3}")
            
        print(f"\n📈 Total items needing restock: {len(low_stock)}")
        
        # Generate restock suggestions
        self.generate_restock_suggestions(low_stock)
        
    def generate_restock_suggestions(self, low_stock_items):
        """Generate restock suggestions"""
        save_suggestions = input("\n💡 Generate restock suggestions file? (y/n): ").strip().lower()
        
        if save_suggestions == 'y':
            suggestions = []
            
            for _, product in low_stock_items.iterrows():
                # Calculate suggested order quantity based on sales history
                suggested_qty = max(20, int(product['Quantity']) + 50)  # Simple logic
                
                suggestion = {
                    'Product_Name': product['Product_Name'],
                    'Current_Stock': product['Quantity'],
                    'Suggested_Order_Qty': suggested_qty,
                    'Last_Cost_Price': product['Cost_Price'],
                    'Estimated_Order_Value': suggested_qty * product['Cost_Price'],
                    'Supplier': product.get('Supplier', 'TBD'),
                    'Priority': 'HIGH' if product['Quantity'] == 0 else 'MEDIUM'
                }
                
                suggestions.append(suggestion)
                
            # Save to file
            suggestions_df = pd.DataFrame(suggestions)
            filename = f"restock_suggestions_{datetime.now().strftime('%Y%m%d')}.csv"
            filepath = os.path.join(self.shop.data_dir, filename)
            suggestions_df.to_csv(filepath, index=False)
            
            print(f"✅ Restock suggestions saved to: {filename}")
            
    def view_stock_movements(self):
        """View stock movement history"""
        print("\n📊 STOCK MOVEMENT HISTORY")
        print("=" * 40)
        
        try:
            stock_df = pd.read_csv(self.shop.stock_movements_file)
            
            if len(stock_df) == 0:
                print("No stock movements found")
                return
                
            # Filter options
            print("Filter options:")
            print("1. Today's movements")
            print("2. Last 7 days")
            print("3. Specific product")
            print("4. All movements (last 50)")
            
            choice = input("Select filter (1-4): ").strip()
            
            if choice == '1':
                today = datetime.now().strftime('%Y-%m-%d')
                filtered_df = stock_df[stock_df['Date'] == today]
                title = f"Today's Stock Movements ({today})"
            elif choice == '2':
                # Last 7 days
                from datetime import timedelta
                week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                filtered_df = stock_df[stock_df['Date'] >= week_ago]
                title = "Last 7 Days Stock Movements"
            elif choice == '3':
                product_search = input("Enter product name: ").strip()
                filtered_df = stock_df[stock_df['Product_Name'].str.contains(product_search, case=False, na=False)]
                title = f"Stock Movements for '{product_search}'"
            else:
                filtered_df = stock_df.tail(50)
                title = "Recent Stock Movements (Last 50)"
                
            if len(filtered_df) == 0:
                print("No movements found for the selected filter")
                return
                
            print(f"\n📋 {title}")
            print("-" * 80)
            
            for _, movement in filtered_df.iterrows():
                print(f"{movement['Date']} {movement['Time']} | {movement['Movement_Type']:12} | "
                      f"{movement['Product_Name'][:25]:25} | Qty: {movement['Quantity']:4} | "
                      f"Ref: {movement['Reference']}")
                      
        except Exception as e:
            print(f"❌ Error loading stock movements: {e}")
            
    def stock_valuation(self):
        """Calculate current stock valuation"""
        print("\n💰 STOCK VALUATION")
        print("=" * 30)
        
        try:
            # Calculate at cost price
            self.shop.inventory['Stock_Value_Cost'] = self.shop.inventory['Quantity'] * self.shop.inventory['Cost_Price']
            
            # Calculate at MRP
            self.shop.inventory['Stock_Value_MRP'] = self.shop.inventory['Quantity'] * self.shop.inventory['MRP']
            
            total_cost_value = self.shop.inventory['Stock_Value_Cost'].sum()
            total_mrp_value = self.shop.inventory['Stock_Value_MRP'].sum()
            potential_profit = total_mrp_value - total_cost_value
            
            print(f"📊 INVENTORY VALUATION SUMMARY")
            print("=" * 50)
            print(f"Total Items: {len(self.shop.inventory):,}")
            print(f"Total Quantity: {self.shop.inventory['Quantity'].sum():,}")
            print(f"Stock Value (Cost Price): ₹{total_cost_value:,.2f}")
            print(f"Stock Value (MRP): ₹{total_mrp_value:,.2f}")
            print(f"Potential Profit: ₹{potential_profit:,.2f}")
            print(f"Potential Margin: {(potential_profit/total_cost_value)*100:.1f}%")
            
            # Category-wise valuation
            print(f"\n📈 CATEGORY-WISE VALUATION:")
            print("-" * 50)
            
            category_valuation = self.shop.inventory.groupby('Category').agg({
                'Quantity': 'sum',
                'Stock_Value_Cost': 'sum',
                'Stock_Value_MRP': 'sum'
            }).sort_values('Stock_Value_Cost', ascending=False)
            
            for category, data in category_valuation.iterrows():
                margin = ((data['Stock_Value_MRP'] - data['Stock_Value_Cost']) / data['Stock_Value_Cost']) * 100
                print(f"{category[:20]:20} | Qty: {data['Quantity']:5,.0f} | Cost: ₹{data['Stock_Value_Cost']:8,.0f} | "
                      f"MRP: ₹{data['Stock_Value_MRP']:8,.0f} | Margin: {margin:5.1f}%")
                      
            # Save valuation report
            save_report = input("\n💾 Save valuation report? (y/n): ").strip().lower()
            if save_report == 'y':
                filename = f"stock_valuation_{datetime.now().strftime('%Y%m%d')}.xlsx"
                filepath = os.path.join(self.shop.data_dir, filename)
                
                with pd.ExcelWriter(filepath) as writer:
                    # Summary sheet
                    summary_data = {
                        'Metric': ['Total Items', 'Total Quantity', 'Stock Value (Cost)', 'Stock Value (MRP)', 
                                 'Potential Profit', 'Potential Margin %'],
                        'Value': [len(self.shop.inventory), self.shop.inventory['Quantity'].sum(),
                                total_cost_value, total_mrp_value, potential_profit, 
                                (potential_profit/total_cost_value)*100]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Detailed inventory
                    valuation_df = self.shop.inventory[['Product_Name', 'Category', 'Quantity', 'Cost_Price', 
                                                      'MRP', 'Stock_Value_Cost', 'Stock_Value_MRP']].copy()
                    valuation_df.to_excel(writer, sheet_name='Detailed_Valuation', index=False)
                    
                    # Category summary
                    category_valuation.to_excel(writer, sheet_name='Category_Wise')
                    
                print(f"✅ Valuation report saved: {filename}")
                
        except Exception as e:
            print(f"❌ Error calculating stock valuation: {e}")
            
    def bulk_price_update(self):
        """Bulk update prices"""
        print("\n💲 BULK PRICE UPDATE")
        print("=" * 30)
        
        print("Update options:")
        print("1. Update by category")
        print("2. Update by percentage increase")
        print("3. Update specific products from file")
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == '1':
            self.update_prices_by_category()
        elif choice == '2':
            self.update_prices_by_percentage()
        elif choice == '3':
            self.update_prices_from_file()
        else:
            print("❌ Invalid option")
            
    def update_prices_by_category(self):
        """Update prices by category"""
        categories = self.shop.inventory['Category'].unique()
        
        print(f"\nAvailable categories:")
        for i, category in enumerate(categories):
            print(f"{i+1}. {category}")
            
        try:
            cat_choice = int(input("Select category: ")) - 1
            if 0 <= cat_choice < len(categories):
                selected_category = categories[cat_choice]
                
                percentage = float(input(f"Percentage increase for {selected_category} (%): "))
                
                # Update MRP for selected category
                category_mask = self.shop.inventory['Category'] == selected_category
                old_mrp = self.shop.inventory.loc[category_mask, 'MRP'].copy()
                
                self.shop.inventory.loc[category_mask, 'MRP'] *= (1 + percentage/100)
                
                # Recalculate selling prices
                self.shop.inventory.loc[category_mask, 'SP_5_Percent'] = self.shop.inventory.loc[category_mask, 'MRP'] * 0.95
                self.shop.inventory.loc[category_mask, 'SP_10_Percent'] = self.shop.inventory.loc[category_mask, 'MRP'] * 0.90
                
                affected_items = category_mask.sum()
                
                print(f"✅ Updated {affected_items} items in {selected_category} category")
                print(f"📈 Applied {percentage}% price increase")
                
                # Save changes
                confirm = input("Save changes? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.shop.save_inventory()
                    print("✅ Prices updated successfully")
                else:
                    # Restore old prices
                    self.shop.inventory.loc[category_mask, 'MRP'] = old_mrp
                    self.shop.inventory.loc[category_mask, 'SP_5_Percent'] = old_mrp * 0.95
                    self.shop.inventory.loc[category_mask, 'SP_10_Percent'] = old_mrp * 0.90
                    print("❌ Changes discarded")
                    
        except (ValueError, IndexError):
            print("❌ Invalid input")
            
    def update_prices_by_percentage(self):
        """Update all prices by percentage"""
        try:
            percentage = float(input("Percentage increase for all products (%): "))
            
            old_mrp = self.shop.inventory['MRP'].copy()
            
            # Update all MRP
            self.shop.inventory['MRP'] *= (1 + percentage/100)
            
            # Recalculate selling prices
            self.shop.inventory['SP_5_Percent'] = self.shop.inventory['MRP'] * 0.95
            self.shop.inventory['SP_10_Percent'] = self.shop.inventory['MRP'] * 0.90
            
            affected_items = len(self.shop.inventory)
            
            print(f"✅ Applied {percentage}% increase to {affected_items} products")
            
            # Save changes
            confirm = input("Save changes? (y/n): ").strip().lower()
            if confirm == 'y':
                self.shop.save_inventory()
                print("✅ Prices updated successfully")
            else:
                # Restore old prices
                self.shop.inventory['MRP'] = old_mrp
                self.shop.inventory['SP_5_Percent'] = old_mrp * 0.95
                self.shop.inventory['SP_10_Percent'] = old_mrp * 0.90
                print("❌ Changes discarded")
                
        except ValueError:
            print("❌ Invalid percentage")
            
    def update_prices_from_file(self):
        """Update prices from CSV file"""
        filename = input("Enter CSV filename (with product names and new MRP): ").strip()
        filepath = os.path.join(self.shop.data_dir, filename)
        
        try:
            price_updates = pd.read_csv(filepath)
            
            if 'Product_Name' not in price_updates.columns or 'MRP' not in price_updates.columns:
                print("❌ CSV must have 'Product_Name' and 'MRP' columns")
                return
                
            updated_count = 0
            
            for _, update in price_updates.iterrows():
                product_mask = self.shop.inventory['Product_Name'] == update['Product_Name']
                
                if product_mask.any():
                    self.shop.inventory.loc[product_mask, 'MRP'] = update['MRP']
                    self.shop.inventory.loc[product_mask, 'SP_5_Percent'] = update['MRP'] * 0.95
                    self.shop.inventory.loc[product_mask, 'SP_10_Percent'] = update['MRP'] * 0.90
                    updated_count += 1
                    
            print(f"✅ Updated {updated_count} products from file")
            
            if updated_count > 0:
                confirm = input("Save changes? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.shop.save_inventory()
                    print("✅ Prices updated successfully")
                    
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
