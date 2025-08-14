import pandas as pd
import re
import os

class ReceiptFormatter:
    """A utility class for properly formatting receipts for 3-inch thermal printers"""
    
    @staticmethod
    def generate_receipt(transaction_id, sales_data_path, inventory_path):
        """Generate a properly formatted receipt for a 3-inch thermal printer"""
        try:
            # Load sales data and inventory data
            sales_df = pd.read_csv(sales_data_path)
            transaction_sales = sales_df[sales_df['Transaction_ID'] == transaction_id]
            
            if transaction_sales.empty:
                return "Receipt not found"
            
            # Load inventory for MRP lookup
            inventory_df = pd.read_csv(inventory_path)
            
            # Get transaction details
            first_row = transaction_sales.iloc[0]
            
            # Receipt width for 3-inch thermal printer
            receipt_width = 35
            
            # Function for centered text
            def center_text(text, width):
                if len(text) >= width:
                    return text
                padding = (width - len(text)) // 2
                return ' ' * padding + text + ' ' * (width - padding - len(text))
            
            receipt = "\n"  # Start with a blank line
            receipt += f"{center_text('BAUJI TRADERS', receipt_width)}\n"
            receipt += f"{center_text('CONFECTIONERY STORE', receipt_width)}\n"
            receipt += f"{'-'*receipt_width}\n"
            receipt += f"Address: 1690 30FT ROAD,\n"
            receipt += f"         JAWAHAR COLONY\n"
            receipt += f"Phone: 9911148114, 9555269666\n\n"
            
            receipt += f"TXN ID: {transaction_id}\n"
            receipt += f"Date: {first_row['Date']}\n"
            receipt += f"Time: {first_row['Time']}\n"
            
            # Only include customer info if available
            if first_row['Customer_Name'] and first_row['Customer_Name'].strip().lower() != 'none' and first_row['Customer_Name'].strip() != '':
                receipt += f"Customer: {first_row['Customer_Name']}\n"
                if first_row['Customer_Phone'] and str(first_row['Customer_Phone']).strip() != '':
                    receipt += f"Phone: {first_row['Customer_Phone']}\n"
            
            receipt += f"Payment: {first_row['Payment_Method']}\n"
            
            receipt += f"{'-'*receipt_width}\n"
            receipt += f"{center_text('ITEMS', receipt_width)}\n"
            receipt += f"{'-'*receipt_width}\n"
            
            # Item header - exactly as shown in the actual receipt
            receipt += "ITEM\n"
            receipt += f"{'-'*receipt_width}\n"
            receipt += "           QTY MRP D% PRICE TOTAL\n"
            receipt += f"{'-'*receipt_width}\n"
            
            total_amount = 0
            total_mrp_amount = 0
            
            for _, row in transaction_sales.iterrows():
                product_name = row['Product_Name']
                quantity = int(row['Quantity_Sold'])
                sell_price = float(row['Unit_Price'])
                
                # Find MRP from inventory
                product_info = inventory_df[inventory_df['Product_Name'] == product_name]
                if not product_info.empty:
                    mrp = float(product_info.iloc[0]['MRP'])
                else:
                    mrp = sell_price  # Fallback if product not found
                
                # Calculate discount percentage
                if mrp > 0:
                    discount_per_unit = mrp - sell_price
                    discount_percentage = (discount_per_unit / mrp) * 100
                else:
                    discount_percentage = 0
                
                item_total = quantity * sell_price
                mrp_total = quantity * mrp
                
                total_amount += item_total
                total_mrp_amount += mrp_total
                
                # Format item row exactly as in the actual receipt
                # Handle product names that can be long (like CHERRY LIQUID 135ML/-)
                receipt += f"{product_name}\n"
                
                # Format the quantity and price details with exact spacing as in receipt
                # Notice the specific spacing pattern in the original receipt
                receipt += f"           {quantity:>1} {int(mrp):>3} {int(discount_percentage):>2}  {int(sell_price):>3}   {int(item_total):>3}\n"
            
            total_savings = total_mrp_amount - total_amount
            
            # Apply any additional discount
            discount = float(first_row['Discount']) if first_row['Discount'] else 0
            additional_discount_amount = total_amount * (discount / 100)
            final_total = total_amount - additional_discount_amount
            total_savings += additional_discount_amount
            
            # Total section - exact format from the actual receipt
            receipt += f"{'-'*receipt_width}\n"
            # Use Rs symbol as seen in the actual receipt instead of ₹
            receipt += f"TOTAL:              ₹      {final_total:.2f}\n"
            receipt += f"{'-'*receipt_width}\n"
            
            # You saved - exact format from the actual receipt
            if total_savings > 0:
                receipt += f"You saved:           ₹       {total_savings:.2f}\n"
                receipt += f"{'-'*receipt_width}\n"
            
            # Thank you message - exact wording from the receipt
            receipt += f"\n{center_text('Thank you for shopping!', receipt_width)}\n"
            receipt += f"{center_text('Visit again soon!', receipt_width)}\n\n"
            
            # Add feed for printer cut
            receipt += "\n\n\n"
            
            return receipt
            
        except Exception as e:
            return f"Error generating receipt: {str(e)}"

# Example usage:
# receipt = ReceiptFormatter.generate_receipt("TXN20250814123456", "sales_transactions.csv", "inventory_master.csv")
