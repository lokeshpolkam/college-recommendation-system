import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, Listbox, Button, Label, SINGLE, messagebox
import shutil
import glob

class DataSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("College Data Selector")
        self.root.geometry("600x500")
        
        # Use your specific data directory
        self.data_folder = r"C:\college recomendation sysstem\data"
        
        # Create data folder if it doesn't exist
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            print(f"Created data directory: {self.data_folder}")
            
        self.selected_files = []
        self.setup_ui()
        self.refresh_file_list()
        
    def setup_ui(self):
        Label(self.root, text="Available Datasets:", font=("Arial", 12)).pack(pady=10)
        
        self.file_listbox = Listbox(self.root, selectmode=tk.MULTIPLE, width=70, height=15)
        self.file_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        Button(button_frame, text="Refresh List", command=self.refresh_file_list).pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Select Dataset(s)", command=self.select_datasets).pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Add New Dataset", command=self.add_dataset).pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Process All Data", command=self.process_all_data).pack(side=tk.LEFT, padx=5)
        
        self.status_label = Label(self.root, text="No datasets selected", fg="red", wraplength=500)
        self.status_label.pack(pady=10)
        
    def refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        try:
            # Get all Excel and CSV files in the directory and subdirectories
            excel_files = glob.glob(os.path.join(self.data_folder, "**", "*.xlsx"), recursive=True)
            excel_files += glob.glob(os.path.join(self.data_folder, "**", "*.xls"), recursive=True)
            csv_files = glob.glob(os.path.join(self.data_folder, "**", "*.csv"), recursive=True)
            
            all_files = excel_files + csv_files
            
            if not all_files:
                self.file_listbox.insert(tk.END, "No datasets found. Please add one.")
            else:
                for file_path in all_files:
                    # Display relative path from data folder
                    rel_path = os.path.relpath(file_path, self.data_folder)
                    self.file_listbox.insert(tk.END, rel_path)
        except Exception as e:
            self.file_listbox.insert(tk.END, f"Error reading directory: {str(e)}")
                
    def select_datasets(self):
        selections = self.file_listbox.curselection()
        if selections:
            self.selected_files = [self.file_listbox.get(i) for i in selections]
            status_text = f"Selected {len(self.selected_files)} dataset(s): {', '.join(self.selected_files)}"
            self.status_label.config(text=status_text, fg="green")
            
            # Save selection for other scripts
            with open("selected_datasets.txt", "w") as f:
                for file in self.selected_files:
                    f.write(file + "\n")
        else:
            self.status_label.config(text="Please select at least one dataset first", fg="red")
            
    def process_all_data(self):
        """Process all datasets in the directory"""
        try:
            all_files = []
            excel_files = glob.glob(os.path.join(self.data_folder, "**", "*.xlsx"), recursive=True)
            excel_files += glob.glob(os.path.join(self.data_folder, "**", "*.xls"), recursive=True)
            csv_files = glob.glob(os.path.join(self.data_folder, "**", "*.csv"), recursive=True)
            
            all_files = excel_files + csv_files
            
            if not all_files:
                messagebox.showinfo("No Data", "No datasets found to process.")
                return
                
            # Save all files for processing
            with open("selected_datasets.txt", "w") as f:
                for file_path in all_files:
                    rel_path = os.path.relpath(file_path, self.data_folder)
                    f.write(rel_path + "\n")
                    
            self.status_label.config(text=f"Processing all {len(all_files)} datasets", fg="blue")
            messagebox.showinfo("Success", f"All {len(all_files)} datasets selected for processing.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process all data: {str(e)}")
            
    def add_dataset(self):
        file_paths = filedialog.askopenfilenames(
            title="Select College Data Files",
            filetypes=[("Excel files", "*.xlsx"), ("Excel files", "*.xls"), ("CSV files", "*.csv")]
        )
        
        if file_paths:
            success_count = 0
            for file_path in file_paths:
                try:
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(self.data_folder, filename)
                    
                    # Copy file to data folder
                    shutil.copy2(file_path, dest_path)
                    success_count += 1
                except Exception as e:
                    print(f"Error copying {file_path}: {str(e)}")
            
            self.refresh_file_list()
            self.status_label.config(text=f"Added {success_count} of {len(file_paths)} files", fg="blue")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataSelector(root)
    root.mainloop()
