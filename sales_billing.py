"""
🏪 BAUJI TRADERS - SALES & BILLING MODULE
=======================================
Complete billing and sales functionality
"""

import pandas as pd
import os
from datetime import datetime, date
import uuid

class SalesBilling:
    def __init__(self, shop_manager):
        self.shop = shop_manager
        
    def create_new_bill(self):
        """Create a new bill/invoice"""
        print("\n💰 NEW BILL/INVOICE")
        print("=" * 40)
        
        # Generate transaction ID
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Customer details
        customer_name = input("Customer Name (press Enter for Walk-in): ").strip() or "Walk-in Customer"
        customer_phone = input("Customer Phone (optional): ").strip()
        
        # Add customer if new
        if customer_phone and customer_phone not in self.shop.customers:
            self.shop.customers[customer_phone] = {
                'name': customer_name,
                'phone': customer_phone,
                'total_purchases': 0,
                'last_visit': datetime.now().isoformat()
            }
            self.shop.save_customers()
        
        bill_items = []
        total_amount = 0
        
        print(f"\n📋 Adding items to bill (Transaction: {transaction_id})")
        print("Enter 'done' when finished adding items")
        
        while True:
            # Product search
            search_term = input("\n🔍 Search product (or 'done' to finish): ").strip()
            
            if search_term.lower() == 'done':
                break
                
            if search_term == '':
                continue
                
            # Find matching products
            matches = self.shop.inventory[self.shop.inventory['Product_Name'].str.contains(search_term, case=False, na=False)]
            
            if len(matches) == 0:
                print("❌ No products found. Try different keywords.")
                continue
            elif len(matches) == 1:
                product = matches.iloc[0]
            else:
                print(f"\n📋 Found {len(matches)} products:")
                for idx, (_, row) in enumerate(matches.head(10).iterrows()):
                    print(f"{idx+1}. {row['Product_Name']} - Stock: {row['Quantity']} - Cost: ₹{row['Cost_Price']:.2f} - MRP: ₹{row['MRP']:.2f}")
                
                try:
                    choice = int(input("\nSelect product (number): ")) - 1
                    if 0 <= choice < len(matches):
                        product = matches.iloc[choice]
                    else:
                        print("❌ Invalid selection")
                        continue
                except ValueError:
                    print("❌ Please enter a valid number")
                    continue
            
            # Check stock
            if product['Quantity'] <= 0:
                print(f"❌ {product['Product_Name']} is out of stock!")
                continue
                
            # Get quantity
            try:
                qty_sold = int(input(f"Quantity to sell (Available: {product['Quantity']}): "))
                if qty_sold <= 0:
                    print("❌ Quantity must be positive")
                    continue
                elif qty_sold > product['Quantity']:
                    print(f"❌ Not enough stock! Available: {product['Quantity']}")
                    continue
            except ValueError:
                print("❌ Please enter a valid number")
                continue
            
            # Price selection
            print(f"\nPrice options for {product['Product_Name']}:")
            print(f"1. MRP: ₹{product['MRP']:.2f}")
            print(f"2. SP 5%: ₹{product['SP_5_Percent']:.2f}")
            print(f"3. SP 10%: ₹{product['SP_10_Percent']:.2f}")
            print("4. Custom price")
            
            price_choice = input("Select price (1-4): ").strip()
            
            if price_choice == '1':
                unit_price = product['MRP']
            elif price_choice == '2':
                unit_price = product['SP_5_Percent']
            elif price_choice == '3':
                unit_price = product['SP_10_Percent']
            elif price_choice == '4':
                try:
                    unit_price = float(input("Enter custom price: ₹"))
                    if unit_price < product['Cost_Price']:
                        confirm = input(f"⚠️  Price below cost (₹{product['Cost_Price']:.2f}). Continue? (y/n): ")
                        if confirm.lower() != 'y':
                            continue
                except ValueError:
                    print("❌ Invalid price")
                    continue
            else:
                print("❌ Invalid choice, using MRP")
                unit_price = product['MRP']
            
            # Calculate line total
            line_total = qty_sold * unit_price
            
            # Add to bill
            bill_item = {
                'product_name': product['Product_Name'],
                'quantity': qty_sold,
                'unit_price': unit_price,
                'line_total': line_total,
                'cost_price': product['Cost_Price'],
                'profit': (unit_price - product['Cost_Price']) * qty_sold
            }
            
            bill_items.append(bill_item)
            total_amount += line_total
            
            print(f"✅ Added: {qty_sold} x {product['Product_Name']} @ ₹{unit_price:.2f} = ₹{line_total:.2f}")
            
        # Check if bill has items
        if not bill_items:
            print("❌ No items added to bill")
            return
            
        # Display bill summary
        self.display_bill_summary(transaction_id, customer_name, customer_phone, bill_items, total_amount)
        
        # Confirm sale
        confirm = input("\n✅ Confirm sale? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Sale cancelled")
            return
            
        # Process payment
        payment_method = self.get_payment_method()
        discount = self.get_discount(total_amount)
        final_amount = total_amount - discount
        
        # Update inventory and save transactions
        self.process_sale(transaction_id, customer_name, customer_phone, bill_items, 
                         total_amount, payment_method, discount, final_amount)
        
        # Print receipt
        self.print_receipt(transaction_id, customer_name, customer_phone, bill_items, 
                          total_amount, payment_method, discount, final_amount)
        
    def quick_sale(self):
        """Quick sale for single item"""
        print("\n⚡ QUICK SALE")
        print("=" * 20)
        
        # Product search
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
        else:
            print(f"\n📋 Found {len(matches)} products:")
            for idx, (_, row) in enumerate(matches.head(5).iterrows()):
                print(f"{idx+1}. {row['Product_Name']} - Cost: ₹{row['Cost_Price']:.2f} - MRP: ₹{row['MRP']:.2f}")
            
            try:
                choice = int(input("\nSelect product: ")) - 1
                product = matches.iloc[choice]
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                return
        
        # Quick quantity input
        try:
            qty = int(input(f"Quantity (Available: {product['Quantity']}): "))
            if qty <= 0 or qty > product['Quantity']:
                print("❌ Invalid quantity")
                return
        except ValueError:
            print("❌ Invalid quantity")
            return
        
        # Use MRP by default
        unit_price = product['MRP']
        total = qty * unit_price
        
        print(f"\n💰 Quick Sale: {qty} x {product['Product_Name']} = ₹{total:.2f}")
        
        confirm = input("Confirm quick sale? (y/n): ").strip().lower()
        if confirm == 'y':
            # Generate transaction ID
            transaction_id = f"QS{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Process as quick sale
            self.process_quick_sale(transaction_id, product, qty, unit_price, total)
            print(f"✅ Quick sale completed! Transaction: {transaction_id}")
        
    def display_bill_summary(self, transaction_id, customer_name, customer_phone, bill_items, total_amount):
        """Display bill summary"""
        print(f"\n📄 BILL SUMMARY")
        print("=" * 60)
        print(f"Transaction ID: {transaction_id}")
        print(f"Customer: {customer_name}")
        if customer_phone:
            print(f"Phone: {customer_phone}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        total_profit = 0
        for item in bill_items:
            print(f"{item['product_name'][:30]:30} | {item['quantity']:3} x ₹{item['unit_price']:6.2f} = ₹{item['line_total']:8.2f}")
            total_profit += item['profit']
            
        print("-" * 60)
        print(f"{'Total Amount:':45} ₹{total_amount:8.2f}")
        print(f"{'Total Profit:':45} ₹{total_profit:8.2f}")
        
    def get_payment_method(self):
        """Get payment method"""
        print("\n💳 Payment Method:")
        print("1. Cash")
        print("2. Card")
        print("3. UPI/Digital")
        print("4. Credit")
        
        choice = input("Select payment method (1-4): ").strip()
        methods = {'1': 'Cash', '2': 'Card', '3': 'UPI', '4': 'Credit'}
        return methods.get(choice, 'Cash')
        
    def get_discount(self, total_amount):
        """Get discount amount"""
        discount_input = input(f"Discount amount (₹) or % (press Enter for no discount): ").strip()
        
        if not discount_input:
            return 0
            
        try:
            if discount_input.endswith('%'):
                percentage = float(discount_input[:-1])
                return (total_amount * percentage) / 100
            else:
                return float(discount_input)
        except ValueError:
            print("❌ Invalid discount, no discount applied")
            return 0
            
    def process_sale(self, transaction_id, customer_name, customer_phone, bill_items, 
                    total_amount, payment_method, discount, final_amount):
        """Process the sale and update records"""
        current_time = datetime.now()
        
        # Update inventory
        for item in bill_items:
            product_index = self.shop.inventory[self.shop.inventory['Product_Name'] == item['product_name']].index[0]
            self.shop.inventory.loc[product_index, 'Quantity'] -= item['quantity']
            
            # Record stock movement
            self.record_stock_movement(item['product_name'], 'SALE', item['quantity'], 
                                     transaction_id, f"Sale to {customer_name}")
        
        # Save updated inventory
        self.shop.save_inventory()
        
        # Record sales transactions
        for item in bill_items:
            sale_record = {
                'Transaction_ID': transaction_id,
                'Date': current_time.strftime('%Y-%m-%d'),
                'Time': current_time.strftime('%H:%M:%S'),
                'Customer_Name': customer_name,
                'Customer_Phone': customer_phone,
                'Product_Name': item['product_name'],
                'Quantity_Sold': item['quantity'],
                'Unit_Price': item['unit_price'],
                'Total_Amount': item['line_total'],
                'Payment_Method': payment_method,
                'Discount': discount / len(bill_items),  # Distribute discount
                'Final_Amount': item['line_total'] - (discount / len(bill_items))
            }
            
            # Append to sales file
            sales_df = pd.read_csv(self.shop.sales_file)
            sales_df = pd.concat([sales_df, pd.DataFrame([sale_record])], ignore_index=True)
            sales_df.to_csv(self.shop.sales_file, index=False)
        
        # Update customer info
        if customer_phone and customer_phone in self.shop.customers:
            self.shop.customers[customer_phone]['total_purchases'] += final_amount
            self.shop.customers[customer_phone]['last_visit'] = current_time.isoformat()
            self.shop.save_customers()
            
    def process_quick_sale(self, transaction_id, product, qty, unit_price, total):
        """Process quick sale"""
        current_time = datetime.now()
        
        # Update inventory
        product_index = self.shop.inventory[self.shop.inventory['Product_Name'] == product['Product_Name']].index[0]
        self.shop.inventory.loc[product_index, 'Quantity'] -= qty
        self.shop.save_inventory()
        
        # Record stock movement
        self.record_stock_movement(product['Product_Name'], 'QUICK_SALE', qty, 
                                 transaction_id, "Quick sale")
        
        # Record sales transaction
        sale_record = {
            'Transaction_ID': transaction_id,
            'Date': current_time.strftime('%Y-%m-%d'),
            'Time': current_time.strftime('%H:%M:%S'),
            'Customer_Name': 'Walk-in Customer',
            'Customer_Phone': '',
            'Product_Name': product['Product_Name'],
            'Quantity_Sold': qty,
            'Unit_Price': unit_price,
            'Total_Amount': total,
            'Payment_Method': 'Cash',
            'Discount': 0,
            'Final_Amount': total
        }
        
        sales_df = pd.read_csv(self.shop.sales_file)
        sales_df = pd.concat([sales_df, pd.DataFrame([sale_record])], ignore_index=True)
        sales_df.to_csv(self.shop.sales_file, index=False)
        
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
        
    def print_receipt(self, transaction_id, customer_name, customer_phone, bill_items, 
                     total_amount, payment_method, discount, final_amount):
        """Print receipt"""
        print(f"\n{'='*50}")
        print(f"        🏪 BAUJI TRADERS")
        print(f"    1690 30FT ROAD, JAWAHAR COLONY")
        print(f"      NIT FARIDABAD - 121001")
        print(f"    PH: 9911148114, 9555269666")
        print(f"{'='*50}")
        print(f"Receipt No: {transaction_id}")
        print(f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"Customer: {customer_name}")
        if customer_phone:
            print(f"Phone: {customer_phone}")
        print(f"{'='*50}")
        
        for item in bill_items:
            print(f"{item['product_name'][:25]:25}")
            print(f"  {item['quantity']} x ₹{item['unit_price']:.2f} = ₹{item['line_total']:.2f}")
            
        print(f"{'-'*50}")
        print(f"Subtotal: ₹{total_amount:.2f}")
        if discount > 0:
            print(f"Discount: -₹{discount:.2f}")
        print(f"{'='*50}")
        print(f"TOTAL: ₹{final_amount:.2f}")
        print(f"Payment: {payment_method}")
        print(f"{'='*50}")
        print(f"Thank you for shopping with us!")
        print(f"Visit again soon!")
        print(f"{'='*50}")
        
    def view_todays_sales(self):
        """View today's sales summary"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            today_sales = sales_df[sales_df['Date'] == today]
            
            if len(today_sales) == 0:
                print(f"\n📊 No sales recorded for today ({today})")
                return
                
            print(f"\n📊 TODAY'S SALES SUMMARY ({today})")
            print("=" * 60)
            
            total_revenue = today_sales['Final_Amount'].sum()
            total_items = today_sales['Quantity_Sold'].sum()
            total_transactions = today_sales['Transaction_ID'].nunique()
            
            print(f"Total Transactions: {total_transactions}")
            print(f"Total Items Sold: {total_items}")
            print(f"Total Revenue: ₹{total_revenue:.2f}")
            print(f"Average Transaction: ₹{total_revenue/total_transactions:.2f}")
            
            # Top selling products today
            print(f"\n📈 Top Selling Products Today:")
            top_products = today_sales.groupby('Product_Name').agg({
                'Quantity_Sold': 'sum',
                'Final_Amount': 'sum'
            }).sort_values('Quantity_Sold', ascending=False).head(10)
            
            for product, data in top_products.iterrows():
                print(f"  {product[:30]:30} | Qty: {data['Quantity_Sold']:3} | Revenue: ₹{data['Final_Amount']:6,.0f}")
                
        except Exception as e:
            print(f"❌ Error loading sales data: {e}")
            
    def process_return(self):
        """Process return/refund"""
        print("\n🔄 RETURN/REFUND")
        print("=" * 30)
        
        transaction_id = input("Enter transaction ID: ").strip()
        
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            transaction_items = sales_df[sales_df['Transaction_ID'] == transaction_id]
            
            if len(transaction_items) == 0:
                print("❌ Transaction not found")
                return
                
            print(f"\n📋 Transaction Items:")
            for idx, item in transaction_items.iterrows():
                print(f"{idx+1}. {item['Product_Name']} - Qty: {item['Quantity_Sold']} - Amount: ₹{item['Final_Amount']:.2f}")
                
            # Select item to return
            try:
                item_choice = int(input("\nSelect item to return (number): ")) - 1
                if item_choice < 0 or item_choice >= len(transaction_items):
                    print("❌ Invalid selection")
                    return
                    
                return_item = transaction_items.iloc[item_choice]
                
                # Return quantity
                max_qty = return_item['Quantity_Sold']
                return_qty = int(input(f"Return quantity (max {max_qty}): "))
                
                if return_qty <= 0 or return_qty > max_qty:
                    print("❌ Invalid quantity")
                    return
                    
                # Process return
                return_amount = (return_item['Final_Amount'] / return_item['Quantity_Sold']) * return_qty
                
                # Update inventory
                product_index = self.shop.inventory[self.shop.inventory['Product_Name'] == return_item['Product_Name']].index[0]
                self.shop.inventory.loc[product_index, 'Quantity'] += return_qty
                self.shop.save_inventory()
                
                # Record stock movement
                self.record_stock_movement(return_item['Product_Name'], 'RETURN', return_qty, 
                                         transaction_id, f"Return from transaction {transaction_id}")
                
                print(f"✅ Return processed: {return_qty} x {return_item['Product_Name']}")
                print(f"💰 Refund amount: ₹{return_amount:.2f}")
                
            except ValueError:
                print("❌ Invalid input")
                
        except Exception as e:
            print(f"❌ Error processing return: {e}")
