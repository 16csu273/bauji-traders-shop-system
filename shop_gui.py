"""
🏪 BAUJI TRADERS - GUI APPLICATION
==================================
Modern GUI for complete shop management system
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
import json
import os
from datetime import datetime, date
import threading

# Import existing modules
from sales_billing import SalesBilling
from stock_manager import StockManager
from customer_manager import CustomerManager
from reports_analytics import ReportsAnalytics

class BaujiTradersGUI:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("🏪 BAUJI TRADERS - Shop Management System")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Configure modern styling
        self.configure_styles()
        
        # Create a simple shop manager for the modules
        self.shop_manager = self.create_shop_manager()
        
        # Initialize modules
        self.sales = SalesBilling(self.shop_manager)
        self.stock = StockManager(self.shop_manager)
        self.customer = CustomerManager(self.shop_manager)
        self.reports = ReportsAnalytics(self.shop_manager)
        
        # Current cart for billing
        self.current_cart = []
        self.current_customer = None
        
        # Barcode manager setup
        self.inventory_file = "inventory_master.csv"
        self.barcode_df = None
        self.barcode_filtered_df = None
        self.barcode_current_filter = 'all'
        
        # Create GUI
        self.create_gui()
        
        # Load initial data
        self.refresh_all_data()
    
    def configure_styles(self):
        """Configure modern GUI styles"""
        style = ttk.Style()
        
        # Configure colors and fonts
        self.root.configure(bg='#f0f0f0')
        
        # Configure button styles
        style.configure('Accent.TButton', 
                       font=('Arial', 12, 'bold'),
                       foreground='white')
        
        # Configure heading styles  
        style.configure('Heading.TLabel',
                       font=('Arial', 14, 'bold'),
                       foreground='#2c3e50')
    
    def create_shop_manager(self):
        """Create a simple shop manager object for the modules"""
        class SimpleShopManager:
            def __init__(self):
                self.inventory_file = r"c:\workstation\adhoc_works\shop\inventory_master.csv"
                self.data_dir = r"c:\workstation\adhoc_works\shop\data"
                self.sales_file = os.path.join(self.data_dir, "sales_transactions.csv")
                self.customers_file = os.path.join(self.data_dir, "customers.json")
                self.stock_movements_file = os.path.join(self.data_dir, "stock_movements.csv")
                
                # Ensure data directory exists
                os.makedirs(self.data_dir, exist_ok=True)
                
                # Load data
                self.load_inventory()
                self.load_customers()
                
            def load_inventory(self):
                """Load inventory data"""
                try:
                    self.inventory = pd.read_csv(self.inventory_file)
                except Exception:
                    self.inventory = pd.DataFrame()
                    
            def load_customers(self):
                """Load customer data"""
                try:
                    if os.path.exists(self.customers_file):
                        with open(self.customers_file, 'r') as f:
                            self.customers = json.load(f)
                    else:
                        self.customers = {}
                except Exception:
                    self.customers = {}
                    
            def save_customers(self):
                """Save customer data"""
                try:
                    with open(self.customers_file, 'w') as f:
                        json.dump(self.customers, f, indent=2)
                except Exception as e:
                    print(f"Error saving customers: {e}")
                    
            def save_inventory(self):
                """Save inventory data"""
                try:
                    self.inventory.to_csv(self.inventory_file, index=False)
                except Exception as e:
                    print(f"Error saving inventory: {e}")
        
        return SimpleShopManager()
    
    def create_gui(self):
        """Create the main GUI interface"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        self.create_header(main_container)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs
        self.create_billing_tab()
        self.create_inventory_tab()
        self.create_customers_tab()
        self.create_reports_tab()
        self.create_transaction_history_tab()
        self.create_barcode_manager_tab()
        self.create_settings_tab()
        
        # Create status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Shop name and logo
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        shop_label = ttk.Label(title_frame, text="🏪 BAUJI TRADERS", 
                              font=("Arial", 24, "bold"))
        shop_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Complete Shop Management System", 
                                  font=("Arial", 12))
        subtitle_label.pack(anchor=tk.W)
        
        # Quick actions
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT)
        
        ttk.Button(actions_frame, text="🔄 Refresh", 
                  command=self.refresh_all_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="💾 Backup", 
                  command=self.backup_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="📊 Quick Report", 
                  command=self.show_quick_report).pack(side=tk.LEFT, padx=2)
    
    def create_billing_tab(self):
        """Create billing and sales tab"""
        billing_frame = ttk.Frame(self.notebook)
        self.notebook.add(billing_frame, text="💰 Billing & Sales")
        
        # Create main panes
        paned_window = ttk.PanedWindow(billing_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane - Product selection
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=2)
        
        # Product search and selection
        ttk.Label(left_frame, text="🛍️ Product Selection", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.product_search_var = tk.StringVar()
        self.product_search_var.trace('w', self.filter_products)
        search_entry = ttk.Entry(search_frame, textvariable=self.product_search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Barcode scanning section
        barcode_frame = ttk.Frame(left_frame)
        barcode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(barcode_frame, text="📱 Barcode Scanner:", 
                 font=("Arial", 12, "bold"), foreground="blue").pack(side=tk.LEFT)
        self.barcode_var = tk.StringVar()
        self.barcode_entry = ttk.Entry(barcode_frame, textvariable=self.barcode_var, 
                                      font=("Arial", 14), width=20)
        self.barcode_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        # Bind barcode entry events
        self.barcode_entry.bind('<Return>', self.process_barcode_scan)
        self.barcode_entry.bind('<FocusIn>', self.on_barcode_focus)
        
        # Quick scan indicator
        self.scan_status_var = tk.StringVar(value="Ready to scan...")
        ttk.Label(barcode_frame, textvariable=self.scan_status_var, 
                 font=("Arial", 10), foreground="green").pack(side=tk.LEFT, padx=(10, 0))
        
        # Auto-focus barcode entry on tab load
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Products listbox with scrollbar
        products_frame = ttk.Frame(left_frame)
        products_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for products
        columns = ('Name', 'Cost_Price', 'Sell_Price', 'MRP', 'Stock', 'Category')
        self.products_tree = ttk.Treeview(products_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.products_tree.heading('Name', text='Product Name')
        self.products_tree.heading('Cost_Price', text='Cost Price (₹)')
        self.products_tree.heading('Sell_Price', text='Sell Price (₹)')
        self.products_tree.heading('MRP', text='MRP (₹)')
        self.products_tree.heading('Stock', text='Stock')
        self.products_tree.heading('Category', text='Category')
        
        self.products_tree.column('Name', width=250)
        self.products_tree.column('Cost_Price', width=90)
        self.products_tree.column('Sell_Price', width=90)
        self.products_tree.column('MRP', width=90)
        self.products_tree.column('Stock', width=70)
        self.products_tree.column('Category', width=110)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(products_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        h_scrollbar = ttk.Scrollbar(products_frame, orient=tk.HORIZONTAL, command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click to add to cart
        self.products_tree.bind('<Double-1>', self.add_to_cart)
        
        # Add to cart button
        ttk.Button(left_frame, text="➕ Add to Cart", 
                  command=self.add_to_cart).pack(pady=10)
        
        # Right pane - Cart and billing
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        # Cart section
        cart_header = ttk.Frame(right_frame)
        cart_header.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(cart_header, text="🛒 Shopping Cart", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Label(cart_header, text="(Double-click item to edit)", 
                 font=("Arial", 9), foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        # Cart listbox
        cart_frame = ttk.Frame(right_frame)
        cart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        cart_columns = ('Product', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show='headings', height=10)
        
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100)
        
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add double-click event for editing cart items
        self.cart_tree.bind('<Double-1>', self.on_cart_item_double_click)
        
        # Cart controls
        cart_controls = ttk.Frame(right_frame)
        cart_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(cart_controls, text="❌ Remove Item", 
                  command=self.remove_from_cart).pack(side=tk.LEFT, padx=2)
        ttk.Button(cart_controls, text="🗑️ Clear Cart", 
                  command=self.clear_cart).pack(side=tk.LEFT, padx=2)
        
        # Billing totals
        totals_frame = ttk.LabelFrame(right_frame, text="💰 Billing Summary")
        totals_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.subtotal_var = tk.StringVar(value="₹0.00")
        self.discount_var = tk.StringVar(value="0")
        self.total_var = tk.StringVar(value="₹0.00")
        
        ttk.Label(totals_frame, text="Subtotal:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(totals_frame, textvariable=self.subtotal_var).grid(row=0, column=1, sticky=tk.E, padx=5, pady=2)
        
        ttk.Label(totals_frame, text="Discount (%):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        discount_entry = ttk.Entry(totals_frame, textvariable=self.discount_var, width=10)
        discount_entry.grid(row=1, column=1, sticky=tk.E, padx=5, pady=2)
        discount_entry.bind('<KeyRelease>', self.calculate_total)
        
        ttk.Label(totals_frame, text="Total:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(totals_frame, textvariable=self.total_var, 
                 font=("Arial", 12, "bold")).grid(row=2, column=1, sticky=tk.E, padx=5, pady=2)
        
        # Payment method
        payment_frame = ttk.LabelFrame(right_frame, text="💳 Payment Method")
        payment_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.payment_method = tk.StringVar(value="Cash")
        payment_methods = ["Cash", "Card", "UPI", "Credit"]
        
        for i, method in enumerate(payment_methods):
            ttk.Radiobutton(payment_frame, text=method, variable=self.payment_method, 
                           value=method).grid(row=0, column=i, padx=5, pady=5)
        
        # Checkout button
        checkout_btn = ttk.Button(right_frame, text="💳 CHECKOUT", 
                                 command=self.process_checkout, 
                                 style="Checkout.TButton")
        checkout_btn.pack(fill=tk.X, pady=10)
        
        # Configure checkout button style for better visibility
        style = ttk.Style()
        style.configure("Checkout.TButton", 
                       font=("Arial", 12, "bold"),
                       foreground="black",
                       background="#4CAF50")
    
    def create_inventory_tab(self):
        """Create inventory management tab"""
        inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_frame, text="📦 Inventory")
        
        # Create main sections
        top_frame = ttk.Frame(inventory_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Controls
        controls_frame = ttk.Frame(top_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(controls_frame, text="📦 Inventory Management", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(controls_frame, text="➕ Add Product", 
                  command=self.add_new_product).pack(side=tk.RIGHT, padx=2)
        ttk.Button(controls_frame, text="📝 Edit Product", 
                  command=self.edit_product).pack(side=tk.RIGHT, padx=2)
        ttk.Button(controls_frame, text="�️ Remove Product", 
                  command=self.remove_product).pack(side=tk.RIGHT, padx=2)
        ttk.Button(controls_frame, text="🔄 Restore Product", 
                  command=self.restore_product).pack(side=tk.RIGHT, padx=2)
        ttk.Button(controls_frame, text="�🔄 Stock Adjustment", 
                  command=self.stock_adjustment).pack(side=tk.RIGHT, padx=2)
        
        # Search frame for inventory
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Search Products:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.inventory_search_var = tk.StringVar()
        self.inventory_search_var.trace('w', self.filter_inventory)
        search_entry = ttk.Entry(search_frame, textvariable=self.inventory_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        # Clear search button
        ttk.Button(search_frame, text="❌ Clear", 
                  command=self.clear_inventory_search).pack(side=tk.LEFT, padx=2)
        
        # Search status label
        self.inventory_search_status = tk.StringVar(value="")
        ttk.Label(search_frame, textvariable=self.inventory_search_status, 
                 font=("Arial", 10), foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        # Inventory table with proper layout
        inv_frame = ttk.Frame(inventory_frame)
        inv_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        inventory_columns = ('Name', 'Category', 'Cost', 'MRP', 'Sell_Price', 'SP_10%', 'Stock', 'Value')
        self.inventory_tree = ttk.Treeview(inv_frame, columns=inventory_columns, show='headings')
        
        # Configure columns with better proportions
        col_widths = {'Name': 250, 'Category': 100, 'Cost': 80, 'MRP': 80, 
                     'Sell_Price': 80, 'SP_10%': 80, 'Stock': 60, 'Value': 100}
        
        for col in inventory_columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=col_widths.get(col, 100))
        
        # Scrollbars for inventory
        inv_v_scroll = ttk.Scrollbar(inv_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        inv_h_scroll = ttk.Scrollbar(inv_frame, orient=tk.HORIZONTAL, command=self.inventory_tree.xview)
        self.inventory_tree.configure(yscrollcommand=inv_v_scroll.set, xscrollcommand=inv_h_scroll.set)
        
        # Grid layout for better space utilization
        self.inventory_tree.grid(row=0, column=0, sticky='nsew')
        inv_v_scroll.grid(row=0, column=1, sticky='ns')
        inv_h_scroll.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights for proper expansion
        inv_frame.grid_rowconfigure(0, weight=1)
        inv_frame.grid_columnconfigure(0, weight=1)
        
        # Summary frame
        summary_frame = ttk.LabelFrame(inventory_frame, text="📊 Inventory Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.total_products_var = tk.StringVar()
        self.total_stock_var = tk.StringVar()
        self.total_value_var = tk.StringVar()
        
        ttk.Label(summary_frame, text="Total Products:").grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(summary_frame, textvariable=self.total_products_var).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(summary_frame, text="Total Stock:").grid(row=0, column=2, padx=10, pady=5)
        ttk.Label(summary_frame, textvariable=self.total_stock_var).grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Label(summary_frame, text="Total Value:").grid(row=0, column=4, padx=10, pady=5)
        ttk.Label(summary_frame, textvariable=self.total_value_var).grid(row=0, column=5, padx=10, pady=5)
    
    def create_customers_tab(self):
        """Create customer management tab"""
        customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(customers_frame, text="👥 Customers")
        
        # Controls
        controls_frame = ttk.Frame(customers_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="👥 Customer Management", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(controls_frame, text="➕ Add Customer", 
                  command=self.add_customer_dialog).pack(side=tk.RIGHT, padx=2)
        ttk.Button(controls_frame, text="📝 Edit Customer", 
                  command=self.edit_customer_dialog).pack(side=tk.RIGHT, padx=2)
        
        # Customer table
        customer_columns = ('Name', 'Phone', 'Email', 'Total_Purchases', 'Last_Visit', 'Loyalty_Points')
        self.customers_tree = ttk.Treeview(customers_frame, columns=customer_columns, show='headings')
        
        for col in customer_columns:
            self.customers_tree.heading(col, text=col.replace('_', ' '))
            self.customers_tree.column(col, width=120)
        
        # Customer scrollbars
        cust_frame = ttk.Frame(customers_frame)
        cust_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        cust_v_scroll = ttk.Scrollbar(cust_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=cust_v_scroll.set)
        
        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cust_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_reports_tab(self):
        """Create reports and analytics tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📊 Reports")
        
        # Create sections
        controls_frame = ttk.Frame(reports_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="📊 Reports & Analytics", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        # Report buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(buttons_frame, text="📈 Sales Report", 
                  command=self.generate_sales_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="📦 Stock Report", 
                  command=self.generate_stock_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="👥 Customer Report", 
                  command=self.generate_customer_report).pack(side=tk.LEFT, padx=2)
        
        # Report display area
        report_notebook = ttk.Notebook(reports_frame)
        report_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Daily summary
        daily_frame = ttk.Frame(report_notebook)
        report_notebook.add(daily_frame, text="📅 Today's Summary")
        
        self.create_daily_summary(daily_frame)
        
        # Charts frame (placeholder for future charts)
        charts_frame = ttk.Frame(report_notebook)
        report_notebook.add(charts_frame, text="📊 Charts")
        
        ttk.Label(charts_frame, text="📊 Charts and Analytics", 
                 font=("Arial", 16)).pack(pady=50)
        ttk.Label(charts_frame, text="Coming Soon: Visual charts and graphs", 
                 font=("Arial", 12)).pack()
    
    def create_transaction_history_tab(self):
        """Create transaction/sales history tab"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="📋 Transaction History")
        
        # Controls
        controls_frame = ttk.Frame(history_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="📋 Sales Transaction History", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        # Action buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(buttons_frame, text="🔄 Refresh", 
                  command=self.load_transaction_history).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🖨️ Reprint Receipt", 
                  command=self.reprint_receipt).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="👁️ View Details", 
                  command=self.view_transaction_details).pack(side=tk.LEFT, padx=2)
        
        # Search frame
        search_frame = ttk.Frame(history_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Search:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.history_search_var = tk.StringVar()
        self.history_search_var.trace('w', self.filter_transaction_history)
        search_entry = ttk.Entry(search_frame, textvariable=self.history_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Label(search_frame, text="Filter by:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 5))
        self.history_filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(search_frame, textvariable=self.history_filter_var, 
                                   values=["All", "Today", "Last 7 Days", "Last 30 Days"], 
                                   width=15, state="readonly")
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind('<<ComboboxSelected>>', self.filter_transaction_history)
        
        # Transaction history table
        history_table_frame = ttk.Frame(history_frame)
        history_table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        history_columns = ('Date', 'Time', 'Customer', 'Phone', 'Items', 'Amount', 'Payment', 'Receipt_ID')
        self.history_tree = ttk.Treeview(history_table_frame, columns=history_columns, show='headings')
        
        # Configure columns
        col_widths = {'Date': 100, 'Time': 80, 'Customer': 150, 'Phone': 120, 
                     'Items': 60, 'Amount': 100, 'Payment': 80, 'Receipt_ID': 120}
        
        for col in history_columns:
            self.history_tree.heading(col, text=col.replace('_', ' '))
            self.history_tree.column(col, width=col_widths.get(col, 100))
        
        # Scrollbars for history
        hist_v_scroll = ttk.Scrollbar(history_table_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        hist_h_scroll = ttk.Scrollbar(history_table_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=hist_v_scroll.set, xscrollcommand=hist_h_scroll.set)
        
        # Grid layout
        self.history_tree.grid(row=0, column=0, sticky='nsew')
        hist_v_scroll.grid(row=0, column=1, sticky='ns')
        hist_h_scroll.grid(row=1, column=0, sticky='ew')
        
        history_table_frame.grid_rowconfigure(0, weight=1)
        history_table_frame.grid_columnconfigure(0, weight=1)
        
        # Summary frame
        summary_frame = ttk.LabelFrame(history_frame, text="📊 Transaction Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.total_transactions_var = tk.StringVar()
        self.total_sales_amount_var = tk.StringVar()
        self.avg_transaction_var = tk.StringVar()
        
        ttk.Label(summary_frame, text="Total Transactions:").grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(summary_frame, textvariable=self.total_transactions_var).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(summary_frame, text="Total Sales:").grid(row=0, column=2, padx=10, pady=5)
        ttk.Label(summary_frame, textvariable=self.total_sales_amount_var).grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Label(summary_frame, text="Avg Transaction:").grid(row=0, column=4, padx=10, pady=5)
        ttk.Label(summary_frame, textvariable=self.avg_transaction_var).grid(row=0, column=5, padx=10, pady=5)
    
    def create_barcode_manager_tab(self):
        """Create barcode manager tab"""
        barcode_frame = ttk.Frame(self.notebook)
        self.notebook.add(barcode_frame, text="📊 Barcode Manager")
        
        # Header
        header_frame = ttk.Frame(barcode_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="📊 Barcode Manager - Assign Barcodes to Products", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        # Control frame
        control_frame = ttk.Frame(barcode_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Search and filter frame
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.barcode_search_var = tk.StringVar()
        self.barcode_search_var.trace('w', self.filter_barcode_products)
        search_entry = ttk.Entry(search_frame, textvariable=self.barcode_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Filter buttons
        ttk.Button(search_frame, text="Show All", command=self.show_all_barcode_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Show With Barcodes", command=self.show_with_barcodes).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Show Without Barcodes", command=self.show_without_barcodes).pack(side=tk.LEFT, padx=5)
        
        # Barcode assignment frame
        assign_frame = ttk.Frame(control_frame)
        assign_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(assign_frame, text="📱 Scan Barcode (Select product first):").pack(side=tk.LEFT)
        self.barcode_assign_var = tk.StringVar()
        self.barcode_assign_entry = ttk.Entry(assign_frame, textvariable=self.barcode_assign_var, width=20, font=("Arial", 10, "bold"))
        self.barcode_assign_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.barcode_assign_entry.bind('<Return>', self.assign_barcode_to_selected)
        
        ttk.Button(assign_frame, text="Assign Barcode", 
                  command=self.assign_barcode_to_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(assign_frame, text="Remove Barcode", 
                  command=self.remove_barcode_from_selected).pack(side=tk.LEFT, padx=5)
        
        # Products tree
        tree_frame = ttk.Frame(barcode_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create Treeview with scrollbar
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.barcode_tree = ttk.Treeview(tree_container, columns=('ID', 'Product', 'Stock', 'MRP', 'Cost', 'Barcode'), show='headings', height=15)
        
        # Bind selection event to auto-focus barcode entry
        self.barcode_tree.bind('<<TreeviewSelect>>', self.on_barcode_product_select)
        
        # Column headers
        self.barcode_tree.heading('ID', text='ID')
        self.barcode_tree.heading('Product', text='Product Name')
        self.barcode_tree.heading('Stock', text='Stock')
        self.barcode_tree.heading('MRP', text='MRP')
        self.barcode_tree.heading('Cost', text='Cost')
        self.barcode_tree.heading('Barcode', text='Barcode')
        
        # Column widths
        self.barcode_tree.column('ID', width=50)
        self.barcode_tree.column('Product', width=300)
        self.barcode_tree.column('Stock', width=80)
        self.barcode_tree.column('MRP', width=80)
        self.barcode_tree.column('Cost', width=80)
        self.barcode_tree.column('Barcode', width=150)
        
        # Add scrollbar
        barcode_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.barcode_tree.yview)
        self.barcode_tree.configure(yscrollcommand=barcode_scrollbar.set)
        
        self.barcode_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barcode_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status frame
        status_frame = ttk.Frame(barcode_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.barcode_status_var = tk.StringVar()
        self.barcode_status_var.set("Ready")
        ttk.Label(status_frame, textvariable=self.barcode_status_var).pack(side=tk.LEFT)
        
        # Initialize barcode manager data
        self.barcode_df = None
        self.barcode_filtered_df = None
        self.barcode_current_filter = 'all'
        self.load_barcode_inventory()
    
    def create_settings_tab(self):
        """Create settings and utilities tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        ttk.Label(settings_frame, text="⚙️ System Settings & Utilities", 
                 font=("Arial", 14, "bold")).pack(anchor=tk.W, padx=10, pady=10)
        
        # Utility buttons
        utilities_frame = ttk.LabelFrame(settings_frame, text="🛠️ System Utilities")
        utilities_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(utilities_frame, text="💾 Backup Data", 
                  command=self.backup_data).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(utilities_frame, text="📥 Import Data", 
                  command=self.import_data).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(utilities_frame, text="📤 Export Data", 
                  command=self.export_data).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(utilities_frame, text="🔄 Reset System", 
                  command=self.reset_system).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Shop information
        shop_frame = ttk.LabelFrame(settings_frame, text="🏪 Shop Information")
        shop_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = """
        Shop Name: BAUJI TRADERS
        Business Type: Confectionery & General Store
        System Version: 2.0 GUI Edition
        
        Features:
        ✅ Complete billing system with receipt printing
        ✅ Advanced inventory management
        ✅ Customer relationship management
        ✅ Comprehensive reporting and analytics
        ✅ Modern GUI interface
        ✅ Data backup and restore
        """
        
        ttk.Label(shop_frame, text=info_text, justify=tk.LEFT).pack(padx=10, pady=10)
    
    def create_daily_summary(self, parent):
        """Create today's summary display"""
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create summary cards
        cards_frame = ttk.Frame(summary_frame)
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Sales card
        sales_card = ttk.LabelFrame(cards_frame, text="💰 Today's Sales")
        sales_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.today_sales_var = tk.StringVar(value="₹0.00")
        self.today_transactions_var = tk.StringVar(value="0")
        
        ttk.Label(sales_card, text="Total Sales:", font=("Arial", 12)).pack(pady=2)
        ttk.Label(sales_card, textvariable=self.today_sales_var, 
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(sales_card, text="Transactions:", font=("Arial", 10)).pack()
        ttk.Label(sales_card, textvariable=self.today_transactions_var).pack()
        
        # Customers card
        customers_card = ttk.LabelFrame(cards_frame, text="👥 Customers")
        customers_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.total_customers_var = tk.StringVar(value="0")
        self.new_customers_var = tk.StringVar(value="0")
        
        ttk.Label(customers_card, text="Total Customers:", font=("Arial", 12)).pack(pady=2)
        ttk.Label(customers_card, textvariable=self.total_customers_var, 
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(customers_card, text="New Today:", font=("Arial", 10)).pack()
        ttk.Label(customers_card, textvariable=self.new_customers_var).pack()
        
        # Stock card
        stock_card = ttk.LabelFrame(cards_frame, text="📦 Stock Status")
        stock_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.low_stock_var = tk.StringVar(value="0")
        self.out_of_stock_var = tk.StringVar(value="0")
        
        ttk.Label(stock_card, text="Low Stock Items:", font=("Arial", 12)).pack(pady=2)
        ttk.Label(stock_card, textvariable=self.low_stock_var, 
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(stock_card, text="Out of Stock:", font=("Arial", 10)).pack()
        ttk.Label(stock_card, textvariable=self.out_of_stock_var).pack()
    
    def create_status_bar(self, parent):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Time label
        self.time_var = tk.StringVar()
        time_label = ttk.Label(status_frame, textvariable=self.time_var)
        time_label.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Update time
        self.update_time()
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)
    
    def refresh_all_data(self):
        """Refresh all data displays"""
        self.status_var.set("Refreshing data...")
        try:
            self.load_products()
            self.load_inventory()
            self.load_customers()
            self.load_transaction_history()
            self.update_daily_summary()
            self.status_var.set("Data refreshed successfully")
        except Exception as e:
            self.status_var.set(f"Error refreshing data: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")
    
    def load_products(self):
        """Load products into the products tree"""
        try:
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Load inventory data
            inventory_file = r"c:\workstation\adhoc_works\shop\inventory_master.csv"
            df = pd.read_csv(inventory_file)
            
            # Sort products alphabetically by Product_Name (case-insensitive)
            df = df.sort_values('Product_Name', key=lambda x: x.str.lower())
            
            # Add products to tree
            for _, row in df.iterrows():
                # Enhanced category determination from product name
                product_name = str(row['Product_Name']).upper()
                category = "General"  # Default category
                
                # Food & Beverages
                if any(word in product_name for word in ['TEA', 'COFFEE', 'BRU', 'LIPTON', 'TAJ MAHAL']):
                    category = "Beverages"
                elif any(word in product_name for word in ['BISCUIT', 'BOURBON', 'MARIE', 'TIGER', 'MONACO', 'KRACKJACK', 'HIDE & SEEK', 'HAPPY']):
                    category = "Biscuits"
                elif any(word in product_name for word in ['CHOCOLATE', 'DAIRY MILK', '5 STAR', 'KIT KAT', 'MUNCH', 'CHOCOPIE']):
                    category = "Confectionery"
                elif any(word in product_name for word in ['MAGGI', 'YIPPEE', 'KNOOR']):
                    category = "Instant Food"
                elif any(word in product_name for word in ['GHEE', 'OIL', 'SAFFOLA', 'PARACHUTE', 'AMLA', 'SARSO', 'NAVRATNA']):
                    category = "Oils & Ghee"
                elif any(word in product_name for word in ['JAM', 'KETCHUP', 'KISSAN', 'HAJMOLA', 'MADHU SUDAN', 'MILK FOOD', 'MOTHER DAIRY']):
                    category = "Food Products"
                elif any(word in product_name for word in ['HORLICKS', 'BOURNVITA', 'QUACKER OATS']):
                    category = "Health Drinks"
                
                # Personal Care
                elif any(word in product_name for word in ['SOAP', 'SHAMPOO', 'PASTE', 'BRUSH', 'CLOSEUP', 'COLGATE', 'DABUR', 'PEPSODENT']):
                    category = "Personal Care"
                elif any(word in product_name for word in ['CINTHOL', 'LUX', 'DOVE', 'PEARS', 'LIFEBOUY', 'SANTOOR', 'DETTOL', 'VIVEL']):
                    category = "Personal Care"
                elif any(word in product_name for word in ['CLINIC', 'H&S', 'SUNSILK', 'AYUR', 'TRESEME', 'VATIKA', 'HAIR CARE', 'HIMALAYA']):
                    category = "Hair Care"
                elif any(word in product_name for word in ['FAIR', 'PONDS', 'CREAM', 'LOTION', 'GARNIER', 'ALMOND DROP']):
                    category = "Skin Care"
                elif any(word in product_name for word in ['DEO', 'DENVER', 'PERFUME', 'FIGARO']):
                    category = "Fragrance"
                
                # Home Care
                elif any(word in product_name for word in ['DETERGENT', 'SURF', 'ARIEL', 'TIDE', 'WHEEL', 'RIN', 'EZEE']):
                    category = "Detergents"
                elif any(word in product_name for word in ['HARPIC', 'LIZOL', 'COLIN', 'VIM', 'EXO', 'CHERRY']):
                    category = "Cleaners"
                elif any(word in product_name for word in ['ALL OUT', 'HIT', 'GOOD KNIGHT', 'MORTEIN', 'LAXMANREKHA']):
                    category = "Pest Control"
                
                # Health & Wellness
                elif any(word in product_name for word in ['VICKS', 'ENO', 'DETTOL LIQUID', 'ANTISEPTIC']):
                    category = "Health Care"
                elif any(word in product_name for word in ['STAYFREE', 'WHISPER', 'PAMPERS']):
                    category = "Personal Hygiene"
                
                # Electronics & Accessories
                elif any(word in product_name for word in ['DURACELL', 'EVEREADY', 'BATTERY']):
                    category = "Batteries"
                elif any(word in product_name for word in ['BLADE', 'GILLETTE', 'WILKINSON']):
                    category = "Shaving"
                
                # Household Items
                elif any(word in product_name for word in ['FOAM', 'VEET']):
                    category = "Personal Accessories"
                elif any(word in product_name for word in ['PATANJALI']):
                    category = "Ayurvedic Products"
                
                # Calculate sell price: cost_price + 40% of (MRP - cost_price)
                cost_price = row['Cost_Price']
                mrp = row['MRP']
                profit_margin = mrp - cost_price
                sell_price = round(cost_price + (0.40 * profit_margin))
                
                self.products_tree.insert('', tk.END, values=(
                    row['Product_Name'],        # Name
                    f"₹{cost_price:.2f}",      # Cost_Price
                    f"₹{sell_price:.0f}",      # Sell_Price  
                    f"₹{mrp:.2f}",             # MRP
                    int(row['Quantity']),       # Stock
                    category                    # Category
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")
    
    def load_inventory(self):
        """Load inventory into the inventory tree"""
        try:
            # Clear existing items
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
            
            # Load inventory data
            inventory_file = r"c:\workstation\adhoc_works\shop\inventory_master.csv"
            df = pd.read_csv(inventory_file)
            
            # Sort products alphabetically by Product_Name (case-insensitive)
            df = df.sort_values('Product_Name', key=lambda x: x.str.lower())
            
            total_products = len(df)
            total_stock = df['Quantity'].sum()
            total_value = (df['Quantity'] * df['Cost_Price']).sum()
            
            # Add items to tree
            for _, row in df.iterrows():
                # Enhanced category determination from product name (same as load_products)
                product_name = str(row['Product_Name']).upper()
                category = "General"  # Default category
                
                # Food & Beverages
                if any(word in product_name for word in ['TEA', 'COFFEE', 'BRU', 'LIPTON', 'TAJ MAHAL']):
                    category = "Beverages"
                elif any(word in product_name for word in ['BISCUIT', 'BOURBON', 'MARIE', 'TIGER', 'MONACO', 'KRACKJACK', 'HIDE & SEEK', 'HAPPY']):
                    category = "Biscuits"
                elif any(word in product_name for word in ['CHOCOLATE', 'DAIRY MILK', '5 STAR', 'KIT KAT', 'MUNCH', 'CHOCOPIE']):
                    category = "Confectionery"
                elif any(word in product_name for word in ['MAGGI', 'YIPPEE', 'KNOOR']):
                    category = "Instant Food"
                elif any(word in product_name for word in ['GHEE', 'OIL', 'SAFFOLA', 'PARACHUTE', 'AMLA', 'SARSO', 'NAVRATNA']):
                    category = "Oils & Ghee"
                elif any(word in product_name for word in ['JAM', 'KETCHUP', 'KISSAN', 'HAJMOLA', 'MADHU SUDAN', 'MILK FOOD', 'MOTHER DAIRY']):
                    category = "Food Products"
                elif any(word in product_name for word in ['HORLICKS', 'BOURNVITA', 'QUACKER OATS']):
                    category = "Health Drinks"
                
                # Personal Care
                elif any(word in product_name for word in ['SOAP', 'SHAMPOO', 'PASTE', 'BRUSH', 'CLOSEUP', 'COLGATE', 'DABUR', 'PEPSODENT']):
                    category = "Personal Care"
                elif any(word in product_name for word in ['CINTHOL', 'LUX', 'DOVE', 'PEARS', 'LIFEBOUY', 'SANTOOR', 'DETTOL', 'VIVEL']):
                    category = "Personal Care"
                elif any(word in product_name for word in ['CLINIC', 'H&S', 'SUNSILK', 'AYUR', 'TRESEME', 'VATIKA', 'HAIR CARE', 'HIMALAYA']):
                    category = "Hair Care"
                elif any(word in product_name for word in ['FAIR', 'PONDS', 'CREAM', 'LOTION', 'GARNIER', 'ALMOND DROP']):
                    category = "Skin Care"
                elif any(word in product_name for word in ['DEO', 'DENVER', 'PERFUME', 'FIGARO']):
                    category = "Fragrance"
                
                # Home Care
                elif any(word in product_name for word in ['DETERGENT', 'SURF', 'ARIEL', 'TIDE', 'WHEEL', 'RIN', 'EZEE']):
                    category = "Detergents"
                elif any(word in product_name for word in ['HARPIC', 'LIZOL', 'COLIN', 'VIM', 'EXO', 'CHERRY']):
                    category = "Cleaners"
                elif any(word in product_name for word in ['ALL OUT', 'HIT', 'GOOD KNIGHT', 'MORTEIN', 'LAXMANREKHA']):
                    category = "Pest Control"
                
                # Health & Wellness
                elif any(word in product_name for word in ['VICKS', 'ENO', 'DETTOL LIQUID', 'ANTISEPTIC']):
                    category = "Health Care"
                elif any(word in product_name for word in ['STAYFREE', 'WHISPER', 'PAMPERS']):
                    category = "Personal Hygiene"
                
                # Electronics & Accessories
                elif any(word in product_name for word in ['DURACELL', 'EVEREADY', 'BATTERY']):
                    category = "Batteries"
                elif any(word in product_name for word in ['BLADE', 'GILLETTE', 'WILKINSON']):
                    category = "Shaving"
                
                # Household Items
                elif any(word in product_name for word in ['FOAM', 'VEET']):
                    category = "Personal Accessories"
                elif any(word in product_name for word in ['PATANJALI']):
                    category = "Ayurvedic Products"
                
                stock_value = row['Quantity'] * row['Cost_Price']
                
                # Calculate sell price: cost_price + 40% of (MRP - cost_price)
                cost_price = row['Cost_Price']
                mrp = row['MRP']
                profit_margin = mrp - cost_price
                sell_price = round(cost_price + (0.40 * profit_margin))
                
                self.inventory_tree.insert('', tk.END, values=(
                    row['Product_Name'],
                    category,
                    f"₹{cost_price:.2f}",
                    f"₹{mrp:.2f}",
                    f"₹{sell_price:.0f}",
                    f"₹{row.get('SP_10_Percent', 0):.2f}",
                    int(row['Quantity']),
                    f"₹{stock_value:.2f}"
                ))
            
            # Update summary
            self.total_products_var.set(f"{total_products:,}")
            self.total_stock_var.set(f"{total_stock:,}")
            self.total_value_var.set(f"₹{total_value:,.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {str(e)}")
    
    def load_customers(self):
        """Load customers into the customers tree"""
        try:
            # Clear existing items
            for item in self.customers_tree.get_children():
                self.customers_tree.delete(item)
            
            # Load customer data
            customers_file = r"c:\workstation\adhoc_works\shop\data\customers.json"
            if os.path.exists(customers_file):
                with open(customers_file, 'r') as f:
                    customers_data = json.load(f)
                
                # Add customers to tree (phone is the key)
                for phone, data in customers_data.items():
                    self.customers_tree.insert('', tk.END, values=(
                        data.get('name', 'Unknown'),
                        phone,
                        data.get('email', ''),
                        f"₹{data.get('total_purchases', 0):.2f}",
                        data.get('last_visit', ''),
                        data.get('loyalty_points', 0)
                    ))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    def update_daily_summary(self):
        """Update today's summary"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            
            # Load sales data
            sales_file = r"c:\workstation\adhoc_works\shop\data\sales_transactions.csv"
            if os.path.exists(sales_file):
                sales_df = pd.read_csv(sales_file)
                today_sales = sales_df[sales_df['Date'] == today]
                
                total_sales = today_sales['Final_Amount'].sum()
                total_transactions = len(today_sales)
                
                self.today_sales_var.set(f"₹{total_sales:.2f}")
                self.today_transactions_var.set(str(total_transactions))
            
            # Load customer data
            customers_file = r"c:\workstation\adhoc_works\shop\data\customers.json"
            if os.path.exists(customers_file):
                with open(customers_file, 'r') as f:
                    customers_data = json.load(f)
                
                total_customers = len(customers_data)
                new_today = sum(1 for data in customers_data.values() 
                               if data.get('registration_date', '') == today)
                
                self.total_customers_var.set(str(total_customers))
                self.new_customers_var.set(str(new_today))
            
            # Stock status
            inventory_file = r"c:\workstation\adhoc_works\shop\inventory_master.csv"
            if os.path.exists(inventory_file):
                df = pd.read_csv(inventory_file)
                low_stock = len(df[df['Quantity'] <= 10])
                out_of_stock = len(df[df['Quantity'] == 0])
                
                self.low_stock_var.set(str(low_stock))
                self.out_of_stock_var.set(str(out_of_stock))
                
        except Exception as e:
            print(f"Error updating daily summary: {e}")
    
    def filter_products(self, *args):
        """Filter products based on search"""
        search_term = self.product_search_var.get().lower()
        
        # Clear and reload products with filter
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        try:
            inventory_file = r"c:\workstation\adhoc_works\shop\inventory_master.csv"
            df = pd.read_csv(inventory_file)
            
            # Filter products
            if search_term:
                df = df[df['Product_Name'].str.lower().str.contains(search_term, na=False)]
            
            # Sort filtered products alphabetically (case-insensitive)
            df = df.sort_values('Product_Name', key=lambda x: x.str.lower())
            
            # Add filtered products to tree
            for _, row in df.iterrows():
                # Enhanced category determination from product name
                product_name = str(row['Product_Name']).upper()
                category = "General"  # Default category
                
                # Food & Beverages
                if any(word in product_name for word in ['TEA', 'COFFEE', 'BRU', 'LIPTON', 'TAJ MAHAL']):
                    category = "Beverages"
                elif any(word in product_name for word in ['BISCUIT', 'BOURBON', 'MARIE', 'TIGER', 'MONACO', 'KRACKJACK', 'HIDE & SEEK', 'HAPPY']):
                    category = "Biscuits"
                elif any(word in product_name for word in ['CHOCOLATE', 'DAIRY MILK', '5 STAR', 'KIT KAT', 'MUNCH', 'CHOCOPIE']):
                    category = "Confectionery"
                elif any(word in product_name for word in ['MAGGI', 'YIPPEE', 'KNOOR']):
                    category = "Instant Food"
                elif any(word in product_name for word in ['GHEE', 'OIL', 'SAFFOLA', 'PARACHUTE', 'AMLA', 'SARSO', 'NAVRATNA']):
                    category = "Oils & Ghee"
                elif any(word in product_name for word in ['JAM', 'KETCHUP', 'KISSAN', 'HAJMOLA', 'MADHU SUDAN', 'MILK FOOD', 'MOTHER DAIRY']):
                    category = "Food Products"
                elif any(word in product_name for word in ['HORLICKS', 'BOURNVITA', 'QUACKER OATS']):
                    category = "Health Drinks"
                
                # Personal Care
                elif any(word in product_name for word in ['SOAP', 'SHAMPOO', 'PASTE', 'BRUSH', 'CLOSEUP', 'COLGATE', 'DABUR', 'PEPSODENT']):
                    category = "Personal Care"
                elif any(word in product_name for word in ['CINTHOL', 'LUX', 'DOVE', 'PEARS', 'LIFEBOUY', 'SANTOOR', 'DETTOL', 'VIVEL']):
                    category = "Personal Care"
                elif any(word in product_name for word in ['CLINIC', 'H&S', 'SUNSILK', 'AYUR', 'TRESEME', 'VATIKA', 'HAIR CARE', 'HIMALAYA']):
                    category = "Hair Care"
                elif any(word in product_name for word in ['FAIR', 'PONDS', 'CREAM', 'LOTION', 'GARNIER', 'ALMOND DROP']):
                    category = "Skin Care"
                elif any(word in product_name for word in ['DEO', 'DENVER', 'PERFUME', 'FIGARO']):
                    category = "Fragrance"
                
                # Home Care
                elif any(word in product_name for word in ['DETERGENT', 'SURF', 'ARIEL', 'TIDE', 'WHEEL', 'RIN', 'EZEE']):
                    category = "Detergents"
                elif any(word in product_name for word in ['HARPIC', 'LIZOL', 'COLIN', 'VIM', 'EXO', 'CHERRY']):
                    category = "Cleaners"
                elif any(word in product_name for word in ['ALL OUT', 'HIT', 'GOOD KNIGHT', 'MORTEIN', 'LAXMANREKHA']):
                    category = "Pest Control"
                
                # Health & Wellness
                elif any(word in product_name for word in ['VICKS', 'ENO', 'DETTOL LIQUID', 'ANTISEPTIC']):
                    category = "Health Care"
                elif any(word in product_name for word in ['STAYFREE', 'WHISPER', 'PAMPERS']):
                    category = "Personal Hygiene"
                
                # Electronics & Accessories
                elif any(word in product_name for word in ['DURACELL', 'EVEREADY', 'BATTERY']):
                    category = "Batteries"
                elif any(word in product_name for word in ['BLADE', 'GILLETTE', 'WILKINSON']):
                    category = "Shaving"
                
                # Household Items
                elif any(word in product_name for word in ['FOAM', 'VEET']):
                    category = "Personal Accessories"
                elif any(word in product_name for word in ['PATANJALI']):
                    category = "Ayurvedic Products"
                
                # Calculate sell price: cost_price + 40% of (MRP - cost_price)
                cost_price = row['Cost_Price']
                mrp = row['MRP']
                profit_margin = mrp - cost_price
                sell_price = round(cost_price + (0.40 * profit_margin))
                
                self.products_tree.insert('', tk.END, values=(
                    row['Product_Name'],        # Name
                    f"₹{cost_price:.2f}",      # Cost_Price
                    f"₹{sell_price:.0f}",      # Sell_Price  
                    f"₹{mrp:.2f}",             # MRP
                    int(row['Quantity']),       # Stock
                    category                    # Category
                ))
        except Exception as e:
            print(f"Error filtering products: {e}")
    
    def filter_inventory(self, *args):
        """Filter inventory based on search"""
        search_term = self.inventory_search_var.get().lower()
        
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        try:
            # Load inventory data
            inventory_file = r"c:\workstation\adhoc_works\shop\inventory_master.csv"
            df = pd.read_csv(inventory_file)
            
            # Filter inventory
            original_count = len(df)
            if search_term:
                df = df[df['Product_Name'].str.lower().str.contains(search_term, na=False)]
            
            # Sort filtered inventory alphabetically (case-insensitive)
            df = df.sort_values('Product_Name', key=lambda x: x.str.lower())
            
            # Update search status
            filtered_count = len(df)
            if search_term:
                self.inventory_search_status.set(f"Found {filtered_count} of {original_count} products")
            else:
                self.inventory_search_status.set("")
            
            # Add filtered items to tree
            total_products = filtered_count
            total_stock = df['Quantity'].sum() if not df.empty else 0
            total_value = (df['Quantity'] * df['Cost_Price']).sum() if not df.empty else 0
            
            for _, row in df.iterrows():
                category = row.get('Category', 'General')
                stock_value = row['Quantity'] * row['Cost_Price']
                
                self.inventory_tree.insert('', tk.END, values=(
                    row['Product_Name'],
                    category,
                    f"₹{row['Cost_Price']:.2f}",
                    f"₹{row['MRP']:.2f}",
                    f"₹{row['SP_5_Percent']:.2f}",
                    f"₹{row['SP_10_Percent']:.2f}",
                    int(row['Quantity']),
                    f"₹{stock_value:.2f}"
                ))
            
            # Update summary with filtered data
            self.total_products_var.set(f"{total_products:,}")
            self.total_stock_var.set(f"{total_stock:,}")
            self.total_value_var.set(f"₹{total_value:,.2f}")
            
        except Exception as e:
            print(f"Error filtering inventory: {e}")
            messagebox.showerror("Error", f"Failed to filter inventory: {str(e)}")
    
    def clear_inventory_search(self):
        """Clear inventory search and show all products"""
        self.inventory_search_var.set("")
        self.inventory_search_status.set("")
        self.load_inventory()  # Reload all inventory data
    
    def process_barcode_scan(self, event=None):
        """Process scanned barcode and add product to cart"""
        barcode = self.barcode_var.get().strip()
        
        if not barcode:
            return
        
        try:
            # Load inventory to find product by barcode or name
            inventory_df = pd.read_csv(self.shop_manager.inventory_file, dtype={'Barcode': str})
            
            # First try to find by exact barcode match (if you have barcode column)
            product_found = None
            
            # Check if inventory has a barcode column
            if 'Barcode' in inventory_df.columns:
                # Handle NaN values and convert to string for comparison
                inventory_df['Barcode'] = inventory_df['Barcode'].fillna('')
                
                # Convert barcode column to string and remove .0 if present
                inventory_df['Barcode_Clean'] = inventory_df['Barcode'].astype(str).str.replace('.0', '', regex=False).str.strip()
                
                # Try exact match first
                barcode_match = inventory_df[inventory_df['Barcode_Clean'] == barcode.strip()]
                if not barcode_match.empty:
                    product_found = barcode_match.iloc[0]
            
            # If no barcode column or no match, try to find by product name/ID
            if product_found is None:
                # Try to find by Sr_No
                try:
                    sr_no = int(barcode)
                    sr_match = inventory_df[inventory_df['Sr_No'] == sr_no]
                    if not sr_match.empty:
                        product_found = sr_match.iloc[0]
                except ValueError:
                    pass
            
            # If still no match, try partial name matching
            if product_found is None:
                name_match = inventory_df[inventory_df['Product_Name'].str.contains(barcode, case=False, na=False)]
                if not name_match.empty:
                    product_found = name_match.iloc[0]
            
            if product_found is not None:
                # Product found - add to cart automatically (no quantity dialog)
                self.add_scanned_product_to_cart_auto(product_found)
                self.scan_status_var.set(f"✅ Added: {product_found['Product_Name'][:30]}...")
                
                # Clear barcode entry for next scan
                self.barcode_var.set("")
                
                # Auto-focus back to barcode entry
                self.root.after(100, lambda: self.barcode_entry.focus_set())
                
            else:
                # Product not found
                self.scan_status_var.set(f"❌ Product not found: {barcode}")
                messagebox.showwarning("Product Not Found", 
                                     f"No product found with barcode/ID: {barcode}\n\n"
                                     f"Please check the barcode or add the product to inventory first.")
                
        except Exception as e:
            self.scan_status_var.set("❌ Scan error")
            messagebox.showerror("Scan Error", f"Error processing barcode: {str(e)}")
        
        # Reset status after 3 seconds
        self.root.after(3000, lambda: self.scan_status_var.set("Ready to scan..."))
    
    def add_scanned_product_to_cart_auto(self, product_row):
        """Add scanned product to cart automatically with quantity 1 (or increment existing)"""
        try:
            product_name = product_row['Product_Name']
            cost_price = product_row['Cost_Price']
            mrp = product_row['MRP']
            available_stock = int(product_row['Quantity'])
            
            # Calculate sell price
            profit_margin = mrp - cost_price
            sell_price = round(cost_price + (0.40 * profit_margin))
            
            # Check if product already in cart
            existing_item = None
            for item in self.current_cart:
                if item['product'] == product_name:
                    existing_item = item
                    break
            
            if existing_item:
                # Product already in cart - increment quantity by 1
                new_quantity = existing_item['quantity'] + 1
                
                # Check stock availability
                if new_quantity > available_stock:
                    messagebox.showwarning("Insufficient Stock", 
                                         f"Cannot add more {product_name}.\n"
                                         f"Available stock: {available_stock}\n"
                                         f"Quantity in cart: {existing_item['quantity']}")
                    return
                
                # Update quantity and total
                existing_item['quantity'] = new_quantity
                existing_item['total'] = new_quantity * existing_item['price']
            else:
                # New product - add with quantity 1
                if available_stock < 1:
                    messagebox.showwarning("Out of Stock", 
                                         f"Product {product_name} is out of stock!")
                    return
                
                # Add new item to cart
                cart_item = {
                    'product': product_name,
                    'quantity': 1,
                    'price': sell_price,
                    'total': sell_price
                }
                self.current_cart.append(cart_item)
            
            # Update cart display and totals
            self.update_cart_display()
            self.calculate_total()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product to cart: {str(e)}")
    
    def add_scanned_product_to_cart(self, product_row):
        """Add scanned product to cart with quantity selection"""
        try:
            product_name = product_row['Product_Name']
            cost_price = product_row['Cost_Price']
            mrp = product_row['MRP']
            available_stock = int(product_row['Quantity'])
            
            # Check if product already in cart
            existing_item = None
            for item in self.current_cart:
                if item['product'] == product_name:
                    existing_item = item
                    break
            
            # Ask for quantity
            if existing_item:
                current_qty = existing_item['quantity']
                quantity = simpledialog.askinteger("Update Quantity", 
                                                 f"Product: {product_name}\n"
                                                 f"Current in cart: {current_qty}\n"
                                                 f"Available stock: {available_stock}\n\n"
                                                 f"Enter new total quantity:", 
                                                 initialvalue=current_qty + 1,
                                                 minvalue=0, maxvalue=available_stock)
                if quantity is None:
                    return
                
                if quantity == 0:
                    # Remove from cart
                    self.current_cart.remove(existing_item)
                else:
                    # Update quantity
                    existing_item['quantity'] = quantity
                    existing_item['total'] = quantity * existing_item['price']
            else:
                quantity = simpledialog.askinteger("Add to Cart", 
                                                 f"Product: {product_name}\n"
                                                 f"Available stock: {available_stock}\n\n"
                                                 f"Enter quantity:", 
                                                 initialvalue=1,
                                                 minvalue=1, maxvalue=available_stock)
                if quantity is None:
                    return
                
                # Calculate sell price
                profit_margin = mrp - cost_price
                sell_price = round(cost_price + (0.40 * profit_margin))
                
                # Add new item to cart
                cart_item = {
                    'product': product_name,
                    'quantity': quantity,
                    'price': sell_price,
                    'total': quantity * sell_price
                }
                self.current_cart.append(cart_item)
            
            # Update cart display and totals
            self.update_cart_display()
            self.calculate_total()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product to cart: {str(e)}")
    
    def on_barcode_focus(self, event=None):
        """Handle barcode entry focus"""
        self.scan_status_var.set("🔍 Scanner ready - scan barcode...")
    
    def on_tab_changed(self, event=None):
        """Handle tab change - focus barcode entry when billing tab is selected"""
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if "Billing" in current_tab:
                # Auto-focus barcode entry when billing tab is active
                self.root.after(100, lambda: self.barcode_entry.focus_set())
        except:
            pass
    
    def add_to_cart(self, event=None):
        """Add selected product to cart"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add to cart")
            return
        
        try:
            # Get selected product details
            item = self.products_tree.item(selection[0])
            values = item['values']
            
            product_name = values[0]  # Product name (first column)
            cost_price_str = str(values[1]).replace('₹', '').strip()  # Cost price
            sell_price_str = str(values[2]).replace('₹', '').strip()  # Sell price  
            mrp_str = str(values[3]).replace('₹', '').strip()  # MRP
            available_stock = int(values[4])  # Stock
            
            # Convert to float safely
            cost_price = float(cost_price_str)
            sell_price = float(sell_price_str) 
            mrp_price = float(mrp_str)
            
            if available_stock <= 0:
                messagebox.showwarning("Warning", f"{product_name} is out of stock!")
                return
            
            # Let user choose between sell price, MRP, or custom price
            price_choice = messagebox.askyesnocancel("Price Selection", 
                                                    f"Product: {product_name}\n\n"
                                                    f"Sell Price: ₹{sell_price:.2f}\n"
                                                    f"MRP: ₹{mrp_price:.2f}\n\n"
                                                    f"Choose price:\n"
                                                    f"Yes = MRP (₹{mrp_price:.2f})\n"
                                                    f"No = Sell Price (₹{sell_price:.2f})\n"
                                                    f"Cancel = Custom Price")
            
            if price_choice is True:  # Yes - MRP
                price = mrp_price
            elif price_choice is False:  # No - Sell Price
                price = sell_price
            else:  # Cancel - Custom Price
                custom_price = simpledialog.askfloat("Custom Price", 
                                                    f"Enter custom price for {product_name}:",
                                                    initialvalue=mrp_price, minvalue=0.01)
                if custom_price is None:
                    return
                price = custom_price
            
            # Ask for quantity
            quantity = simpledialog.askinteger("Quantity", 
                                             f"Enter quantity for {product_name}:\n(Available: {available_stock})",
                                             initialvalue=1, minvalue=1, maxvalue=available_stock)
            
            if quantity is None:
                return
            
            # Check if product already in cart
            existing_item = None
            for cart_item in self.current_cart:
                if cart_item['product'] == product_name:
                    existing_item = cart_item
                    break
            
            if existing_item:
                # Update existing item
                new_qty = existing_item['quantity'] + quantity
                if new_qty > available_stock:
                    messagebox.showwarning("Warning", f"Cannot add more. Only {available_stock} available.")
                    return
                existing_item['quantity'] = new_qty
                existing_item['price'] = price  # Update price in case it changed
                existing_item['total'] = new_qty * price
            else:
                # Add new item to cart
                self.current_cart.append({
                    'product': product_name,
                    'quantity': quantity,
                    'price': price,
                    'total': quantity * price
                })
            
            # Update display
            self.update_cart_display()
            self.calculate_total()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product to cart: {str(e)}")
            print(f"Debug - Add to cart error: {e}")
            print(f"Debug - Values: {values}")
            return
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        # Get selected item
        item = self.cart_tree.item(selection[0])
        product_name = item['values'][0]
        
        # Remove from cart
        self.current_cart = [item for item in self.current_cart if item['product'] != product_name]
        
        self.update_cart_display()
        self.calculate_total()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if messagebox.askyesno("Confirm", "Clear all items from cart?"):
            self.current_cart = []
            self.update_cart_display()
            self.calculate_total()
    
    def update_cart_display(self):
        """Update cart tree display"""
        # Clear existing items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        for cart_item in self.current_cart:
            self.cart_tree.insert('', tk.END, values=(
                cart_item['product'],
                cart_item['quantity'],
                f"₹{cart_item['price']:.2f}",
                f"₹{cart_item['total']:.2f}"
            ))
    
    def calculate_total(self, event=None):
        """Calculate and update total"""
        try:
            subtotal = sum(item['total'] for item in self.current_cart)
            self.subtotal_var.set(f"₹{subtotal:.2f}")
            
            discount_percent = float(self.discount_var.get() or 0)
            discount_amount = subtotal * (discount_percent / 100)
            total = subtotal - discount_amount
            
            self.total_var.set(f"₹{total:.2f}")
            
        except ValueError:
            self.total_var.set(f"₹{sum(item['total'] for item in self.current_cart):.2f}")
    
    def on_cart_item_double_click(self, event):
        """Handle double-click on cart item for editing"""
        selection = self.cart_tree.selection()
        if not selection:
            return
        
        item = self.cart_tree.item(selection[0])
        values = item['values']
        
        if not values:
            return
            
        product_name = values[0]
        current_qty = values[1]
        current_price = values[2].replace('₹', '').replace(',', '')
        
        # Show edit dialog
        self.show_cart_edit_dialog(product_name, current_qty, current_price)
    
    def show_cart_edit_dialog(self, product_name, current_qty, current_price):
        """Show dialog to edit cart item quantity and price"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Cart Item")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Product name (read-only)
        ttk.Label(dialog, text="Product:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Label(dialog, text=product_name, font=("Arial", 10)).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Quantity
        ttk.Label(dialog, text="Quantity:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        qty_var = tk.StringVar(value=str(current_qty))
        qty_entry = ttk.Entry(dialog, textvariable=qty_var, width=15)
        qty_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        qty_entry.focus()
        qty_entry.select_range(0, tk.END)
        
        # Price
        ttk.Label(dialog, text="Price (₹):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        price_var = tk.StringVar(value=str(current_price))
        price_entry = ttk.Entry(dialog, textvariable=price_var, width=15)
        price_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def save_changes():
            try:
                new_qty = int(qty_var.get())
                new_price = float(price_var.get())
                
                if new_qty <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return
                    
                if new_price <= 0:
                    messagebox.showerror("Error", "Price must be greater than 0")
                    return
                
                # Update cart item
                for cart_item in self.current_cart:
                    if cart_item['product'] == product_name:
                        cart_item['quantity'] = new_qty
                        cart_item['price'] = new_price
                        cart_item['total'] = new_qty * new_price
                        break
                
                # Update display
                self.update_cart_display()
                self.calculate_total()
                
                dialog.destroy()
                messagebox.showinfo("Success", f"Updated {product_name}")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for quantity and price")
        
        def cancel_edit():
            dialog.destroy()
        
        ttk.Button(button_frame, text="💾 Save", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=cancel_edit).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to save
        qty_entry.bind('<Return>', lambda e: save_changes())
        price_entry.bind('<Return>', lambda e: save_changes())
    
    def add_new_customer(self):
        """Add new customer during billing"""
        self.add_customer_dialog()
    
    def process_checkout(self):
        """Process the checkout"""
        if not self.current_cart:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        
        try:
            # Calculate totals for display
            subtotal = sum(item['total'] for item in self.current_cart)
            discount_percent = float(self.discount_var.get() or 0)
            discount_amount = subtotal * (discount_percent / 100)
            final_amount = subtotal - discount_amount
            
            # Get customer information with new checkout dialog
            checkout_dialog = CheckoutDialog(self.root, "Checkout", final_amount)
            self.root.wait_window(checkout_dialog.dialog)
            
            if checkout_dialog.action == 'cancel' or not checkout_dialog.result:
                # User cancelled the dialog
                return
            
            customer_info = checkout_dialog.result
            
            # Get payment method
            payment_method = self.payment_method.get()
            
            # Generate transaction ID
            transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Process sale directly
            result = self.process_sale_direct(
                transaction_id=transaction_id,
                cart_items=self.current_cart,
                customer_info=customer_info,
                payment_method=payment_method,
                discount_percent=discount_percent,
                final_amount=final_amount
            )
            
            if result['success']:
                # Clear cart first
                self.current_cart = []
                self.update_cart_display()
                self.calculate_total()
                
                # Reset discount
                self.discount_var.set("0")
                
                # Refresh data
                self.refresh_all_data()
                
                # Handle different actions
                if checkout_dialog.action == 'save_print':
                    # Direct print without asking
                    self.print_receipt(transaction_id, direct_print=True)
                    messagebox.showinfo("Success", 
                                      f"✅ Sale completed and receipt printed!\n"
                                      f"Transaction ID: {transaction_id}\n"
                                      f"Customer: {customer_info['name']}\n"
                                      f"Total Amount: ₹{final_amount:.2f}")
                
                elif checkout_dialog.action == 'show_receipt':
                    # Show success message first
                    messagebox.showinfo("Success", 
                                      f"✅ Sale completed successfully!\n"
                                      f"Transaction ID: {transaction_id}\n"
                                      f"Customer: {customer_info['name']}\n"
                                      f"Total Amount: ₹{final_amount:.2f}")
                    
                    # Then ask to print receipt (current behavior)
                    if messagebox.askyesno("Print Receipt", "Would you like to print receipt?"):
                        self.print_receipt(transaction_id)
                    
            else:
                messagebox.showerror("Error", f"Sale failed: {result['message']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Checkout failed: {str(e)}")
    
    def process_sale_direct(self, transaction_id, cart_items, customer_info, payment_method, discount_percent, final_amount):
        """Process sale directly without using complex modules"""
        try:
            # Load current inventory
            inventory_df = pd.read_csv(self.shop_manager.inventory_file)
            
            # Load sales file
            sales_file = self.shop_manager.sales_file
            if os.path.exists(sales_file):
                sales_df = pd.read_csv(sales_file)
            else:
                # Create new sales file
                sales_columns = [
                    'Transaction_ID', 'Date', 'Time', 'Customer_Name', 'Customer_Phone',
                    'Product_Name', 'Quantity_Sold', 'Unit_Price', 'Total_Amount', 
                    'Payment_Method', 'Discount', 'Final_Amount'
                ]
                sales_df = pd.DataFrame(columns=sales_columns)
            
            current_time = datetime.now()
            current_date = current_time.strftime('%Y-%m-%d')
            current_time_str = current_time.strftime('%H:%M:%S')
            
            # Process each item in cart
            for item in cart_items:
                product_name = item['product']
                quantity = item['quantity']
                unit_price = item['price']
                total_amount = item['total']
                
                # Check and update inventory
                product_idx = inventory_df[inventory_df['Product_Name'] == product_name].index
                if len(product_idx) > 0:
                    current_stock = inventory_df.loc[product_idx[0], 'Quantity']
                    if current_stock >= quantity:
                        # Update stock
                        inventory_df.loc[product_idx[0], 'Quantity'] -= quantity
                    else:
                        return {'success': False, 'message': f"Insufficient stock for {product_name}"}
                else:
                    return {'success': False, 'message': f"Product {product_name} not found"}
                
                # Add to sales record
                new_sale = {
                    'Transaction_ID': transaction_id,
                    'Date': current_date,
                    'Time': current_time_str,
                    'Customer_Name': customer_info['name'],
                    'Customer_Phone': customer_info['phone'],
                    'Product_Name': product_name,
                    'Quantity_Sold': quantity,
                    'Unit_Price': unit_price,
                    'Total_Amount': total_amount,
                    'Payment_Method': payment_method,
                    'Discount': discount_percent,
                    'Final_Amount': final_amount / len(cart_items)  # Distribute total across items
                }
                
                sales_df = pd.concat([sales_df, pd.DataFrame([new_sale])], ignore_index=True)
            
            # Save files
            inventory_df.to_csv(self.shop_manager.inventory_file, index=False)
            sales_df.to_csv(sales_file, index=False)
            
            # Save customer info with purchase amount
            self.save_customer_info(customer_info, final_amount)
            
            return {'success': True, 'transaction_id': transaction_id}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def save_customer_info(self, customer_info, purchase_amount=0):
        """Save customer information to customers.json with phone as primary key"""
        try:
            customers_file = 'data/customers.json'
            
            # Load existing customers
            if os.path.exists(customers_file):
                with open(customers_file, 'r') as f:
                    customers = json.load(f)
            else:
                customers = {}
            
            # Use phone number as primary key
            phone = customer_info.get('phone', '').strip()
            if not phone:
                print("Warning: Customer has no phone number, using name as key")
                phone = customer_info.get('name', 'unknown')
            
            # Check if customer already exists
            if phone in customers:
                # Update existing customer data
                existing_customer = customers[phone]
                existing_customer['name'] = customer_info['name']
                existing_customer['email'] = customer_info.get('email', '')
                existing_customer['last_visit'] = datetime.now().strftime('%Y-%m-%d')
                # Add purchase amount to total purchases
                existing_customer['total_purchases'] = existing_customer.get('total_purchases', 0) + purchase_amount
                existing_customer['loyalty_points'] = existing_customer.get('loyalty_points', 0) + 1
            else:
                # Add new customer
                customers[phone] = {
                    'name': customer_info['name'],
                    'phone': phone,
                    'email': customer_info.get('email', ''),
                    'total_purchases': purchase_amount,
                    'last_visit': datetime.now().strftime('%Y-%m-%d'),
                    'loyalty_points': 1
                }
            
            # Save customers file
            os.makedirs('data', exist_ok=True)
            with open(customers_file, 'w') as f:
                json.dump(customers, f, indent=2)
                
            print(f"Customer saved: {customer_info['name']} ({phone}) - Purchase: ₹{purchase_amount}")
                
        except Exception as e:
            print(f"Error saving customer info: {e}")
    
    def print_receipt(self, transaction_id, direct_print=False):
        """Print receipt for transaction"""
        try:
            # Generate receipt text
            receipt = self.generate_receipt_direct(transaction_id)
            
            if direct_print:
                # Direct print to thermal printer without preview
                self.send_to_printer(receipt)
                return
            
            # Create receipt window optimized for thermal paper preview
            receipt_window = tk.Toplevel(self.root)
            receipt_window.title("🧾 Thermal Receipt Preview")
            receipt_window.geometry("400x600")
            
            # Receipt text with thermal paper font
            text_widget = tk.Text(receipt_window, font=("Courier", 8), width=42)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            text_widget.insert(tk.END, receipt)
            text_widget.config(state=tk.DISABLED)
            
            # Print button
            ttk.Button(receipt_window, text="🖨️ Print to Thermal Printer", 
                      command=lambda: self.send_to_printer(receipt)).pack(pady=10)
                      
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate receipt: {str(e)}")
    
    def generate_receipt_direct(self, transaction_id):
        """Generate receipt text directly"""
        try:
            # Load sales data and inventory data
            sales_df = pd.read_csv(self.shop_manager.sales_file)
            transaction_sales = sales_df[sales_df['Transaction_ID'] == transaction_id]
            
            if transaction_sales.empty:
                return "Receipt not found"
            
            # Load inventory for MRP lookup
            inventory_df = pd.read_csv(self.shop_manager.inventory_file)
            
            # Get transaction details
            first_row = transaction_sales.iloc[0]
            
            receipt = f"""
{'='*42}
        BAUJI TRADERS
      CONFECTIONERY STORE
{'='*42}
Address: 1690 30FT ROAD,
         JAWAHAR COLONY
Phone: 9911148114, 9555269666

TXN ID: {transaction_id}
Date: {first_row['Date']}
Time: {first_row['Time']}
Customer: {first_row['Customer_Name']}
Phone: {first_row['Customer_Phone']}
Payment: {first_row['Payment_Method']}

{'='*42}
ITEMS:
{'='*42}
"""
            
            # Header row for thermal paper
            receipt += f"{'Item':<14} {'Q':<2} {'MRP':<4} {'D%':<3} {'Rate':<4} {'Tot':<4}\n"
            receipt += f"{'-'*42}\n"
            
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
                
                # Format product name for thermal paper (truncate if too long)
                product_short = product_name[:13] if len(product_name) > 13 else product_name
                
                receipt += f"{product_short:<14} {quantity:<2} {mrp:<4.0f} {discount_percentage:<2.0f}% {sell_price:<4.0f} {item_total:<4.0f}\n"
            
            total_savings = total_mrp_amount - total_amount
            
            # Apply any additional discount from transaction
            discount = float(first_row['Discount']) if first_row['Discount'] else 0
            additional_discount_amount = total_amount * (discount / 100)
            final_total = total_amount - additional_discount_amount
            total_savings += additional_discount_amount
            
            receipt += f"{'-'*42}\n"
            receipt += f"{'TOTAL:':<30} Rs.{final_total:<8.0f}\n"
            
            if additional_discount_amount > 0:
                receipt += f"Extra Discount ({discount}%): Rs.{additional_discount_amount:.0f}\n"
            
            receipt += f"{'='*42}\n"
            receipt += f"You saved Rs.{total_savings:.0f} today!\n"
            receipt += f"{'='*42}\n"
            receipt += f"\nThank you for shopping!\n"
            receipt += f"Visit again soon!\n\n"
            receipt += f"{'='*42}\n"
            
            return receipt
            
        except Exception as e:
            return f"Error generating receipt: {str(e)}"
            
            return receipt
            
        except Exception as e:
            return f"Error generating receipt: {str(e)}"
    
    def send_to_printer(self, receipt_text):
        """Send receipt to thermal printer"""
        try:
            # For actual thermal printer, you would use something like:
            # import win32print
            # printer_name = win32print.GetDefaultPrinter()
            # or specify your thermal printer name
            
            # For now, we'll simulate sending to printer
            # You can replace this with actual printer code
            
            # Try to print using default printer (works with thermal printers)
            import tempfile
            import os
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(receipt_text)
                temp_file = f.name
            
            # Send to default printer (will work if thermal printer is default)
            os.system(f'notepad /p "{temp_file}"')
            
            # Clean up
            try:
                os.unlink(temp_file)
            except:
                pass
                
            messagebox.showinfo("Print", "✅ Receipt sent to thermal printer!")
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print receipt: {str(e)}\n\nPlease check your thermal printer connection.")
    
    # Transaction History Functions
    def load_transaction_history(self):
        """Load and display transaction history"""
        try:
            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Load sales data
            if not os.path.exists(self.shop_manager.sales_file):
                self.update_transaction_summary(0, 0, 0)
                return
            
            sales_df = pd.read_csv(self.shop_manager.sales_file)
            
            if sales_df.empty:
                self.update_transaction_summary(0, 0, 0)
                return
            
            # Group by transaction ID to get transaction-level data
            transaction_groups = sales_df.groupby('Transaction_ID').agg({
                'Date': 'first',
                'Time': 'first', 
                'Customer_Name': 'first',
                'Customer_Phone': 'first',
                'Payment_Method': 'first',
                'Total_Amount': 'first',
                'Product_Name': 'count'  # Count of items
            }).reset_index()
            
            # Sort by date and time (newest first)
            transaction_groups['DateTime'] = pd.to_datetime(
                transaction_groups['Date'] + ' ' + transaction_groups['Time']
            )
            transaction_groups = transaction_groups.sort_values('DateTime', ascending=False)
            
            # Store all transactions for filtering
            self.all_transactions = transaction_groups
            
            # Apply current filter
            self.filter_transaction_history()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transaction history: {str(e)}")
    
    def filter_transaction_history(self, *args):
        """Filter transaction history based on search and date filter"""
        try:
            if not hasattr(self, 'all_transactions'):
                return
            
            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            df = self.all_transactions.copy()
            
            # Apply date filter
            filter_value = self.history_filter_var.get()
            today = pd.Timestamp.now().normalize()
            
            if filter_value == "Today":
                df = df[df['DateTime'].dt.normalize() == today]
            elif filter_value == "Last 7 Days":
                week_ago = today - pd.Timedelta(days=7)
                df = df[df['DateTime'] >= week_ago]
            elif filter_value == "Last 30 Days":
                month_ago = today - pd.Timedelta(days=30)
                df = df[df['DateTime'] >= month_ago]
            
            # Apply search filter
            search_text = self.history_search_var.get().lower()
            if search_text:
                mask = (
                    df['Customer_Name'].str.lower().str.contains(search_text, na=False) |
                    df['Customer_Phone'].str.lower().str.contains(search_text, na=False) |
                    df['Transaction_ID'].str.lower().str.contains(search_text, na=False) |
                    df['Payment_Method'].str.lower().str.contains(search_text, na=False)
                )
                df = df[mask]
            
            # Display filtered results
            total_amount = 0
            for _, row in df.iterrows():
                # Format values
                date_str = row['Date']
                time_str = row['Time']
                customer = row['Customer_Name'] if pd.notna(row['Customer_Name']) else 'Walk-in'
                phone = row['Customer_Phone'] if pd.notna(row['Customer_Phone']) else 'N/A'
                items_count = int(row['Product_Name'])  # This is the count of items
                amount = float(row['Total_Amount'])
                payment = row['Payment_Method']
                transaction_id = row['Transaction_ID']
                
                total_amount += amount
                
                # Insert into tree
                self.history_tree.insert('', 'end', values=(
                    date_str, time_str, customer, phone, items_count, 
                    f"₹{amount:.2f}", payment, transaction_id
                ))
            
            # Update summary
            transaction_count = len(df)
            avg_transaction = total_amount / transaction_count if transaction_count > 0 else 0
            self.update_transaction_summary(transaction_count, total_amount, avg_transaction)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter transactions: {str(e)}")
    
    def update_transaction_summary(self, count, total_amount, avg_amount):
        """Update transaction summary display"""
        self.total_transactions_var.set(f"{count}")
        self.total_sales_amount_var.set(f"₹{total_amount:.2f}")
        self.avg_transaction_var.set(f"₹{avg_amount:.2f}")
    
    def reprint_receipt(self):
        """Reprint receipt for selected transaction"""
        try:
            selected = self.history_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a transaction to reprint receipt")
                return
            
            # Get transaction ID from selected item
            item = self.history_tree.item(selected[0])
            transaction_id = item['values'][7]  # Receipt_ID column
            
            # Generate and display receipt
            self.print_receipt(transaction_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reprint receipt: {str(e)}")
    
    def view_transaction_details(self):
        """View detailed transaction information"""
        try:
            selected = self.history_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a transaction to view details")
                return
            
            # Get transaction ID from selected item
            item = self.history_tree.item(selected[0])
            transaction_id = item['values'][7]  # Receipt_ID column
            
            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Transaction Details - {transaction_id}")
            details_window.geometry("800x600")
            
            # Load transaction data
            sales_df = pd.read_csv(self.shop_manager.sales_file)
            transaction_data = sales_df[sales_df['Transaction_ID'] == transaction_id]
            
            if transaction_data.empty:
                ttk.Label(details_window, text="Transaction not found").pack(pady=20)
                return
            
            # Create notebook for organized display
            details_notebook = ttk.Notebook(details_window)
            details_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Transaction Info Tab
            info_frame = ttk.Frame(details_notebook)
            details_notebook.add(info_frame, text="📋 Transaction Info")
            
            first_row = transaction_data.iloc[0]
            
            info_text = f"""
Transaction ID: {transaction_id}
Date: {first_row['Date']}
Time: {first_row['Time']}
Customer: {first_row['Customer_Name']}
Phone: {first_row['Customer_Phone']}
Payment Method: {first_row['Payment_Method']}
Total Amount: ₹{first_row['Total_Amount']:.2f}
Discount: {first_row['Discount']}%
"""
            
            ttk.Label(info_frame, text=info_text, font=("Arial", 12)).pack(anchor=tk.W, padx=20, pady=20)
            
            # Items Tab
            items_frame = ttk.Frame(details_notebook)
            details_notebook.add(items_frame, text="🛍️ Items Purchased")
            
            # Items table
            items_columns = ('Product', 'Quantity', 'Unit_Price', 'Total')
            items_tree = ttk.Treeview(items_frame, columns=items_columns, show='headings')
            
            for col in items_columns:
                items_tree.heading(col, text=col.replace('_', ' '))
                items_tree.column(col, width=150)
            
            # Add items to table
            for _, row in transaction_data.iterrows():
                items_tree.insert('', 'end', values=(
                    row['Product_Name'],
                    row['Quantity_Sold'],
                    f"₹{row['Unit_Price']:.2f}",
                    f"₹{row['Unit_Price'] * row['Quantity_Sold']:.2f}"
                ))
            
            items_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Action buttons
            button_frame = ttk.Frame(details_window)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Button(button_frame, text="🖨️ Print Receipt", 
                      command=lambda: self.print_receipt(transaction_id)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="❌ Close", 
                      command=details_window.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view transaction details: {str(e)}")
    
    # Additional methods for other functionalities
    def add_new_product(self):
        """Add new product dialog"""
        dialog = ProductDialog(self.root, "Add New Product")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                # Add product directly to inventory
                result = self.add_product_direct(dialog.result)
                if result['success']:
                    messagebox.showinfo("Success", "Product added successfully!")
                    self.refresh_all_data()
                else:
                    messagebox.showerror("Error", result['message'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {str(e)}")
    
    def add_product_direct(self, product_data):
        """Add product directly to inventory file"""
        try:
            # Load current inventory
            inventory_df = pd.read_csv(self.shop_manager.inventory_file)
            
            # Check if product already exists
            if product_data['name'] in inventory_df['Product_Name'].values:
                return {'success': False, 'message': 'Product already exists'}
            
            # Calculate pricing
            cost_price = product_data['cost_price']
            mrp = product_data['mrp']
            sp_5_percent = mrp * 0.95
            sp_10_percent = mrp * 0.90
            
            # Create new product row
            new_product = {
                'Product_Name': product_data['name'],
                'Cost_Price': cost_price,
                'MRP': mrp,
                'SP_5_Percent': sp_5_percent,
                'SP_10_Percent': sp_10_percent,
                'Quantity': product_data['quantity'],
                'Category': product_data.get('category', 'General'),
                'Actual_Margin_Percent': ((mrp - cost_price) / cost_price) * 100
            }
            
            # Add to inventory
            inventory_df = pd.concat([inventory_df, pd.DataFrame([new_product])], ignore_index=True)
            
            # Save inventory
            inventory_df.to_csv(self.shop_manager.inventory_file, index=False)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def edit_product(self):
        """Edit selected product with full edit dialog"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit")
            return
        
        item = self.inventory_tree.item(selection[0])
        values = item['values']
        product_name = values[0]
        
        # Find product in inventory
        try:
            product_row = self.shop_manager.inventory[
                self.shop_manager.inventory['Product_Name'] == product_name
            ]
            
            if product_row.empty:
                messagebox.showerror("Error", "Product not found in inventory")
                return
                
            current_data = product_row.iloc[0]
            
            # Create edit dialog
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"📝 Edit Product - {product_name}")
            edit_window.geometry("500x600")
            edit_window.grab_set()
            
            # Center the window
            edit_window.transient(self.root)
            
            # Main frame
            main_frame = ttk.Frame(edit_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            ttk.Label(main_frame, text=f"📝 Edit Product: {product_name}", 
                     font=("Arial", 16, "bold")).pack(pady=(0, 20))
            
            # Create form fields
            fields = {}
            
            # Product Name (read-only for now)
            ttk.Label(main_frame, text="Product Name:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 2))
            name_var = tk.StringVar(value=current_data['Product_Name'])
            name_entry = ttk.Entry(main_frame, textvariable=name_var, state='readonly', width=50)
            name_entry.pack(fill=tk.X, pady=(0, 10))
            fields['Product_Name'] = name_var
            
            # Category
            ttk.Label(main_frame, text="Category:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
            category_var = tk.StringVar(value=current_data.get('Category', ''))
            category_combo = ttk.Combobox(main_frame, textvariable=category_var, width=47)
            category_combo['values'] = ['General', 'Dairy', 'Beverages', 'Snacks', 'Personal Care', 'Household']
            category_combo.pack(fill=tk.X, pady=(0, 10))
            fields['Category'] = category_var
            
            # Cost Price
            ttk.Label(main_frame, text="Cost Price (₹):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
            cost_var = tk.StringVar(value=str(current_data.get('Cost_Price', 0)))
            cost_entry = ttk.Entry(main_frame, textvariable=cost_var, width=50)
            cost_entry.pack(fill=tk.X, pady=(0, 10))
            fields['Cost_Price'] = cost_var
            
            # MRP
            ttk.Label(main_frame, text="MRP (₹):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
            mrp_var = tk.StringVar(value=str(current_data.get('MRP', 0)))
            mrp_entry = ttk.Entry(main_frame, textvariable=mrp_var, width=50)
            mrp_entry.pack(fill=tk.X, pady=(0, 10))
            fields['MRP'] = mrp_var
            
            # Stock Quantity
            ttk.Label(main_frame, text="Stock Quantity:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
            stock_var = tk.StringVar(value=str(current_data.get('Quantity', 0)))
            stock_entry = ttk.Entry(main_frame, textvariable=stock_var, width=50)
            stock_entry.pack(fill=tk.X, pady=(0, 10))
            fields['Quantity'] = stock_var
            
            # Auto-calculate selling prices when MRP changes (for background calculation)
            def update_selling_prices(*args):
                # Still calculate but don't show in UI - used for saving to CSV
                try:
                    mrp_value = float(mrp_var.get())
                    # Calculate but store in hidden variables
                    sp_5_value = mrp_value * 0.95  # 5% discount
                    sp_10_value = mrp_value * 0.90  # 10% discount
                    # Store for saving purposes
                    fields['SP_5_Percent'] = sp_5_value
                    fields['SP_10_Percent'] = sp_10_value
                except ValueError:
                    fields['SP_5_Percent'] = 0
                    fields['SP_10_Percent'] = 0
            
            mrp_var.trace('w', update_selling_prices)
            
            # Initialize selling prices calculation
            update_selling_prices()
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(20, 0))
            
            def save_changes():
                try:
                    # Validate inputs
                    cost_price = float(fields['Cost_Price'].get())
                    mrp = float(fields['MRP'].get())
                    stock = int(fields['Quantity'].get())
                    
                    if cost_price <= 0 or mrp <= 0 or stock < 0:
                        messagebox.showerror("Error", "Please enter valid positive values")
                        return
                    
                    # Calculate selling prices automatically
                    sp_5_percent = mrp * 0.95  # 5% discount
                    sp_10_percent = mrp * 0.90  # 10% discount
                    
                    # Update inventory
                    idx = self.shop_manager.inventory[
                        self.shop_manager.inventory['Product_Name'] == product_name
                    ].index[0]
                    
                    self.shop_manager.inventory.loc[idx, 'Category'] = fields['Category'].get()
                    self.shop_manager.inventory.loc[idx, 'Cost_Price'] = cost_price
                    self.shop_manager.inventory.loc[idx, 'MRP'] = mrp
                    self.shop_manager.inventory.loc[idx, 'SP_5_Percent'] = sp_5_percent
                    self.shop_manager.inventory.loc[idx, 'SP_10_Percent'] = sp_10_percent
                    self.shop_manager.inventory.loc[idx, 'Quantity'] = stock
                    
                    # Save to file
                    self.shop_manager.save_inventory()
                    
                    messagebox.showinfo("Success", f"Product '{product_name}' updated successfully!")
                    edit_window.destroy()
                    self.refresh_all_data()
                    
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numeric values")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update product: {str(e)}")
            
            def cancel_edit():
                edit_window.destroy()
            
            ttk.Button(buttons_frame, text="💾 Save Changes", 
                      command=save_changes).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="❌ Cancel", 
                      command=cancel_edit).pack(side=tk.LEFT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product data: {str(e)}")
    
    def remove_product(self):
        """Remove selected product from inventory"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to remove")
            return
        
        item = self.inventory_tree.item(selection[0])
        product_name = item['values'][0]
        current_stock = int(item['values'][6])
        
        # Confirm deletion
        if current_stock > 0:
            confirm_msg = f"Product '{product_name}' has {current_stock} items in stock.\n\nAre you sure you want to remove this product permanently?\n\nThis action cannot be undone."
        else:
            confirm_msg = f"Are you sure you want to remove '{product_name}' permanently?\n\nThis action cannot be undone."
        
        if not messagebox.askyesno("Confirm Removal", confirm_msg):
            return
        
        try:
            # Load current inventory
            inventory_df = pd.read_csv(self.shop_manager.inventory_file)
            
            # Find and remove the product
            product_exists = inventory_df['Product_Name'] == product_name
            if not product_exists.any():
                messagebox.showerror("Error", f"Product '{product_name}' not found in inventory")
                return
            
            # Find and save deleted product data before removing
            deleted_product_data = inventory_df[product_exists].copy()
            
            # Save deleted product to restore file
            self.save_deleted_product(product_name, deleted_product_data)
            
            # Remove the product
            inventory_df = inventory_df[~product_exists]
            
            # Save updated inventory
            inventory_df.to_csv(self.shop_manager.inventory_file, index=False)
            
            # Update shop manager inventory
            self.shop_manager.load_inventory()
            
            # Refresh inventory display
            self.load_inventory()
            
            # Refresh billing products display to remove deleted product
            self.load_products()
            
            # Show success message
            messagebox.showinfo("Success", f"Product '{product_name}' has been removed successfully")
            
            # Update status
            self.status_var.set(f"Product '{product_name}' removed successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove product: {str(e)}")
    
    def stock_adjustment(self):
        """Stock adjustment dialog"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product for stock adjustment")
            return
        
        item = self.inventory_tree.item(selection[0])
        product_name = item['values'][0]
        current_stock = int(item['values'][6])
        
        # Ask for adjustment
        adjustment = simpledialog.askinteger("Stock Adjustment", 
                                           f"Current stock for {product_name}: {current_stock}\n"
                                           f"Enter adjustment (+/- value):",
                                           initialvalue=0)
        
        if adjustment is not None and adjustment != 0:
            try:
                result = self.adjust_stock_direct(product_name, adjustment)
                if result['success']:
                    messagebox.showinfo("Success", f"Stock adjusted by {adjustment}")
                    self.refresh_all_data()
                else:
                    messagebox.showerror("Error", result['message'])
            except Exception as e:
                messagebox.showerror("Error", f"Stock adjustment failed: {str(e)}")
    
    def adjust_stock_direct(self, product_name, adjustment):
        """Adjust stock directly"""
        try:
            # Load inventory
            inventory_df = pd.read_csv(self.shop_manager.inventory_file)
            
            # Find product
            product_idx = inventory_df[inventory_df['Product_Name'] == product_name].index
            if len(product_idx) == 0:
                return {'success': False, 'message': 'Product not found'}
            
            # Update stock
            current_stock = inventory_df.loc[product_idx[0], 'Quantity']
            new_stock = current_stock + adjustment
            
            if new_stock < 0:
                return {'success': False, 'message': 'Stock cannot be negative'}
            
            inventory_df.loc[product_idx[0], 'Quantity'] = new_stock
            
            # Save inventory
            inventory_df.to_csv(self.shop_manager.inventory_file, index=False)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def save_deleted_product(self, product_name, product_data):
        """Save deleted product data for restore functionality"""
        try:
            import json
            from datetime import datetime
            
            # Create deleted products file path
            deleted_file = os.path.join(self.shop_manager.data_dir, "deleted_products.json")
            
            # Load existing deleted products
            if os.path.exists(deleted_file):
                with open(deleted_file, 'r') as f:
                    deleted_products = json.load(f)
            else:
                deleted_products = {}
            
            # Add deletion timestamp and product data
            deleted_products[product_name] = {
                'product_data': product_data.iloc[0].to_dict(),
                'deleted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'deleted_by': 'Admin'  # Could be enhanced to track actual user
            }
            
            # Keep only last 50 deleted products to avoid file getting too large
            if len(deleted_products) > 50:
                # Sort by deletion time and keep most recent 50
                sorted_items = sorted(deleted_products.items(), 
                                    key=lambda x: x[1]['deleted_at'], reverse=True)
                deleted_products = dict(sorted_items[:50])
            
            # Save updated deleted products
            with open(deleted_file, 'w') as f:
                json.dump(deleted_products, f, indent=2)
                
        except Exception as e:
            print(f"Error saving deleted product: {e}")
    
    def restore_product(self):
        """Show restore dialog with recently deleted products"""
        try:
            import json
            
            # Load deleted products
            deleted_file = os.path.join(self.shop_manager.data_dir, "deleted_products.json")
            
            if not os.path.exists(deleted_file):
                messagebox.showinfo("No Deleted Products", "No recently deleted products found to restore.")
                return
            
            with open(deleted_file, 'r') as f:
                deleted_products = json.load(f)
            
            if not deleted_products:
                messagebox.showinfo("No Deleted Products", "No recently deleted products found to restore.")
                return
            
            # Create restore dialog
            restore_window = tk.Toplevel(self.root)
            restore_window.title("🔄 Restore Deleted Products")
            restore_window.geometry("800x600")
            restore_window.grab_set()
            restore_window.transient(self.root)
            
            # Main frame
            main_frame = ttk.Frame(restore_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            ttk.Label(main_frame, text="🔄 Restore Deleted Products", 
                     font=("Arial", 16, "bold")).pack(pady=(0, 20))
            
            # Instructions
            ttk.Label(main_frame, text="Select a product to restore:", 
                     font=("Arial", 12)).pack(anchor=tk.W, pady=(0, 10))
            
            # Create treeview for deleted products
            tree_frame = ttk.Frame(main_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            columns = ('Product_Name', 'Cost_Price', 'MRP', 'Stock', 'Deleted_At')
            deleted_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
            
            # Configure columns
            deleted_tree.heading('Product_Name', text='Product Name')
            deleted_tree.heading('Cost_Price', text='Cost Price (₹)')
            deleted_tree.heading('MRP', text='MRP (₹)')
            deleted_tree.heading('Stock', text='Last Stock')
            deleted_tree.heading('Deleted_At', text='Deleted At')
            
            deleted_tree.column('Product_Name', width=250)
            deleted_tree.column('Cost_Price', width=100)
            deleted_tree.column('MRP', width=100)
            deleted_tree.column('Stock', width=80)
            deleted_tree.column('Deleted_At', width=150)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=deleted_tree.yview)
            deleted_tree.configure(yscrollcommand=scrollbar.set)
            
            deleted_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Populate with deleted products
            for product_name, product_info in deleted_products.items():
                data = product_info['product_data']
                deleted_tree.insert('', tk.END, values=(
                    product_name,
                    f"₹{data.get('Cost_Price', 0):.2f}",
                    f"₹{data.get('MRP', 0):.2f}",
                    int(data.get('Quantity', 0)),
                    product_info['deleted_at']
                ))
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X)
            
            def restore_selected():
                selection = deleted_tree.selection()
                if not selection:
                    messagebox.showwarning("Warning", "Please select a product to restore")
                    return
                
                item = deleted_tree.item(selection[0])
                product_name = item['values'][0]
                
                # Confirm restore
                if messagebox.askyesno("Confirm Restore", 
                                     f"Are you sure you want to restore '{product_name}'?"):
                    
                    result = self.restore_product_direct(product_name, deleted_products[product_name])
                    
                    if result['success']:
                        messagebox.showinfo("Success", f"Product '{product_name}' has been restored successfully!")
                        restore_window.destroy()
                        self.refresh_all_data()
                    else:
                        messagebox.showerror("Error", f"Failed to restore product: {result['message']}")
            
            def delete_permanently():
                selection = deleted_tree.selection()
                if not selection:
                    messagebox.showwarning("Warning", "Please select a product to delete permanently")
                    return
                
                item = deleted_tree.item(selection[0])
                product_name = item['values'][0]
                
                if messagebox.askyesno("Confirm Permanent Deletion", 
                                     f"Are you sure you want to permanently delete '{product_name}'?\n"
                                     f"This action cannot be undone."):
                    
                    # Remove from deleted products
                    del deleted_products[product_name]
                    
                    # Save updated deleted products
                    with open(deleted_file, 'w') as f:
                        json.dump(deleted_products, f, indent=2)
                    
                    # Remove from tree
                    deleted_tree.delete(selection[0])
                    
                    messagebox.showinfo("Success", f"Product '{product_name}' has been permanently deleted")
            
            def close_dialog():
                restore_window.destroy()
            
            ttk.Button(buttons_frame, text="🔄 Restore Selected", 
                      command=restore_selected).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="🗑️ Delete Permanently", 
                      command=delete_permanently).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="❌ Close", 
                      command=close_dialog).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load deleted products: {str(e)}")
    
    def restore_product_direct(self, product_name, product_info):
        """Restore a deleted product back to inventory"""
        try:
            import json
            
            # Load current inventory
            inventory_df = pd.read_csv(self.shop_manager.inventory_file)
            
            # Check if product already exists
            if product_name in inventory_df['Product_Name'].values:
                return {'success': False, 'message': f'Product "{product_name}" already exists in inventory'}
            
            # Get product data
            product_data = product_info['product_data']
            
            # Create new row for inventory
            new_product = pd.DataFrame([product_data])
            
            # Add to inventory
            inventory_df = pd.concat([inventory_df, new_product], ignore_index=True)
            
            # Save updated inventory
            inventory_df.to_csv(self.shop_manager.inventory_file, index=False)
            
            # Remove from deleted products
            deleted_file = os.path.join(self.shop_manager.data_dir, "deleted_products.json")
            with open(deleted_file, 'r') as f:
                deleted_products = json.load(f)
            
            if product_name in deleted_products:
                del deleted_products[product_name]
                
                with open(deleted_file, 'w') as f:
                    json.dump(deleted_products, f, indent=2)
            
            # Update shop manager
            self.shop_manager.load_inventory()
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def add_customer_dialog(self):
        """Add customer dialog"""
        dialog = CustomerDialog(self.root, "Add New Customer")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                result = self.add_customer_direct(dialog.result)
                if result['success']:
                    messagebox.showinfo("Success", "Customer added successfully!")
                    self.load_customers()
                else:
                    messagebox.showerror("Error", result['message'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
    
    def add_customer_direct(self, customer_data):
        """Add customer directly to file"""
        try:
            # Load customers
            customers = self.shop_manager.customers
            
            # Check if customer exists
            if customer_data['name'] in customers:
                return {'success': False, 'message': 'Customer already exists'}
            
            # Add new customer
            customers[customer_data['name']] = {
                'name': customer_data['name'],
                'phone': customer_data['phone'],
                'email': customer_data['email'],
                'registration_date': date.today().strftime('%Y-%m-%d'),
                'total_purchases': 0,
                'last_visit': '',
                'loyalty_points': 0
            }
            
            # Save customers
            self.shop_manager.save_customers()
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def edit_customer_dialog(self):
        """Edit customer dialog"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to edit")
            return
        
        item = self.customers_tree.item(selection[0])
        customer_name = item['values'][0]
        
        messagebox.showinfo("Edit Customer", f"Edit functionality for {customer_name} will be implemented in the next version.")
    
    def generate_sales_report(self):
        """Generate sales report with MRP and Profit columns"""
        try:
            # Simple daily report generation
            today = date.today().strftime('%Y-%m-%d')
            
            # Load sales data
            if os.path.exists(self.shop_manager.sales_file):
                sales_df = pd.read_csv(self.shop_manager.sales_file)
                today_sales = sales_df[sales_df['Date'] == today]
                
                if not today_sales.empty:
                    # Load inventory to get MRP data
                    inventory_df = pd.read_csv(self.shop_manager.inventory_file)
                    
                    # Add MRP and Profit columns
                    enhanced_sales = today_sales.copy()
                    enhanced_sales['MRP'] = 0.0
                    enhanced_sales['Profit'] = 0.0
                    
                    # Calculate MRP and Profit for each transaction
                    for idx, row in enhanced_sales.iterrows():
                        product_name = row['Product_Name']
                        unit_price = row['Unit_Price']
                        quantity_sold = row['Quantity_Sold']
                        
                        # Find product in inventory
                        product_match = inventory_df[inventory_df['Product_Name'] == product_name]
                        if not product_match.empty:
                            mrp = product_match.iloc[0]['MRP']
                            # Profit = (MRP - Unit_Price) * Quantity_Sold (as requested by user)
                            profit = (mrp - unit_price) * quantity_sold
                            
                            enhanced_sales.at[idx, 'MRP'] = mrp
                            enhanced_sales.at[idx, 'Profit'] = profit
                    
                    # Reorder columns to put MRP and Profit after Unit_Price
                    column_order = [
                        'Transaction_ID', 'Date', 'Time', 'Customer_Name', 'Customer_Phone',
                        'Product_Name', 'Quantity_Sold', 'Unit_Price', 'MRP', 'Total_Amount', 
                        'Payment_Method', 'Discount', 'Final_Amount', 'Profit'
                    ]
                    
                    # Ensure all columns exist
                    for col in column_order:
                        if col not in enhanced_sales.columns:
                            enhanced_sales[col] = 0.0
                    
                    enhanced_sales = enhanced_sales[column_order]
                    
                    # Create enhanced report
                    report_file = f"data/daily_report_{today}.xlsx"
                    enhanced_sales.to_excel(report_file, index=False)
                    
                    messagebox.showinfo("Success", 
                                      f"Enhanced sales report generated: {report_file}\n"
                                      f"Added columns: MRP and Profit\n"
                                      f"Transactions: {len(enhanced_sales)}")
                else:
                    messagebox.showinfo("Info", "No sales data for today")
            else:
                messagebox.showinfo("Info", "No sales data available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate sales report: {str(e)}")
    
    def backup_data(self):
        """Backup all data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = filedialog.asksaveasfilename(
                title="Save Backup As",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if backup_file:
                # Create backup with multiple sheets
                with pd.ExcelWriter(backup_file) as writer:
                    # Backup inventory
                    inventory_df = pd.read_csv(self.shop_manager.inventory_file)
                    inventory_df.to_excel(writer, sheet_name='Inventory', index=False)
                    
                    # Backup sales
                    if os.path.exists(self.shop_manager.sales_file):
                        sales_df = pd.read_csv(self.shop_manager.sales_file)
                        sales_df.to_excel(writer, sheet_name='Sales', index=False)
                    
                    # Backup customers
                    customers_file = 'data/customers.json'
                    if os.path.exists(customers_file):
                        with open(customers_file, 'r') as f:
                            customers_data = json.load(f)
                        if customers_data:
                            customers_df = pd.DataFrame(customers_data)
                            customers_df.to_excel(writer, sheet_name='Customers', index=False)
                
                messagebox.showinfo("Success", f"Backup created: {backup_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def generate_stock_report(self):
        """Generate stock report"""
        messagebox.showinfo("Stock Report", "Stock report generation will be implemented in the next version.")
    
    def generate_customer_report(self):
        """Generate customer report"""
        messagebox.showinfo("Customer Report", "Customer report generation will be implemented in the next version.")
    
    def show_quick_report(self):
        """Show quick daily report"""
        self.update_daily_summary()
        self.notebook.select(3)  # Switch to reports tab
        messagebox.showinfo("Quick Report", "Daily summary updated! Check the Reports tab for details.")
    
    def import_data(self):
        """Import data from file"""
        messagebox.showinfo("Import Data", "Data import functionality will be implemented in the next version.")
    
    def export_data(self):
        """Export data to Excel"""
        try:
            export_file = filedialog.asksaveasfilename(
                title="Export Data As",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if export_file:
                # Export inventory to Excel
                inventory_file = r"c:\workstation\adhoc_works\shop\inventory_master.csv"
                df = pd.read_csv(inventory_file)
                df.to_excel(export_file, index=False)
                messagebox.showinfo("Success", f"Data exported to: {export_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def reset_system(self):
        """Reset system to original state"""
        if messagebox.askyesno("Confirm Reset", 
                              "This will reset the system to original state and clear all sales data.\n"
                              "Are you sure you want to continue?"):
            try:
                # Run reset using existing reset functionality
                os.system(r'python "c:\workstation\adhoc_works\shop\reset_system_simple.py"')
                messagebox.showinfo("Success", "System reset completed!")
                self.refresh_all_data()
            except Exception as e:
                messagebox.showerror("Error", f"Reset failed: {str(e)}")
    
    def load_barcode_inventory(self):
        """Load inventory data for barcode manager"""
        try:
            self.barcode_df = pd.read_csv(self.inventory_file, dtype={'Barcode': str})
            self.barcode_df['Barcode'] = self.barcode_df['Barcode'].fillna('')
            # Clean up barcode format - remove .0 if present
            self.barcode_df['Barcode'] = self.barcode_df['Barcode'].str.replace('.0', '', regex=False).str.strip()
            self.filter_barcode_products()
            self.barcode_status_var.set(f"Loaded {len(self.barcode_df)} products")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {str(e)}")
            self.barcode_status_var.set("Error loading inventory")
    
    def filter_barcode_products(self, *args):
        """Filter products based on search criteria"""
        if self.barcode_df is None:
            return
        
        search_term = self.barcode_search_var.get().lower()
        
        # Start with all products or apply current filter
        if self.barcode_current_filter == 'with_barcodes':
            filtered_df = self.barcode_df[self.barcode_df['Barcode'].str.strip() != '']
        elif self.barcode_current_filter == 'without_barcodes':
            filtered_df = self.barcode_df[self.barcode_df['Barcode'].str.strip() == '']
        else:
            filtered_df = self.barcode_df.copy()
        
        # Apply search filter
        if search_term:
            mask = filtered_df['Product_Name'].str.lower().str.contains(search_term, na=False)
            filtered_df = filtered_df[mask]
        
        self.barcode_filtered_df = filtered_df
        self.update_barcode_tree()
    
    def update_barcode_tree(self):
        """Update the product tree view"""
        for item in self.barcode_tree.get_children():
            self.barcode_tree.delete(item)
        
        if self.barcode_filtered_df is not None:
            for _, row in self.barcode_filtered_df.iterrows():
                barcode_display = row['Barcode'] if row['Barcode'] and row['Barcode'].strip() else "No Barcode"
                self.barcode_tree.insert('', 'end', values=(
                    row['Sr_No'],
                    row['Product_Name'],
                    int(row['Quantity']),
                    f"₹{row['MRP']:.2f}",
                    f"₹{row['Cost_Price']:.2f}",
                    barcode_display
                ))
    
    def show_all_barcode_products(self):
        """Show all products"""
        self.barcode_current_filter = 'all'
        self.filter_barcode_products()
        self.barcode_status_var.set("Showing all products")
    
    def show_with_barcodes(self):
        """Show only products with barcodes"""
        self.barcode_current_filter = 'with_barcodes'
        self.filter_barcode_products()
        count = len(self.barcode_filtered_df) if self.barcode_filtered_df is not None else 0
        self.barcode_status_var.set(f"Showing {count} products with barcodes")
    
    def show_without_barcodes(self):
        """Show only products without barcodes"""
        self.barcode_current_filter = 'without_barcodes'
        self.filter_barcode_products()
        count = len(self.barcode_filtered_df) if self.barcode_filtered_df is not None else 0
        self.barcode_status_var.set(f"Showing {count} products without barcodes")
    
    def assign_barcode_to_selected(self, event=None):
        """Assign barcode to selected product"""
        selected_items = self.barcode_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a product first!")
            # Auto-focus for next attempt
            self.barcode_assign_entry.focus_set()
            return
        
        barcode = self.barcode_assign_var.get().strip()
        if not barcode:
            messagebox.showwarning("Warning", "Please scan or enter a barcode!")
            # Auto-focus for next attempt
            self.barcode_assign_entry.focus_set()
            return
        
        # Check if barcode already exists
        if not self.barcode_df[self.barcode_df['Barcode'] == barcode].empty:
            existing_product = self.barcode_df[self.barcode_df['Barcode'] == barcode]['Product_Name'].iloc[0]
            messagebox.showerror("Error", f"Barcode '{barcode}' is already assigned to '{existing_product}'!")
            # Clear and refocus for next attempt
            self.barcode_assign_var.set("")
            self.barcode_assign_entry.focus_set()
            return
        
        # Get selected product
        item = selected_items[0]
        product_id = self.barcode_tree.item(item, 'values')[0]
        product_name = self.barcode_tree.item(item, 'values')[1]
        
        try:
            # Update dataframe
            self.barcode_df.loc[self.barcode_df['Sr_No'] == float(product_id), 'Barcode'] = barcode
            
            # Save to CSV
            self.barcode_df.to_csv(self.inventory_file, index=False)
            
            # Clear entry and refresh
            self.barcode_assign_var.set("")
            self.filter_barcode_products()
            
            # Reload main inventory if it exists
            if hasattr(self, 'load_inventory'):
                self.load_inventory()
            
            # Success feedback - no popup, just status update
            self.barcode_status_var.set(f"✅ BEEP! Barcode '{barcode}' assigned to '{product_name}'")
            
            # Auto-focus for next barcode assignment
            self.barcode_assign_entry.focus_set()
            
            # Auto-select next product without barcode for continuous workflow
            self.auto_select_next_unassigned_product()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign barcode: {str(e)}")
            # Auto-focus for retry
            self.barcode_assign_entry.focus_set()
    
    def remove_barcode_from_selected(self):
        """Remove barcode from selected product"""
        selected_items = self.barcode_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a product first!")
            return
        
        # Get selected product
        item = selected_items[0]
        product_id = self.barcode_tree.item(item, 'values')[0]
        product_name = self.barcode_tree.item(item, 'values')[1]
        current_barcode = self.barcode_tree.item(item, 'values')[5]
        
        if current_barcode == "No Barcode":
            messagebox.showinfo("Info", "This product doesn't have a barcode to remove!")
            return
        
        if messagebox.askyesno("Confirm", f"Remove barcode '{current_barcode}' from '{product_name}'?"):
            try:
                # Update dataframe
                self.barcode_df.loc[self.barcode_df['Sr_No'] == float(product_id), 'Barcode'] = ''
                
                # Save to CSV
                self.barcode_df.to_csv(self.inventory_file, index=False)
                
                # Refresh display
                self.filter_barcode_products()
                
                # Reload main inventory if it exists
                if hasattr(self, 'load_inventory'):
                    self.load_inventory()
                
                messagebox.showinfo("Success", f"Barcode removed from '{product_name}'!")
                self.barcode_status_var.set(f"Removed barcode from {product_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove barcode: {str(e)}")

    def on_barcode_product_select(self, event):
        """Handle product selection - auto focus barcode entry for quick scanning"""
        selected_items = self.barcode_tree.selection()
        if selected_items:
            # Get selected product info
            item = selected_items[0]
            product_name = self.barcode_tree.item(item, 'values')[1]
            current_barcode = self.barcode_tree.item(item, 'values')[5]
            
            # Clear previous barcode entry
            self.barcode_assign_var.set("")
            
            # Auto-focus the barcode entry for quick scanning
            self.barcode_assign_entry.focus_set()
            
            # Update status to guide user
            if current_barcode == "No Barcode":
                self.barcode_status_var.set(f"📱 Ready to scan barcode for: {product_name}")
            else:
                self.barcode_status_var.set(f"📱 Current barcode: {current_barcode} | Scan new barcode to replace")

    def auto_select_next_unassigned_product(self):
        """Auto-select next product without barcode for continuous workflow"""
        try:
            # Find next product without barcode in current view
            for item in self.barcode_tree.get_children():
                barcode_value = self.barcode_tree.item(item, 'values')[5]
                if barcode_value == "No Barcode":
                    # Select this item
                    self.barcode_tree.selection_set(item)
                    self.barcode_tree.see(item)  # Scroll to make it visible
                    
                    # Update status
                    product_name = self.barcode_tree.item(item, 'values')[1]
                    self.barcode_status_var.set(f"📱 Next product ready: {product_name}")
                    return
            
            # If no unassigned products found, show completion message
            self.barcode_status_var.set("🎉 All visible products have barcodes assigned!")
            
        except Exception as e:
            # Silently continue if there's an error
            pass

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

class ProductDialog:
    """Dialog for adding/editing products"""
    def __init__(self, parent, title):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on screen
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        self.result = None
        
        # Available categories
        self.categories = [
            "General", "Beverages", "Biscuits", "Confectionery", 
            "Instant Food", "Oils & Ghee", "Food Products", 
            "Health Drinks", "Personal Care", "Hair Care", 
            "Skin Care", "Fragrance", "Detergents", "Cleaners", 
            "Pest Control", "Health Care", "Personal Hygiene", "Batteries"
        ]
        
        # Create form
        ttk.Label(self.dialog, text="Product Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Category:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.category_var = tk.StringVar(value="General")
        category_combo = ttk.Combobox(self.dialog, textvariable=self.category_var, 
                                     values=self.categories, state="readonly", width=27)
        category_combo.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Cost Price:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.cost_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.cost_var, width=30).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="MRP:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.mrp_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.mrp_var, width=30).grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Initial Quantity:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        self.quantity_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.quantity_var, width=30).grid(row=4, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        try:
            if not self.name_var.get().strip():
                messagebox.showerror("Error", "Product name is required")
                return
                
            self.result = {
                'name': self.name_var.get().strip(),
                'category': self.category_var.get(),
                'cost_price': float(self.cost_var.get()),
                'mrp': float(self.mrp_var.get()),
                'quantity': int(self.quantity_var.get())
            }
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
    
    def cancel(self):
        self.dialog.destroy()

class CheckoutDialog:
    """Dialog for checkout with customer information and receipt options"""
    def __init__(self, parent, title, cart_total):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on screen
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        self.result = None
        self.action = None  # 'save_print', 'show_receipt', or 'cancel'
        
        # Header
        header_frame = ttk.Frame(self.dialog)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ttk.Label(header_frame, text="💳 Checkout - Customer Information", 
                 font=("Arial", 12, "bold")).pack()
        ttk.Label(header_frame, text=f"Total Amount: ₹{cart_total:.2f}", 
                 font=("Arial", 10), foreground="green").pack()
        
        # Customer form
        form_frame = ttk.Frame(self.dialog)
        form_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ttk.Label(form_frame, text="Customer Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.focus_set()  # Auto-focus for quick entry
        
        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.phone_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email (Optional):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Save & Print Receipt button (prominent)
        save_print_btn = ttk.Button(button_frame, text="💾 Save & Print Receipt", 
                                   command=self.save_and_print, 
                                   style="SavePrint.TButton")
        save_print_btn.pack(side=tk.LEFT, padx=5)
        
        # Show Receipt button
        show_receipt_btn = ttk.Button(button_frame, text="👁️ Show Receipt", 
                                     command=self.show_receipt)
        show_receipt_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(button_frame, text="❌ Cancel", 
                               command=self.cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure style for save & print button
        style = ttk.Style()
        style.configure("SavePrint.TButton", 
                       font=("Arial", 9, "bold"))
        
        # Bind Enter key to save & print for quick checkout
        self.dialog.bind('<Return>', lambda e: self.save_and_print())
    
    def save_and_print(self):
        """Save transaction and print receipt directly"""
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Customer name is required")
            return
        
        self.result = {
            'name': self.name_var.get().strip(),
            'phone': self.phone_var.get().strip(),
            'email': self.email_var.get().strip()
        }
        self.action = 'save_print'
        self.dialog.destroy()
    
    def show_receipt(self):
        """Save transaction and show receipt preview"""
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Customer name is required")
            return
        
        self.result = {
            'name': self.name_var.get().strip(),
            'phone': self.phone_var.get().strip(),
            'email': self.email_var.get().strip()
        }
        self.action = 'show_receipt'
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the checkout"""
        self.action = 'cancel'
        self.dialog.destroy()

class CustomerDialog:
    """Dialog for adding/editing customers"""
    def __init__(self, parent, title):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on screen
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        self.result = None
        
        # Create form
        ttk.Label(self.dialog, text="Customer Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Phone:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.phone_var, width=30).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Email:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.email_var, width=30).grid(row=2, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Customer name is required")
            return
        
        self.result = {
            'name': self.name_var.get().strip(),
            'phone': self.phone_var.get().strip(),
            'email': self.email_var.get().strip()
        }
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

def main():
    """Main function to start the GUI"""
    try:
        # Check if required modules exist
        required_files = [
            'sales_billing.py',
            'stock_manager.py', 
            'customer_manager.py',
            'reports_analytics.py',
            'inventory_master.csv'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print("Missing required files:")
            for file in missing_files:
                print(f"  - {file}")
            print("\nPlease ensure all system files are present.")
            return
        
        # Start GUI
        app = BaujiTradersGUI()
        app.run()
        
    except ImportError as e:
        print(f"Missing required module: {e}")
        print("Please install required packages:")
        print("  pip install ttkthemes")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
