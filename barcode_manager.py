#!/usr/bin/env python3
"""
Barcode Manager - Tool to assign barcodes to products
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json

class BarcodeManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Barcode Manager - Assign Barcodes to Products")
        self.root.geometry("1000x600")
        
        self.inventory_file = "inventory_master.csv"
        self.df = None
        self.filtered_df = None
        self.current_filter = 'all'  # Track current filter state
        
        self.setup_ui()
        self.load_inventory()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Search Products", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_products)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(search_frame, text="Show All", command=self.show_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Show With Barcodes", command=self.show_with_barcodes).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Show Without Barcodes", command=self.show_without_barcodes).pack(side=tk.LEFT, padx=5)
        
        # Products tree
        tree_frame = ttk.LabelFrame(main_frame, text="Products", padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview with scrollbar
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_container, columns=('ID', 'Product', 'Stock', 'MRP', 'Cost', 'Barcode'), show='headings', height=15)
        
        # Column headers
        self.tree.heading('ID', text='ID')
        self.tree.heading('Product', text='Product Name')
        self.tree.heading('Stock', text='Stock')
        self.tree.heading('MRP', text='MRP')
        self.tree.heading('Cost', text='Cost')
        self.tree.heading('Barcode', text='Barcode')
        
        # Column widths
        self.tree.column('ID', width=50)
        self.tree.column('Product', width=400)
        self.tree.column('Stock', width=80)
        self.tree.column('MRP', width=80)
        self.tree.column('Cost', width=80)
        self.tree.column('Barcode', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Barcode assignment frame
        barcode_frame = ttk.LabelFrame(main_frame, text="Assign Barcode", padding=10)
        barcode_frame.pack(fill=tk.X)
        
        ttk.Label(barcode_frame, text="Scan or enter barcode:").pack(side=tk.LEFT)
        self.barcode_var = tk.StringVar()
        barcode_entry = ttk.Entry(barcode_frame, textvariable=self.barcode_var, width=20)
        barcode_entry.pack(side=tk.LEFT, padx=(5, 10))
        barcode_entry.bind('<Return>', self.assign_barcode)
        
        ttk.Button(barcode_frame, text="Assign to Selected Product", 
                  command=self.assign_barcode).pack(side=tk.LEFT, padx=5)
        ttk.Button(barcode_frame, text="Remove Barcode", 
                  command=self.remove_barcode).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue")
        status_label.pack(pady=5)
        
        # Focus on barcode entry
        barcode_entry.focus_set()
    
    def load_inventory(self):
        """Load inventory from CSV"""
        try:
            # Force barcode column to be read as string
            dtype_dict = {'Barcode': str}
            self.df = pd.read_csv(self.inventory_file, dtype=dtype_dict)
            
            # Replace 'nan' strings with empty strings and handle NaN values
            self.df['Barcode'] = self.df['Barcode'].replace('nan', '').fillna('')
            
            self.filtered_df = self.df.copy()
            self.refresh_tree()
            self.status_var.set(f"Loaded {len(self.df)} products")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {e}")
            print(f"DEBUG: Load error: {e}")
    
    def refresh_tree(self):
        """Refresh the product tree"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add products
        for _, row in self.filtered_df.iterrows():
            # Get barcode value and handle all edge cases
            barcode_value = str(row.get('Barcode', '')).strip()
            if barcode_value == 'nan' or barcode_value == '' or pd.isna(row.get('Barcode')):
                barcode_display = ''
            else:
                barcode_display = barcode_value
                
            self.tree.insert('', tk.END, values=(
                row['Sr_No'],
                row['Product_Name'],
                row['Quantity'],
                f"₹{row['MRP']:.2f}",
                f"₹{row['Cost_Price']:.2f}",
                barcode_display
            ))
    
    def filter_products(self, *args):
        """Filter products based on search"""
        search_term = self.search_var.get().lower()
        if search_term:
            self.current_filter = 'search'
            self.filtered_df = self.df[
                self.df['Product_Name'].str.lower().str.contains(search_term, na=False)
            ]
        else:
            self.current_filter = 'all'
            self.filtered_df = self.df.copy()
        self.refresh_tree()
    
    def show_all(self):
        """Show all products"""
        self.current_filter = 'all'
        self.filtered_df = self.df.copy()
        self.search_var.set("")
        self.refresh_tree()
    
    def show_with_barcodes(self):
        """Show only products with barcodes"""
        self.current_filter = 'with_barcodes'
        
        # Filter for products that have actual barcode values (not empty, not 'nan')
        mask = (self.df['Barcode'] != '') & (self.df['Barcode'] != 'nan') & (self.df['Barcode'].notna())
        self.filtered_df = self.df[mask]
        
        self.refresh_tree()
        self.status_var.set(f"Showing {len(self.filtered_df)} products with barcodes")
    
    def show_without_barcodes(self):
        """Show only products without barcodes"""
        self.current_filter = 'without_barcodes'
        # Show products without barcode values (empty or 'nan')
        mask = (self.df['Barcode'] == '') | (self.df['Barcode'] == 'nan') | (self.df['Barcode'].isna())
        self.filtered_df = self.df[mask]
        self.refresh_tree()
        self.status_var.set(f"Showing {len(self.filtered_df)} products without barcodes")
    
    def assign_barcode(self, event=None):
        """Assign barcode to selected product"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first")
            return
        
        barcode = self.barcode_var.get().strip()
        if not barcode:
            messagebox.showwarning("Warning", "Please enter a barcode")
            return
        
        try:
            # Get selected product
            item = self.tree.item(selection[0])
            product_id = item['values'][0]
            product_name = item['values'][1]
            
            # Check if barcode already exists
            existing = self.df[self.df['Barcode'] == barcode]
            if not existing.empty:
                existing_product = existing.iloc[0]['Product_Name']
                if not messagebox.askyesno("Barcode Exists", 
                    f"Barcode {barcode} is already assigned to:\n{existing_product}\n\n"
                    f"Do you want to reassign it to:\n{product_name}?"):
                    return
                # Remove from existing product
                self.df.loc[self.df['Barcode'] == barcode, 'Barcode'] = ''
            
            # Load fresh dataframe to avoid any state issues
            df_fresh = pd.read_csv(self.inventory_file, dtype={'Barcode': str})
            df_fresh['Barcode'] = df_fresh['Barcode'].replace('nan', '').fillna('')
            
            # Convert product_id to float to match Sr_No column
            try:
                product_id_float = float(product_id)
            except:
                messagebox.showerror("Error", f"Invalid product ID: {product_id}")
                return
            
            # Check if product exists before assignment
            matching_products = df_fresh[df_fresh['Sr_No'] == product_id_float]
            
            if matching_products.empty:
                messagebox.showerror("Error", f"Product ID {product_id} not found in inventory")
                return
            
            # Assign barcode
            df_fresh.loc[df_fresh['Sr_No'] == product_id_float, 'Barcode'] = barcode
            
            # Save immediately
            df_fresh.to_csv(self.inventory_file, index=False)
            
            # Reload the dataframe to ensure consistency
            self.load_inventory()
            print(f"DEBUG: Reloaded inventory")
            
            # Refresh display based on current filter
            if hasattr(self, 'current_filter'):
                if self.current_filter == 'with_barcodes':
                    self.show_with_barcodes()
                elif self.current_filter == 'without_barcodes':
                    self.show_without_barcodes()
                else:
                    self.filter_products()
            else:
                self.filter_products()
            
            # Clear barcode entry
            self.barcode_var.set("")
            
            self.status_var.set(f"✅ Assigned barcode {barcode} to {product_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign barcode: {e}")
    
    def remove_barcode(self):
        """Remove barcode from selected product"""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first")
            return
        
        try:
            # Get selected product
            item = self.tree.item(selection[0])
            values = item['values']
            
            product_id = values[0]
            product_name = values[1]
            current_barcode = str(values[5]).strip()
            
            # Simple barcode validation - just check if it's not empty or 'nan'
            if not current_barcode or current_barcode == '' or current_barcode == 'nan':
                messagebox.showinfo("Info", "This product doesn't have a barcode assigned")
                return
            
            if messagebox.askyesno("Confirm", f"Remove barcode {current_barcode} from {product_name}?"):
                # Convert product_id to float to match Sr_No column (same fix as assign_barcode)
                try:
                    product_id_float = float(product_id)
                except:
                    messagebox.showerror("Error", f"Invalid product ID: {product_id}")
                    return
                
                # Load and clean data
                df = pd.read_csv(self.inventory_file, dtype={'Barcode': str})
                df['Barcode'] = df['Barcode'].replace('nan', '').fillna('')
                
                # Check if product exists before removal
                matching_products = df[df['Sr_No'] == product_id_float]
                
                if matching_products.empty:
                    messagebox.showerror("Error", f"Product ID {product_id} not found in inventory")
                    return
                
                # Remove barcode
                df.loc[df['Sr_No'] == product_id_float, 'Barcode'] = ''
                
                # Save
                df.to_csv(self.inventory_file, index=False)
                
                # Reload data and refresh display
                self.load_inventory()
                
                # Apply current filter
                if hasattr(self, 'current_filter') and self.current_filter == 'with_barcodes':
                    self.show_with_barcodes()
                elif hasattr(self, 'current_filter') and self.current_filter == 'without_barcodes':
                    self.show_without_barcodes()
                else:
                    self.show_all()
                
                self.status_var.set(f"✅ Removed barcode from {product_name}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove barcode: {e}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BarcodeManager()
    app.run()
