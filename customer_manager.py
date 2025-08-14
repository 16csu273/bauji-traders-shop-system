"""
👥 BAUJI TRADERS - CUSTOMER MANAGEMENT MODULE
===========================================
Complete customer relationship management functionality
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import json

class CustomerManager:
    def __init__(self, shop_manager):
        self.shop = shop_manager
        
    def add_customer(self):
        """Add new customer"""
        print("\n👤 ADD NEW CUSTOMER")
        print("=" * 30)
        
        name = input("Customer Name: ").strip()
        if not name:
            print("❌ Name is required")
            return
            
        phone = input("Phone Number: ").strip()
        if not phone:
            print("❌ Phone number is required")
            return
            
        if phone in self.shop.customers:
            print("❌ Customer already exists!")
            return
            
        email = input("Email (optional): ").strip()
        address = input("Address (optional): ").strip()
        
        # Customer details
        customer_data = {
            'name': name,
            'phone': phone,
            'email': email,
            'address': address,
            'registration_date': datetime.now().isoformat(),
            'total_purchases': 0,
            'total_amount': 0,
            'last_visit': datetime.now().isoformat(),
            'visit_count': 0,
            'customer_type': 'Regular',
            'notes': ''
        }
        
        self.shop.customers[phone] = customer_data
        self.shop.save_customers()
        
        print(f"✅ Customer added successfully!")
        print(f"📱 Phone: {phone}")
        print(f"👤 Name: {name}")
        
    def search_customer(self):
        """Search for customers"""
        print("\n🔍 SEARCH CUSTOMERS")
        print("=" * 30)
        
        search_term = input("Enter name or phone number: ").strip()
        
        if not search_term:
            return
            
        found_customers = []
        
        for phone, customer in self.shop.customers.items():
            if (search_term.lower() in customer['name'].lower() or 
                search_term in phone):
                found_customers.append((phone, customer))
                
        if not found_customers:
            print("❌ No customers found")
            return
            
        print(f"\n📋 Found {len(found_customers)} customers:")
        print("-" * 60)
        
        for phone, customer in found_customers:
            print(f"📱 {phone} | 👤 {customer['name']}")
            print(f"   💰 Total Purchases: ₹{customer['total_amount']:.2f}")
            print(f"   📅 Last Visit: {datetime.fromisoformat(customer['last_visit']).strftime('%Y-%m-%d')}")
            print()
            
        # Select customer for details
        if len(found_customers) == 1:
            self.view_customer_details(found_customers[0][0])
        else:
            phone_select = input("Enter phone number for details (or press Enter): ").strip()
            if phone_select and phone_select in self.shop.customers:
                self.view_customer_details(phone_select)
                
    def view_customer_details(self, phone):
        """View detailed customer information"""
        if phone not in self.shop.customers:
            print("❌ Customer not found")
            return
            
        customer = self.shop.customers[phone]
        
        print(f"\n👤 CUSTOMER DETAILS")
        print("=" * 40)
        print(f"Name: {customer['name']}")
        print(f"Phone: {phone}")
        print(f"Email: {customer.get('email', 'N/A')}")
        print(f"Address: {customer.get('address', 'N/A')}")
        print(f"Registration Date: {datetime.fromisoformat(customer['registration_date']).strftime('%Y-%m-%d')}")
        print(f"Total Purchases: ₹{customer['total_amount']:.2f}")
        print(f"Visit Count: {customer['visit_count']}")
        print(f"Last Visit: {datetime.fromisoformat(customer['last_visit']).strftime('%Y-%m-%d %H:%M')}")
        print(f"Customer Type: {customer.get('customer_type', 'Regular')}")
        
        if customer.get('notes'):
            print(f"Notes: {customer['notes']}")
            
        # Show purchase history
        self.show_customer_purchase_history(phone)
        
        # Customer actions
        print(f"\n📋 Customer Actions:")
        print("1. Edit customer")
        print("2. Add note")
        print("3. View detailed purchase history")
        print("4. Delete customer")
        print("0. Back to menu")
        
        choice = input("Select action (0-4): ").strip()
        
        if choice == '1':
            self.edit_customer(phone)
        elif choice == '2':
            self.add_customer_note(phone)
        elif choice == '3':
            self.detailed_purchase_history(phone)
        elif choice == '4':
            self.delete_customer(phone)
            
    def show_customer_purchase_history(self, phone):
        """Show recent purchase history"""
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            customer_sales = sales_df[sales_df['Customer_Phone'] == phone].tail(10)
            
            if len(customer_sales) == 0:
                print("\n📊 No purchase history found")
                return
                
            print(f"\n📊 Recent Purchases (Last 10):")
            print("-" * 60)
            
            for _, sale in customer_sales.iterrows():
                print(f"{sale['Date']} | {sale['Product_Name'][:25]:25} | Qty: {sale['Quantity_Sold']:2} | ₹{sale['Final_Amount']:6.2f}")
                
        except Exception as e:
            print(f"❌ Error loading purchase history: {e}")
            
    def detailed_purchase_history(self, phone):
        """Show detailed purchase history with analytics"""
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            customer_sales = sales_df[sales_df['Customer_Phone'] == phone]
            
            if len(customer_sales) == 0:
                print("\n📊 No purchase history found")
                return
                
            print(f"\n📊 DETAILED PURCHASE HISTORY")
            print("=" * 60)
            
            # Summary statistics
            total_transactions = customer_sales['Transaction_ID'].nunique()
            total_amount = customer_sales['Final_Amount'].sum()
            total_items = customer_sales['Quantity_Sold'].sum()
            avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
            
            print(f"Total Transactions: {total_transactions}")
            print(f"Total Amount: ₹{total_amount:.2f}")
            print(f"Total Items Purchased: {total_items}")
            print(f"Average Transaction: ₹{avg_transaction:.2f}")
            
            # Most purchased products
            print(f"\n📈 Top Purchased Products:")
            top_products = customer_sales.groupby('Product_Name').agg({
                'Quantity_Sold': 'sum',
                'Final_Amount': 'sum'
            }).sort_values('Quantity_Sold', ascending=False).head(10)
            
            for product, data in top_products.iterrows():
                print(f"  {product[:30]:30} | Qty: {data['Quantity_Sold']:3} | Amount: ₹{data['Final_Amount']:6.2f}")
                
            # Monthly spending pattern
            customer_sales['Year_Month'] = customer_sales['Date'].str[:7]
            monthly_spending = customer_sales.groupby('Year_Month')['Final_Amount'].sum()
            
            print(f"\n📅 Monthly Spending Pattern:")
            for month, amount in monthly_spending.tail(6).items():
                print(f"  {month}: ₹{amount:.2f}")
                
            # Save detailed report
            save_report = input("\n💾 Save detailed report? (y/n): ").strip().lower()
            if save_report == 'y':
                filename = f"customer_report_{phone}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                filepath = os.path.join(self.shop.data_dir, filename)
                
                with pd.ExcelWriter(filepath) as writer:
                    customer_sales.to_excel(writer, sheet_name='All_Purchases', index=False)
                    top_products.to_excel(writer, sheet_name='Top_Products')
                    monthly_spending.to_excel(writer, sheet_name='Monthly_Spending')
                    
                print(f"✅ Report saved: {filename}")
                
        except Exception as e:
            print(f"❌ Error generating detailed history: {e}")
            
    def edit_customer(self, phone):
        """Edit customer information"""
        customer = self.shop.customers[phone]
        
        print(f"\n✏️  EDIT CUSTOMER")
        print("=" * 30)
        
        print("Leave blank to keep current value")
        
        name = input(f"Name ({customer['name']}): ").strip()
        if name:
            customer['name'] = name
            
        email = input(f"Email ({customer.get('email', 'N/A')}): ").strip()
        if email:
            customer['email'] = email
            
        address = input(f"Address ({customer.get('address', 'N/A')}): ").strip()
        if address:
            customer['address'] = address
            
        # Customer type
        print(f"\nCustomer Type Options:")
        print("1. Regular")
        print("2. VIP")
        print("3. Wholesale")
        print("4. Credit")
        
        type_choice = input(f"Select type (current: {customer.get('customer_type', 'Regular')}): ").strip()
        types = {'1': 'Regular', '2': 'VIP', '3': 'Wholesale', '4': 'Credit'}
        if type_choice in types:
            customer['customer_type'] = types[type_choice]
            
        self.shop.save_customers()
        print("✅ Customer updated successfully!")
        
    def add_customer_note(self, phone):
        """Add note to customer"""
        note = input("Enter note: ").strip()
        
        if note:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            existing_notes = self.shop.customers[phone].get('notes', '')
            
            if existing_notes:
                new_notes = f"{existing_notes}\n[{current_time}] {note}"
            else:
                new_notes = f"[{current_time}] {note}"
                
            self.shop.customers[phone]['notes'] = new_notes
            self.shop.save_customers()
            
            print("✅ Note added successfully!")
            
    def delete_customer(self, phone):
        """Delete customer"""
        customer = self.shop.customers[phone]
        
        print(f"\n🗑️  DELETE CUSTOMER")
        print(f"Customer: {customer['name']} ({phone})")
        print(f"Total Purchases: ₹{customer['total_amount']:.2f}")
        
        confirm = input("Are you sure you want to delete this customer? (type 'DELETE'): ")
        
        if confirm == 'DELETE':
            del self.shop.customers[phone]
            self.shop.save_customers()
            print("✅ Customer deleted successfully!")
        else:
            print("❌ Deletion cancelled")
            
    def customer_loyalty_program(self):
        """Manage customer loyalty program"""
        print("\n🎁 CUSTOMER LOYALTY PROGRAM")
        print("=" * 40)
        
        print("1. View loyalty points")
        print("2. Add loyalty points")
        print("3. Redeem loyalty points")
        print("4. Loyalty program settings")
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == '1':
            self.view_loyalty_points()
        elif choice == '2':
            self.add_loyalty_points()
        elif choice == '3':
            self.redeem_loyalty_points()
        elif choice == '4':
            self.loyalty_program_settings()
            
    def view_loyalty_points(self):
        """View customer loyalty points"""
        phone = input("Enter customer phone: ").strip()
        
        if phone not in self.shop.customers:
            print("❌ Customer not found")
            return
            
        customer = self.shop.customers[phone]
        points = customer.get('loyalty_points', 0)
        
        print(f"\n🎁 Loyalty Points for {customer['name']}")
        print(f"Current Points: {points}")
        print(f"Points Value: ₹{points * 0.1:.2f}")  # 1 point = ₹0.1
        
    def add_loyalty_points(self):
        """Add loyalty points to customer"""
        phone = input("Enter customer phone: ").strip()
        
        if phone not in self.shop.customers:
            print("❌ Customer not found")
            return
            
        try:
            points = int(input("Points to add: "))
            reason = input("Reason: ").strip() or "Manual addition"
            
            current_points = self.shop.customers[phone].get('loyalty_points', 0)
            new_points = current_points + points
            
            self.shop.customers[phone]['loyalty_points'] = new_points
            self.shop.save_customers()
            
            print(f"✅ Added {points} points")
            print(f"Total points: {new_points}")
            
        except ValueError:
            print("❌ Invalid points value")
            
    def redeem_loyalty_points(self):
        """Redeem customer loyalty points"""
        phone = input("Enter customer phone: ").strip()
        
        if phone not in self.shop.customers:
            print("❌ Customer not found")
            return
            
        customer = self.shop.customers[phone]
        current_points = customer.get('loyalty_points', 0)
        
        if current_points == 0:
            print("❌ No points to redeem")
            return
            
        print(f"Available points: {current_points}")
        print(f"Redemption value: ₹{current_points * 0.1:.2f}")
        
        try:
            points_to_redeem = int(input("Points to redeem: "))
            
            if points_to_redeem > current_points:
                print("❌ Insufficient points")
                return
                
            redemption_value = points_to_redeem * 0.1
            
            print(f"Redemption value: ₹{redemption_value:.2f}")
            confirm = input("Confirm redemption? (y/n): ").strip().lower()
            
            if confirm == 'y':
                new_points = current_points - points_to_redeem
                self.shop.customers[phone]['loyalty_points'] = new_points
                self.shop.save_customers()
                
                print(f"✅ Redeemed {points_to_redeem} points for ₹{redemption_value:.2f}")
                print(f"Remaining points: {new_points}")
                
        except ValueError:
            print("❌ Invalid points value")
            
    def customer_analytics(self):
        """Customer analytics and insights"""
        print("\n📊 CUSTOMER ANALYTICS")
        print("=" * 40)
        
        try:
            # Load sales data
            sales_df = pd.read_csv(self.shop.sales_file)
            
            if len(sales_df) == 0:
                print("No sales data available")
                return
                
            # Customer statistics
            total_customers = len(self.shop.customers)
            customers_with_purchases = sales_df['Customer_Phone'].nunique()
            
            print(f"📋 Customer Statistics:")
            print(f"Total Registered Customers: {total_customers}")
            print(f"Customers with Purchases: {customers_with_purchases}")
            
            # Top customers by amount
            print(f"\n💰 Top Customers by Purchase Amount:")
            top_customers = sales_df.groupby('Customer_Phone').agg({
                'Final_Amount': 'sum',
                'Transaction_ID': 'nunique',
                'Customer_Name': 'first'
            }).sort_values('Final_Amount', ascending=False).head(10)
            
            for phone, data in top_customers.iterrows():
                if phone in self.shop.customers:
                    print(f"  {data['Customer_Name'][:20]:20} | ₹{data['Final_Amount']:8,.0f} | {data['Transaction_ID']:3} transactions")
                    
            # Customer segmentation
            print(f"\n🎯 Customer Segmentation:")
            customer_totals = sales_df.groupby('Customer_Phone')['Final_Amount'].sum()
            
            high_value = len(customer_totals[customer_totals >= 10000])
            medium_value = len(customer_totals[(customer_totals >= 2000) & (customer_totals < 10000)])
            low_value = len(customer_totals[customer_totals < 2000])
            
            print(f"  High Value (≥₹10,000): {high_value} customers")
            print(f"  Medium Value (₹2,000-₹10,000): {medium_value} customers")
            print(f"  Low Value (<₹2,000): {low_value} customers")
            
            # Recent customer activity
            print(f"\n📅 Recent Customer Activity:")
            sales_df['Date'] = pd.to_datetime(sales_df['Date'])
            last_30_days = sales_df[sales_df['Date'] >= (datetime.now() - timedelta(days=30))]
            
            active_customers_30d = last_30_days['Customer_Phone'].nunique()
            new_customers_30d = 0
            
            for phone, customer in self.shop.customers.items():
                reg_date = datetime.fromisoformat(customer['registration_date'])
                if reg_date >= (datetime.now() - timedelta(days=30)):
                    new_customers_30d += 1
                    
            print(f"  Active in Last 30 Days: {active_customers_30d}")
            print(f"  New Registrations (30 days): {new_customers_30d}")
            
            # Customer lifetime value
            print(f"\n💎 Customer Lifetime Value:")
            avg_customer_value = customer_totals.mean()
            median_customer_value = customer_totals.median()
            
            print(f"  Average Customer Value: ₹{avg_customer_value:.2f}")
            print(f"  Median Customer Value: ₹{median_customer_value:.2f}")
            
        except Exception as e:
            print(f"❌ Error generating analytics: {e}")
            
    def export_customer_data(self):
        """Export customer data"""
        print("\n💾 EXPORT CUSTOMER DATA")
        print("=" * 30)
        
        print("Export options:")
        print("1. All customers (basic info)")
        print("2. All customers with purchase history")
        print("3. VIP customers only")
        print("4. Customers with purchases last 30 days")
        
        choice = input("Select option (1-4): ").strip()
        
        try:
            # Create customer DataFrame
            customers_data = []
            for phone, customer in self.shop.customers.items():
                customers_data.append({
                    'Phone': phone,
                    'Name': customer['name'],
                    'Email': customer.get('email', ''),
                    'Address': customer.get('address', ''),
                    'Registration_Date': customer['registration_date'],
                    'Total_Amount': customer['total_amount'],
                    'Visit_Count': customer['visit_count'],
                    'Last_Visit': customer['last_visit'],
                    'Customer_Type': customer.get('customer_type', 'Regular'),
                    'Loyalty_Points': customer.get('loyalty_points', 0),
                    'Notes': customer.get('notes', '')
                })
                
            customers_df = pd.DataFrame(customers_data)
            
            if choice == '1':
                export_df = customers_df[['Phone', 'Name', 'Email', 'Address', 'Registration_Date']]
                filename = f"customers_basic_{datetime.now().strftime('%Y%m%d')}.csv"
            elif choice == '2':
                # Include purchase history
                filename = f"customers_complete_{datetime.now().strftime('%Y%m%d')}.xlsx"
            elif choice == '3':
                export_df = customers_df[customers_df['Customer_Type'] == 'VIP']
                filename = f"vip_customers_{datetime.now().strftime('%Y%m%d')}.csv"
            elif choice == '4':
                # Customers active in last 30 days
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                export_df = customers_df[customers_df['Last_Visit'] >= thirty_days_ago]
                filename = f"active_customers_30d_{datetime.now().strftime('%Y%m%d')}.csv"
            else:
                print("❌ Invalid option")
                return
                
            filepath = os.path.join(self.shop.data_dir, filename)
            
            if choice == '2':
                # Excel export with multiple sheets
                with pd.ExcelWriter(filepath) as writer:
                    customers_df.to_excel(writer, sheet_name='Customers', index=False)
                    
                    # Add purchase summary
                    sales_df = pd.read_csv(self.shop.sales_file)
                    purchase_summary = sales_df.groupby('Customer_Phone').agg({
                        'Final_Amount': 'sum',
                        'Transaction_ID': 'nunique',
                        'Date': ['min', 'max']
                    }).round(2)
                    purchase_summary.to_excel(writer, sheet_name='Purchase_Summary')
            else:
                export_df.to_csv(filepath, index=False)
                
            print(f"✅ Customer data exported: {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            
    def import_customers_from_file(self):
        """Import customers from CSV file"""
        print("\n📥 IMPORT CUSTOMERS")
        print("=" * 30)
        
        filename = input("Enter CSV filename: ").strip()
        filepath = os.path.join(self.shop.data_dir, filename)
        
        try:
            import_df = pd.read_csv(filepath)
            
            required_columns = ['Name', 'Phone']
            if not all(col in import_df.columns for col in required_columns):
                print(f"❌ CSV must have columns: {required_columns}")
                return
                
            imported_count = 0
            skipped_count = 0
            
            for _, row in import_df.iterrows():
                phone = str(row['Phone']).strip()
                name = str(row['Name']).strip()
                
                if phone in self.shop.customers:
                    skipped_count += 1
                    continue
                    
                customer_data = {
                    'name': name,
                    'phone': phone,
                    'email': row.get('Email', ''),
                    'address': row.get('Address', ''),
                    'registration_date': datetime.now().isoformat(),
                    'total_purchases': 0,
                    'total_amount': 0,
                    'last_visit': datetime.now().isoformat(),
                    'visit_count': 0,
                    'customer_type': row.get('Customer_Type', 'Regular'),
                    'notes': row.get('Notes', '')
                }
                
                self.shop.customers[phone] = customer_data
                imported_count += 1
                
            self.shop.save_customers()
            
            print(f"✅ Import completed!")
            print(f"📥 Imported: {imported_count} customers")
            print(f"⏭️  Skipped: {skipped_count} customers (already exist)")
            
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
        except Exception as e:
            print(f"❌ Error importing customers: {e}")
