"""
📊 BAUJI TRADERS - REPORTS & ANALYTICS MODULE
============================================
Comprehensive reporting and business analytics functionality
"""

import pandas as pd
import os
from datetime import datetime, timedelta, date
import json
from collections import defaultdict

# Optional imports for advanced features
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

class ReportsAnalytics:
    def __init__(self, shop_manager):
        self.shop = shop_manager
        
    def daily_sales_report(self):
        """Generate daily sales report"""
        print("\n📊 DAILY SALES REPORT")
        print("=" * 40)
        
        # Date selection
        report_date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not report_date:
            report_date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            daily_sales = sales_df[sales_df['Date'] == report_date]
            
            if len(daily_sales) == 0:
                print(f"❌ No sales found for {report_date}")
                return
                
            # Summary metrics
            total_transactions = daily_sales['Transaction_ID'].nunique()
            total_revenue = daily_sales['Final_Amount'].sum()
            total_items = daily_sales['Quantity_Sold'].sum()
            total_discount = daily_sales['Discount'].sum()
            
            print(f"\n📋 Sales Summary for {report_date}")
            print("=" * 50)
            print(f"Total Transactions: {total_transactions}")
            print(f"Total Items Sold: {total_items}")
            print(f"Gross Revenue: ₹{(total_revenue + total_discount):.2f}")
            print(f"Total Discount: ₹{total_discount:.2f}")
            print(f"Net Revenue: ₹{total_revenue:.2f}")
            print(f"Average Transaction: ₹{total_revenue/total_transactions:.2f}")
            
            # Payment method breakdown
            payment_breakdown = daily_sales.groupby('Payment_Method')['Final_Amount'].sum()
            print(f"\n💳 Payment Method Breakdown:")
            for method, amount in payment_breakdown.items():
                percentage = (amount / total_revenue) * 100
                print(f"  {method}: ₹{amount:.2f} ({percentage:.1f}%)")
                
            # Top selling products
            print(f"\n📈 Top Selling Products:")
            top_products = daily_sales.groupby('Product_Name').agg({
                'Quantity_Sold': 'sum',
                'Final_Amount': 'sum'
            }).sort_values('Quantity_Sold', ascending=False).head(10)
            
            for product, data in top_products.iterrows():
                print(f"  {product[:30]:30} | Qty: {data['Quantity_Sold']:3} | Revenue: ₹{data['Final_Amount']:6,.0f}")
                
            # Hourly sales pattern
            daily_sales['Hour'] = daily_sales['Time'].str[:2].astype(int)
            hourly_sales = daily_sales.groupby('Hour')['Final_Amount'].sum()
            
            print(f"\n🕐 Hourly Sales Pattern:")
            for hour, amount in hourly_sales.items():
                print(f"  {hour:02d}:00 - {hour+1:02d}:00: ₹{amount:.2f}")
                
            # Customer analysis
            unique_customers = daily_sales['Customer_Phone'].nunique()
            walk_in_customers = len(daily_sales[daily_sales['Customer_Phone'] == ''])
            
            print(f"\n👥 Customer Analysis:")
            print(f"  Unique Customers: {unique_customers}")
            print(f"  Walk-in Customers: {walk_in_customers}")
            print(f"  Registered Customers: {unique_customers - (1 if walk_in_customers > 0 else 0)}")
            
            # Save report
            self.save_daily_report(report_date, daily_sales, {
                'total_transactions': total_transactions,
                'total_revenue': total_revenue,
                'total_items': total_items,
                'total_discount': total_discount
            })
            
        except Exception as e:
            print(f"❌ Error generating daily report: {e}")
            
    def weekly_sales_report(self):
        """Generate weekly sales report"""
        print("\n📊 WEEKLY SALES REPORT")
        print("=" * 40)
        
        # Date range selection
        end_date = input("Enter end date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            start_date_obj = end_date_obj - timedelta(days=6)
            start_date = start_date_obj.strftime('%Y-%m-%d')
            
            sales_df = pd.read_csv(self.shop.sales_file)
            weekly_sales = sales_df[(sales_df['Date'] >= start_date) & (sales_df['Date'] <= end_date)]
            
            if len(weekly_sales) == 0:
                print(f"❌ No sales found for week {start_date} to {end_date}")
                return
                
            print(f"\n📋 Weekly Sales Report ({start_date} to {end_date})")
            print("=" * 60)
            
            # Daily breakdown
            daily_totals = weekly_sales.groupby('Date').agg({
                'Transaction_ID': 'nunique',
                'Final_Amount': 'sum',
                'Quantity_Sold': 'sum'
            })
            
            print(f"📅 Daily Breakdown:")
            total_week_revenue = 0
            for date_str, data in daily_totals.iterrows():
                day_name = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
                print(f"  {date_str} ({day_name[:3]}): ₹{data['Final_Amount']:6,.0f} | {data['Transaction_ID']:3} txns | {data['Quantity_Sold']:4} items")
                total_week_revenue += data['Final_Amount']
                
            # Weekly summary
            total_transactions = weekly_sales['Transaction_ID'].nunique()
            total_items = weekly_sales['Quantity_Sold'].sum()
            avg_daily_revenue = total_week_revenue / 7
            
            print(f"\n📊 Weekly Summary:")
            print(f"Total Revenue: ₹{total_week_revenue:,.2f}")
            print(f"Total Transactions: {total_transactions}")
            print(f"Total Items Sold: {total_items}")
            print(f"Average Daily Revenue: ₹{avg_daily_revenue:,.2f}")
            
            # Best and worst days
            best_day = daily_totals.loc[daily_totals['Final_Amount'].idxmax()]
            worst_day = daily_totals.loc[daily_totals['Final_Amount'].idxmin()]
            
            print(f"\n🏆 Best Day: {daily_totals['Final_Amount'].idxmax()} - ₹{best_day['Final_Amount']:,.2f}")
            print(f"📉 Worst Day: {daily_totals['Final_Amount'].idxmin()} - ₹{worst_day['Final_Amount']:,.2f}")
            
            # Product performance
            print(f"\n📈 Top Products This Week:")
            weekly_products = weekly_sales.groupby('Product_Name').agg({
                'Quantity_Sold': 'sum',
                'Final_Amount': 'sum'
            }).sort_values('Final_Amount', ascending=False).head(15)
            
            for product, data in weekly_products.iterrows():
                print(f"  {product[:35]:35} | Qty: {data['Quantity_Sold']:3} | Revenue: ₹{data['Final_Amount']:6,.0f}")
                
        except Exception as e:
            print(f"❌ Error generating weekly report: {e}")
            
    def monthly_sales_report(self):
        """Generate monthly sales report"""
        print("\n📊 MONTHLY SALES REPORT")
        print("=" * 40)
        
        # Month selection
        month_input = input("Enter month (YYYY-MM) or press Enter for current month: ").strip()
        if not month_input:
            month_input = datetime.now().strftime('%Y-%m')
            
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            monthly_sales = sales_df[sales_df['Date'].str.startswith(month_input)]
            
            if len(monthly_sales) == 0:
                print(f"❌ No sales found for {month_input}")
                return
                
            print(f"\n📋 Monthly Sales Report for {month_input}")
            print("=" * 50)
            
            # Monthly summary
            total_revenue = monthly_sales['Final_Amount'].sum()
            total_transactions = monthly_sales['Transaction_ID'].nunique()
            total_items = monthly_sales['Quantity_Sold'].sum()
            total_customers = monthly_sales['Customer_Phone'].nunique()
            
            # Calculate days in month for averages
            year, month = map(int, month_input.split('-'))
            days_in_month = (date(year, month + 1, 1) - date(year, month, 1)).days if month < 12 else (date(year + 1, 1, 1) - date(year, month, 1)).days
            
            print(f"Total Revenue: ₹{total_revenue:,.2f}")
            print(f"Total Transactions: {total_transactions}")
            print(f"Total Items Sold: {total_items}")
            print(f"Unique Customers: {total_customers}")
            print(f"Average Daily Revenue: ₹{total_revenue/days_in_month:,.2f}")
            print(f"Average Transaction Value: ₹{total_revenue/total_transactions:.2f}")
            
            # Weekly breakdown within month
            monthly_sales['Week'] = pd.to_datetime(monthly_sales['Date']).dt.isocalendar().week
            weekly_breakdown = monthly_sales.groupby('Week')['Final_Amount'].sum()
            
            print(f"\n📅 Weekly Breakdown:")
            for week, revenue in weekly_breakdown.items():
                print(f"  Week {week}: ₹{revenue:,.2f}")
                
            # Category performance
            print(f"\n🏷️  Category Performance:")
            
            # Join with inventory to get categories
            inventory_categories = self.shop.inventory[['Product_Name', 'Category']].drop_duplicates()
            monthly_with_categories = monthly_sales.merge(inventory_categories, on='Product_Name', how='left')
            
            category_performance = monthly_with_categories.groupby('Category').agg({
                'Final_Amount': 'sum',
                'Quantity_Sold': 'sum'
            }).sort_values('Final_Amount', ascending=False)
            
            for category, data in category_performance.iterrows():
                percentage = (data['Final_Amount'] / total_revenue) * 100
                print(f"  {category[:20]:20} | Revenue: ₹{data['Final_Amount']:8,.0f} ({percentage:4.1f}%) | Qty: {data['Quantity_Sold']:4}")
                
            # Top customers of the month
            print(f"\n👑 Top Customers:")
            top_customers = monthly_sales.groupby(['Customer_Phone', 'Customer_Name']).agg({
                'Final_Amount': 'sum',
                'Transaction_ID': 'nunique'
            }).sort_values('Final_Amount', ascending=False).head(10)
            
            for (phone, name), data in top_customers.iterrows():
                if phone:  # Skip empty phone numbers
                    print(f"  {name[:25]:25} | ₹{data['Final_Amount']:6,.0f} | {data['Transaction_ID']:2} visits")
                    
        except Exception as e:
            print(f"❌ Error generating monthly report: {e}")
            
    def profit_analysis_report(self):
        """Detailed profit analysis"""
        print("\n💰 PROFIT ANALYSIS REPORT")
        print("=" * 40)
        
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            
            if len(sales_df) == 0:
                print("❌ No sales data available")
                return
                
            # Join sales with inventory to get cost prices
            inventory_costs = self.shop.inventory[['Product_Name', 'Cost_Price']].drop_duplicates()
            sales_with_costs = sales_df.merge(inventory_costs, on='Product_Name', how='left')
            
            # Calculate profit for each sale
            sales_with_costs['Cost_Total'] = sales_with_costs['Quantity_Sold'] * sales_with_costs['Cost_Price']
            sales_with_costs['Profit'] = sales_with_costs['Final_Amount'] - sales_with_costs['Cost_Total']
            sales_with_costs['Profit_Margin'] = (sales_with_costs['Profit'] / sales_with_costs['Final_Amount']) * 100
            
            # Overall profit summary
            total_revenue = sales_with_costs['Final_Amount'].sum()
            total_cost = sales_with_costs['Cost_Total'].sum()
            total_profit = sales_with_costs['Profit'].sum()
            overall_margin = (total_profit / total_revenue) * 100
            
            print(f"📊 Overall Profit Summary:")
            print(f"Total Revenue: ₹{total_revenue:,.2f}")
            print(f"Total Cost: ₹{total_cost:,.2f}")
            print(f"Total Profit: ₹{total_profit:,.2f}")
            print(f"Overall Margin: {overall_margin:.2f}%")
            
            # Most profitable products
            print(f"\n🏆 Most Profitable Products:")
            product_profits = sales_with_costs.groupby('Product_Name').agg({
                'Final_Amount': 'sum',
                'Cost_Total': 'sum',
                'Profit': 'sum',
                'Quantity_Sold': 'sum'
            })
            product_profits['Margin_%'] = (product_profits['Profit'] / product_profits['Final_Amount']) * 100
            top_profitable = product_profits.sort_values('Profit', ascending=False).head(15)
            
            for product, data in top_profitable.iterrows():
                print(f"  {product[:30]:30} | Profit: ₹{data['Profit']:6,.0f} | Margin: {data['Margin_%']:5.1f}% | Qty: {data['Quantity_Sold']:3}")
                
            # Least profitable products
            print(f"\n📉 Least Profitable Products:")
            least_profitable = product_profits.sort_values('Profit', ascending=True).head(10)
            
            for product, data in least_profitable.iterrows():
                print(f"  {product[:30]:30} | Profit: ₹{data['Profit']:6,.0f} | Margin: {data['Margin_%']:5.1f}% | Qty: {data['Quantity_Sold']:3}")
                
            # Monthly profit trend
            print(f"\n📈 Monthly Profit Trend:")
            sales_with_costs['Year_Month'] = sales_with_costs['Date'].str[:7]
            monthly_profits = sales_with_costs.groupby('Year_Month').agg({
                'Final_Amount': 'sum',
                'Cost_Total': 'sum',
                'Profit': 'sum'
            })
            monthly_profits['Margin_%'] = (monthly_profits['Profit'] / monthly_profits['Final_Amount']) * 100
            
            for month, data in monthly_profits.tail(12).iterrows():
                print(f"  {month}: Revenue ₹{data['Final_Amount']:6,.0f} | Profit ₹{data['Profit']:6,.0f} | Margin {data['Margin_%']:5.1f}%")
                
        except Exception as e:
            print(f"❌ Error generating profit analysis: {e}")
            
    def inventory_turnover_report(self):
        """Inventory turnover analysis"""
        print("\n🔄 INVENTORY TURNOVER REPORT")
        print("=" * 40)
        
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            
            # Calculate turnover for last 30, 60, 90 days
            periods = [30, 60, 90]
            
            for period in periods:
                print(f"\n📊 {period}-Day Turnover Analysis:")
                print("-" * 40)
                
                cutoff_date = (datetime.now() - timedelta(days=period)).strftime('%Y-%m-%d')
                period_sales = sales_df[sales_df['Date'] >= cutoff_date]
                
                # Product sales in period
                product_sales = period_sales.groupby('Product_Name')['Quantity_Sold'].sum()
                
                # Join with current inventory
                turnover_data = []
                for _, product in self.shop.inventory.iterrows():
                    product_name = product['Product_Name']
                    current_stock = product['Quantity']
                    sold_quantity = product_sales.get(product_name, 0)
                    
                    if current_stock > 0:
                        turnover_ratio = sold_quantity / current_stock
                        days_of_stock = current_stock / (sold_quantity / period) if sold_quantity > 0 else float('inf')
                    else:
                        turnover_ratio = float('inf') if sold_quantity > 0 else 0
                        days_of_stock = 0
                        
                    turnover_data.append({
                        'Product_Name': product_name,
                        'Current_Stock': current_stock,
                        'Sold_Quantity': sold_quantity,
                        'Turnover_Ratio': turnover_ratio,
                        'Days_of_Stock': days_of_stock if days_of_stock != float('inf') else 999
                    })
                
                turnover_df = pd.DataFrame(turnover_data)
                
                # Fast moving products
                fast_moving = turnover_df.sort_values('Turnover_Ratio', ascending=False).head(10)
                print(f"🚀 Fast Moving Products ({period} days):")
                for _, item in fast_moving.iterrows():
                    print(f"  {item['Product_Name'][:30]:30} | Ratio: {item['Turnover_Ratio']:4.2f} | Stock: {item['Current_Stock']:3} | Sold: {item['Sold_Quantity']:3}")
                
                # Slow moving products
                slow_moving = turnover_df[turnover_df['Sold_Quantity'] > 0].sort_values('Turnover_Ratio', ascending=True).head(10)
                print(f"\n🐌 Slow Moving Products ({period} days):")
                for _, item in slow_moving.iterrows():
                    print(f"  {item['Product_Name'][:30]:30} | Ratio: {item['Turnover_Ratio']:4.2f} | Stock: {item['Current_Stock']:3} | Sold: {item['Sold_Quantity']:3}")
                
                # Dead stock
                dead_stock = turnover_df[turnover_df['Sold_Quantity'] == 0]
                if len(dead_stock) > 0:
                    print(f"\n💀 Dead Stock ({period} days) - {len(dead_stock)} items:")
                    for _, item in dead_stock.head(10).iterrows():
                        print(f"  {item['Product_Name'][:30]:30} | Stock: {item['Current_Stock']:3}")
                        
        except Exception as e:
            print(f"❌ Error generating turnover report: {e}")
            
    def customer_analysis_report(self):
        """Detailed customer analysis"""
        print("\n👥 CUSTOMER ANALYSIS REPORT")
        print("=" * 40)
        
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            
            # Customer segmentation analysis
            customer_totals = sales_df.groupby('Customer_Phone').agg({
                'Final_Amount': 'sum',
                'Transaction_ID': 'nunique',
                'Date': ['min', 'max'],
                'Customer_Name': 'first'
            })
            
            # Flatten column names
            customer_totals.columns = ['Total_Spent', 'Visit_Count', 'First_Visit', 'Last_Visit', 'Customer_Name']
            
            # Calculate customer lifetime value segments
            high_value = customer_totals[customer_totals['Total_Spent'] >= 10000]
            medium_value = customer_totals[(customer_totals['Total_Spent'] >= 2000) & (customer_totals['Total_Spent'] < 10000)]
            low_value = customer_totals[customer_totals['Total_Spent'] < 2000]
            
            print(f"📊 Customer Segmentation:")
            print(f"High Value (≥₹10,000): {len(high_value)} customers - ₹{high_value['Total_Spent'].sum():,.0f} total")
            print(f"Medium Value (₹2,000-₹10,000): {len(medium_value)} customers - ₹{medium_value['Total_Spent'].sum():,.0f} total")
            print(f"Low Value (<₹2,000): {len(low_value)} customers - ₹{low_value['Total_Spent'].sum():,.0f} total")
            
            # RFM Analysis (Recency, Frequency, Monetary)
            print(f"\n📈 RFM Analysis:")
            
            # Calculate recency (days since last purchase)
            today = datetime.now()
            customer_totals['Recency'] = (today - pd.to_datetime(customer_totals['Last_Visit'])).dt.days
            
            # Frequency is visit count
            customer_totals['Frequency'] = customer_totals['Visit_Count']
            
            # Monetary is total spent
            customer_totals['Monetary'] = customer_totals['Total_Spent']
            
            # Create RFM scores (1-5 scale)
            customer_totals['R_Score'] = pd.qcut(customer_totals['Recency'].rank(method='first'), 5, labels=[5,4,3,2,1])
            customer_totals['F_Score'] = pd.qcut(customer_totals['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
            customer_totals['M_Score'] = pd.qcut(customer_totals['Monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
            
            # Combine RFM scores
            customer_totals['RFM_Score'] = customer_totals['R_Score'].astype(str) + customer_totals['F_Score'].astype(str) + customer_totals['M_Score'].astype(str)
            
            # Customer segments based on RFM
            def rfm_segment(row):
                if row['RFM_Score'] in ['555', '554', '544', '545', '454', '455', '445']:
                    return 'Champions'
                elif row['RFM_Score'] in ['543', '444', '435', '355', '354', '345', '344', '335']:
                    return 'Loyal Customers'
                elif row['RFM_Score'] in ['512', '511', '422', '421', '412', '411', '311']:
                    return 'New Customers'
                elif row['RFM_Score'] in ['533', '532', '531', '523', '522', '521', '515', '514', '513', '425', '424', '413', '414', '415', '315', '314', '313']:
                    return 'Potential Loyalists'
                elif row['RFM_Score'] in ['155', '154', '144', '214', '215', '115', '114']:
                    return 'At Risk'
                elif row['RFM_Score'] in ['111', '112', '121', '131', '141', '151']:
                    return 'Lost Customers'
                else:
                    return 'Others'
            
            customer_totals['Segment'] = customer_totals.apply(rfm_segment, axis=1)
            
            # Segment analysis
            segment_analysis = customer_totals.groupby('Segment').agg({
                'Total_Spent': ['count', 'sum', 'mean'],
                'Frequency': 'mean',
                'Recency': 'mean'
            }).round(2)
            
            print("\n🎯 Customer Segments:")
            for segment in segment_analysis.index:
                count = segment_analysis.loc[segment, ('Total_Spent', 'count')]
                total_value = segment_analysis.loc[segment, ('Total_Spent', 'sum')]
                avg_value = segment_analysis.loc[segment, ('Total_Spent', 'mean')]
                avg_frequency = segment_analysis.loc[segment, ('Frequency', 'mean')]
                avg_recency = segment_analysis.loc[segment, ('Recency', 'mean')]
                
                print(f"  {segment:20} | {count:3} customers | Total: ₹{total_value:8,.0f} | Avg: ₹{avg_value:6,.0f} | Freq: {avg_frequency:4.1f} | Recency: {avg_recency:3.0f} days")
                
        except Exception as e:
            print(f"❌ Error generating customer analysis: {e}")
            
    def save_daily_report(self, report_date, sales_data, summary):
        """Save daily report to file"""
        try:
            filename = f"daily_report_{report_date}.xlsx"
            filepath = os.path.join(self.shop.data_dir, filename)
            
            with pd.ExcelWriter(filepath) as writer:
                # Summary sheet
                summary_df = pd.DataFrame([summary])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Detailed sales
                sales_data.to_excel(writer, sheet_name='Detailed_Sales', index=False)
                
                # Product summary
                product_summary = sales_data.groupby('Product_Name').agg({
                    'Quantity_Sold': 'sum',
                    'Final_Amount': 'sum'
                }).sort_values('Quantity_Sold', ascending=False)
                product_summary.to_excel(writer, sheet_name='Product_Summary')
                
            print(f"✅ Daily report saved: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            
    def custom_date_range_report(self):
        """Generate report for custom date range"""
        print("\n📊 CUSTOM DATE RANGE REPORT")
        print("=" * 40)
        
        start_date = input("Start date (YYYY-MM-DD): ").strip()
        end_date = input("End date (YYYY-MM-DD): ").strip()
        
        if not start_date or not end_date:
            print("❌ Both dates are required")
            return
            
        try:
            sales_df = pd.read_csv(self.shop.sales_file)
            range_sales = sales_df[(sales_df['Date'] >= start_date) & (sales_df['Date'] <= end_date)]
            
            if len(range_sales) == 0:
                print(f"❌ No sales found for {start_date} to {end_date}")
                return
                
            # Generate comprehensive report for date range
            print(f"\n📋 Sales Report: {start_date} to {end_date}")
            print("=" * 60)
            
            # Basic metrics
            total_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days + 1
            total_revenue = range_sales['Final_Amount'].sum()
            total_transactions = range_sales['Transaction_ID'].nunique()
            total_items = range_sales['Quantity_Sold'].sum()
            
            print(f"Period: {total_days} days")
            print(f"Total Revenue: ₹{total_revenue:,.2f}")
            print(f"Total Transactions: {total_transactions}")
            print(f"Total Items Sold: {total_items}")
            print(f"Average Daily Revenue: ₹{total_revenue/total_days:,.2f}")
            
            # Save comprehensive report
            save_report = input("\n💾 Save detailed report? (y/n): ").strip().lower()
            if save_report == 'y':
                filename = f"custom_report_{start_date}_to_{end_date}.xlsx"
                filepath = os.path.join(self.shop.data_dir, filename)
                
                with pd.ExcelWriter(filepath) as writer:
                    range_sales.to_excel(writer, sheet_name='Sales_Data', index=False)
                    
                    # Daily summary
                    daily_summary = range_sales.groupby('Date').agg({
                        'Transaction_ID': 'nunique',
                        'Final_Amount': 'sum',
                        'Quantity_Sold': 'sum'
                    })
                    daily_summary.to_excel(writer, sheet_name='Daily_Summary')
                    
                    # Product summary
                    product_summary = range_sales.groupby('Product_Name').agg({
                        'Quantity_Sold': 'sum',
                        'Final_Amount': 'sum'
                    }).sort_values('Final_Amount', ascending=False)
                    product_summary.to_excel(writer, sheet_name='Product_Summary')
                    
                print(f"✅ Report saved: {filename}")
                
        except Exception as e:
            print(f"❌ Error generating custom report: {e}")
            
    def export_all_reports(self):
        """Export all reports in one go"""
        print("\n📁 EXPORT ALL REPORTS")
        print("=" * 30)
        
        export_date = datetime.now().strftime('%Y%m%d')
        
        try:
            # Create comprehensive report package
            filename = f"bauji_traders_complete_reports_{export_date}.xlsx"
            filepath = os.path.join(self.shop.data_dir, filename)
            
            with pd.ExcelWriter(filepath) as writer:
                # Current inventory
                self.shop.inventory.to_excel(writer, sheet_name='Current_Inventory', index=False)
                
                # Sales data
                sales_df = pd.read_csv(self.shop.sales_file)
                sales_df.to_excel(writer, sheet_name='All_Sales', index=False)
                
                # Customer data
                customers_data = []
                for phone, customer in self.shop.customers.items():
                    customers_data.append({
                        'Phone': phone,
                        'Name': customer['name'],
                        'Total_Amount': customer['total_amount'],
                        'Visit_Count': customer['visit_count'],
                        'Registration_Date': customer['registration_date'],
                        'Customer_Type': customer.get('customer_type', 'Regular')
                    })
                pd.DataFrame(customers_data).to_excel(writer, sheet_name='Customers', index=False)
                
                # Stock movements
                stock_df = pd.read_csv(self.shop.stock_movements_file)
                stock_df.to_excel(writer, sheet_name='Stock_Movements', index=False)
                
                # Summary analytics
                summary_data = {
                    'Metric': [
                        'Total Products',
                        'Total Stock Value',
                        'Total Customers',
                        'Total Sales Revenue',
                        'Total Transactions'
                    ],
                    'Value': [
                        len(self.shop.inventory),
                        (self.shop.inventory['Quantity'] * self.shop.inventory['Cost_Price']).sum(),
                        len(self.shop.customers),
                        sales_df['Final_Amount'].sum(),
                        sales_df['Transaction_ID'].nunique()
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Business_Summary', index=False)
                
            print(f"✅ Complete reports exported: {filename}")
            print(f"📊 Includes: Inventory, Sales, Customers, Stock Movements, Summary")
            
        except Exception as e:
            print(f"❌ Error exporting reports: {e}")
