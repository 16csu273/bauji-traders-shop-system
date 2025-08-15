"""
HTML Receipt Generator for Bauji Traders
========================================
Generates HTML receipts using the invoice template
"""

import pandas as pd
import os
from datetime import datetime
import webbrowser
import tempfile

class HTMLReceiptGenerator:
    def __init__(self, sales_file, inventory_file):
        self.sales_file = sales_file
        self.inventory_file = inventory_file
        
    def generate_receipt_html(self, transaction_id):
        """Generate HTML receipt for a given transaction ID"""
        try:
            # Load transaction data
            sales_df = pd.read_csv(self.sales_file)
            transaction_sales = sales_df[sales_df['Transaction_ID'] == transaction_id]
            
            if transaction_sales.empty:
                return None, "Transaction not found"
            
            # Load inventory for MRP lookup
            inventory_df = pd.read_csv(self.inventory_file)
            
            # Get transaction details
            first_row = transaction_sales.iloc[0]
            
            # Calculate totals
            subtotal = 0
            total_discount = 0
            total_savings = 0
            total_mrp_amount = 0  # Track total MRP for correct savings percentage
            
            # Build items HTML
            items_html = ""
            for _, row in transaction_sales.iterrows():
                product_name = row['Product_Name']
                quantity = int(row['Quantity_Sold'])
                unit_price = float(row['Unit_Price'])
                line_total = float(row['Total_Amount'])
                
                # Find MRP from inventory
                product_info = inventory_df[inventory_df['Product_Name'] == product_name]
                if not product_info.empty:
                    mrp = float(product_info.iloc[0]['MRP'])
                else:
                    mrp = unit_price
                
                # Calculate discount percentage
                if mrp > 0:
                    discount_per_unit = mrp - unit_price
                    discount_percentage = (discount_per_unit / mrp) * 100
                    item_savings = discount_per_unit * quantity
                else:
                    discount_percentage = 0
                    item_savings = 0
                
                # Calculate MRP total for this item
                mrp_line_total = mrp * quantity
                
                subtotal += line_total
                total_savings += item_savings
                total_mrp_amount += mrp_line_total
                
                # Split product name and size if needed for better display
                product_display = product_name
                size_info = ""
                
                # Try to extract size info (like 200ML, 1KG, etc.)
                import re
                size_match = re.search(r'(\d+\s*(?:ML|GM|G|KG|L|MG))', product_name, re.IGNORECASE)
                if size_match:
                    size_info = size_match.group(1)
                    product_display = product_name.replace(size_match.group(1), '').strip()
                
                # Handle long product names by wrapping to next line
                if len(product_display) > 20:
                    # Split into two lines for better formatting
                    first_part = product_display[:20].strip()
                    second_part = product_display[20:].strip()
                    if second_part:
                        product_html = f"{first_part}<br><span style='font-size:9px;'>{second_part}</span>"
                    else:
                        product_html = first_part
                    if size_info:
                        product_html += f"<br><span style='font-size:9px;'>{size_info}</span>"
                else:
                    product_html = product_display
                    if size_info:
                        product_html += f"<br><span style='font-size:9px;'>{size_info}</span>"
                
                # Create item row HTML
                items_html += f"""
    <tr>
      <td>{product_html}</td>
      <td class="right">{quantity}</td>
      <td class="right">{mrp:.0f}</td>
      <td class="right">{discount_percentage:.1f}</td>
      <td class="right">{unit_price:.0f}</td>
      <td class="right">{line_total:.0f}</td>
    </tr>"""
            
            # Calculate final totals
            additional_discount = 0
            if 'Discount' in first_row and first_row['Discount'] and str(first_row['Discount']).strip() not in ['', 'nan', 'NaN', 'None']:
                try:
                    additional_discount = float(first_row['Discount'])
                except (ValueError, TypeError):
                    additional_discount = 0
            
            if additional_discount > 0:
                discount_amount = subtotal * (additional_discount / 100)
                total_savings += discount_amount
                final_total = subtotal - discount_amount
            else:
                final_total = subtotal
            
            # Customer info
            customer_name = str(first_row['Customer_Name']) if first_row['Customer_Name'] and str(first_row['Customer_Name']).strip().lower() not in ['none', 'nan', ''] else "Walk-in Customer"
            customer_phone = str(first_row['Customer_Phone']) if first_row['Customer_Phone'] and str(first_row['Customer_Phone']).strip() not in ['none', 'nan', ''] else ""
            
            # Payment method
            payment_method = str(first_row['Payment_Method'])
            
            # Date and time
            transaction_date = str(first_row['Date'])
            transaction_time = str(first_row['Time'])
            datetime_str = f"{transaction_date} {transaction_time}"
            
            # Generate HTML using template
            html_content = self.get_html_template()
            
            # Replace placeholders
            html_content = html_content.replace('{{DATETIME}}', str(datetime_str))
            html_content = html_content.replace('{{CUSTOMER_NAME}}', str(customer_name))
            html_content = html_content.replace('{{CUSTOMER_PHONE}}', str(customer_phone) if customer_phone else "N/A")
            html_content = html_content.replace('{{PAYMENT_METHOD}}', str(payment_method))
            html_content = html_content.replace('{{ITEMS_HTML}}', str(items_html))
            html_content = html_content.replace('{{TOTAL_SAVINGS}}', f"{total_savings:.0f}")
            # Fix savings percentage: (save amount)/(total mrp)*100
            html_content = html_content.replace('{{SAVINGS_PERCENTAGE}}', f"{(total_savings/total_mrp_amount*100):.1f}" if total_mrp_amount > 0 else "0")
            html_content = html_content.replace('{{TOTAL_MRP}}', f"{total_mrp_amount:.0f}")
            html_content = html_content.replace('{{FINAL_TOTAL}}', f"{final_total:.0f}")
            # Ensure final_total is valid before using it for UPI
            upi_amount = final_total if not pd.isna(final_total) and final_total > 0 else subtotal
            html_content = html_content.replace('{{UPI_AMOUNT}}', f"{upi_amount:.0f}")
            html_content = html_content.replace('{{TOTAL_AMOUNT}}', f"{upi_amount:.0f}")
            
            return html_content, None
            
        except Exception as e:
            return None, f"Error generating receipt: {str(e)}"
    
    def get_html_template(self):
        """Get the HTML template with placeholders"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Receipt - Bauji Traders</title>
  <style>
    body {
      width: 2.8in;
      font-family: 'Segoe UI', Arial, sans-serif;
      font-size: 11px;
      margin: 0;
      padding: 0.2in 0.1in;
      background: #fff;
      color: #222;
    }
    .center { text-align: center; }
    .bold { font-weight: bold; }
    .shop-info, .customer-info, .footer { margin-bottom: 8px; }
    .invoice-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 8px;
    }
    .invoice-table th, .invoice-table td {
      padding: 2px 3px;
      text-align: left;
      font-size: 10px;
    }
    .invoice-table th {
      border-bottom: 1px solid #aaa;
      font-weight: bold;
      background: #f5f5f5;
    }
    .invoice-table td {
      border-bottom: 1px dotted #ddd;
      white-space: nowrap;
    }
    .right { text-align: right; }
    .total-row td {
      border-top: 1px solid #aaa;
      font-weight: bold;
      background: #f5f5f5;
    }
    .save-row td {
      color: #388e3c;
      font-weight: bold;
      border: none;
      background: #e8f5e9;
    }
    .footer {
      border-top: 1px dashed #aaa;
      padding-top: 6px;
      font-size: 10px;
      text-align: center;
    }
    .qr-section {
      text-align: center;
      margin-top: 10px;
      padding-top: 8px;
      border-top: 1px dashed #aaa;
    }
    .qr-code {
      width: 80px;
      height: 80px;
      margin: 5px auto;
      display: block;
    }
    @media print {
      body { margin: 0; padding: 0.1in; }
      .qr-section { page-break-inside: avoid; }
    }
  </style>
</head>
<body>
  <div class="shop-info center bold">
    M/s SHRI BAUJI TRADERS<br>
    1690 30FT ROAD<br>
    JAWAHAR COLONY NIT FARIDABAD<br>
    State: 07<br>
    PH: 9911148114, 9555269666
  </div>
  <div class="customer-info">
    <div>Date/Time: {{DATETIME}}</div>
    <div>Customer: {{CUSTOMER_NAME}}</div>
    <div>Phone: {{CUSTOMER_PHONE}}</div>
    <div>Payment: {{PAYMENT_METHOD}}</div>
  </div>
  <table class="invoice-table">
    <tr>
      <th style="width: 1.1in;">Item</th>
      <th class="right" style="width: 0.3in;">Qty</th>
      <th class="right" style="width: 0.4in;">MRP</th>
      <th class="right" style="width: 0.4in;">Dis%</th>
      <th class="right" style="width: 0.4in;">Rate</th>
      <th class="right" style="width: 0.5in;">Total</th>
    </tr>
    {{ITEMS_HTML}}
    <tr class="save-row">
      <td colspan="6">SAVE RS {{TOTAL_SAVINGS}} ({{SAVINGS_PERCENTAGE}}%)</td>
    </tr>
    <tr class="total-row">
      <td colspan="5" class="right">TOTAL RS</td>
      <td class="right"><span style="text-decoration: line-through; color: #999; font-size: 10px;">{{TOTAL_MRP}}</span> {{FINAL_TOTAL}}</td>
    </tr>
  </table>
  <div class="footer">
    Thanks for visiting us, come back soon!
  </div>
  <div class="qr-section">
    <div style="font-size: 10px; font-weight: bold; margin-bottom: 3px;">Pay with UPI</div>
    <img class="qr-code" id="qrcode" alt="UPI QR Code" />
    <div style="font-size: 8px; color: #333; margin-top: 3px; line-height: 1.2;">
      <div>UPI ID: 9911108114@ybl</div>
      <div>Payee: Puneet Verma</div>
      <div style="font-weight: bold;">Amount: ₹{{UPI_AMOUNT}}</div>
    </div>
  </div>
  <script>
    // Generate UPI QR Code - Puneet Verma's UPI Details
    const upiId = "9911108114@ybl";
    let amount = "{{UPI_AMOUNT}}";
    const merchantName = "Puneet Verma";
    
    // Validate amount to prevent NaN
    if (!amount || amount === "nan" || amount === "NaN" || isNaN(parseFloat(amount))) {
      amount = "0";
    }
    
    // UPI payment URL format
    const upiUrl = `upi://pay?pa=${upiId}&pn=${encodeURIComponent(merchantName)}&am=${amount}&cu=INR&tn=${encodeURIComponent('Payment to Bauji Traders')}`;
    
    // Generate QR code using qr-server.com API
    const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=${encodeURIComponent(upiUrl)}`;
    
    // Set QR code image source
    document.getElementById('qrcode').src = qrCodeUrl;
  </script>
</body>
</html>"""
    
    def preview_receipt(self, transaction_id):
        """Generate and open receipt preview in browser"""
        try:
            html_content, error = self.generate_receipt_html(transaction_id)
            
            if error:
                print(f"Error: {error}")
                return False
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(html_content)
            temp_file.close()
            
            # Open in default browser
            webbrowser.open(f'file://{temp_file.name}')
            
            print(f"Receipt preview opened in browser: {temp_file.name}")
            return True
            
        except Exception as e:
            print(f"Error opening preview: {str(e)}")
            return False
    
    def save_receipt_html(self, transaction_id, output_path=None):
        """Save receipt as HTML file"""
        try:
            html_content, error = self.generate_receipt_html(transaction_id)
            
            if error:
                print(f"Error: {error}")
                return False
            
            if not output_path:
                # Create receipts directory if it doesn't exist
                receipts_dir = "receipts"
                os.makedirs(receipts_dir, exist_ok=True)
                output_path = os.path.join(receipts_dir, f"receipt_{transaction_id}.html")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Receipt saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saving receipt: {str(e)}")
            return False

def main():
    """Test the HTML receipt generator"""
    # File paths
    sales_file = "data/sales_transactions.csv"
    inventory_file = "inventory_master.csv"
    
    # Check if files exist
    if not os.path.exists(sales_file):
        print(f"Error: Sales file not found: {sales_file}")
        return
    
    if not os.path.exists(inventory_file):
        print(f"Error: Inventory file not found: {inventory_file}")
        return
    
    # Create generator
    generator = HTMLReceiptGenerator(sales_file, inventory_file)
    
    # Get latest transaction for testing
    try:
        sales_df = pd.read_csv(sales_file)
        if sales_df.empty:
            print("No transactions found in sales file")
            return
        
        latest_transaction = sales_df['Transaction_ID'].iloc[-1]
        print(f"Testing with latest transaction: {latest_transaction}")
        
        # Generate and preview receipt
        success = generator.preview_receipt(latest_transaction)
        
        if success:
            print("Receipt preview opened successfully!")
            
            # Also save a copy
            generator.save_receipt_html(latest_transaction, f"test_receipt_{latest_transaction}.html")
        else:
            print("Failed to generate receipt preview")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
