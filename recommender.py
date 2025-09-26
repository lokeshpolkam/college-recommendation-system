import pandas as pd
import numpy as np
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
import re

class CollegeRecommender:
    def __init__(self, root):
        self.root = root
        self.root.title("College Recommendation System")
        self.root.geometry("900x700")
        
        self.model = None
        self.available_categories = set()
        self.available_branches = set()
        self.load_model()
        self.setup_ui()
        
    def load_model(self):
        """Load the most recent trained model"""
        models_dir = "models"
        if not os.path.exists(models_dir):
            messagebox.showerror("Error", "No models found. Please run trainer.py first.")
            return False
            
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.json')]
        if not model_files:
            messagebox.showerror("Error", "No models found. Please run trainer.py first.")
            return False
            
        # Use the college branch model
        model_path = os.path.join(models_dir, "college_branch_model.json")
        
        if not os.path.exists(model_path):
            messagebox.showerror("Error", "College branch model not found. Please run trainer.py first.")
            return False
            
        try:
            with open(model_path, "r") as f:
                self.model = json.load(f)
                
            # Extract available categories and branches from the model
            for college_branch, categories in self.model.items():
                self.available_categories.update(categories.keys())
                
                # Extract branch from college_branch string
                if " - " in college_branch:
                    branch = college_branch.split(" - ")[1]
                    self.available_branches.add(branch)
                
            print(f"Loaded model with {len(self.model)} college-branch combinations")
            print("Available categories:", sorted(self.available_categories))
            print("Available branches:", sorted(self.available_branches))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            return False
            
        return True
        
    def setup_ui(self):
        """Set up the user interface"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        ttk.Label(main_frame, text="College Recommendation System", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10)
        
        # Input fields
        ttk.Label(main_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, width=25)
        category_combo['values'] = sorted(self.available_categories) if self.available_categories else ['OPEN', 'OBC-NCL', 'SC', 'ST', 'EWS']
        category_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        if 'OPEN' in self.available_categories:
            category_combo.set('OPEN')
        elif self.available_categories:
            category_combo.set(sorted(self.available_categories)[0])
        
        ttk.Label(main_frame, text="JEE Rank:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.rank_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.rank_var, width=25).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="12th Percentage:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.twelveth_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.twelveth_var, width=25).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="Preferred Branch:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.branch_var = tk.StringVar()
        branch_combo = ttk.Combobox(main_frame, textvariable=self.branch_var, width=25)
        
        # Get available branches or use defaults
        branch_values = ['Any'] + sorted(self.available_branches) if self.available_branches else [
            'Any', 'Computer Science', 'Electrical', 'Mechanical', 'Electronics', 'Civil'
        ]
        branch_combo['values'] = branch_values
        branch_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        branch_combo.set('Any')
        
        ttk.Label(main_frame, text="Round:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.round_var = tk.StringVar(value="1")
        round_combo = ttk.Combobox(main_frame, textvariable=self.round_var, width=25)
        round_combo['values'] = ('1', '2', '3', '4', '5', '6')
        round_combo.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Get Recommendations", command=self.get_recommendations).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Debug Model", command=self.debug_model).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Show All Branches", command=self.show_all_branches).pack(side=tk.LEFT, padx=10)
        
        # Results
        ttk.Label(main_frame, text="Recommendations:", font=("Arial", 12, "bold")).grid(
            row=7, column=0, columnspan=2, pady=(20, 5), sticky=tk.W)
        
        # Treeview for results
        columns = ("College", "Branch", "Category", "Min Rank", "Max Rank", "Chance")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Set column widths
        self.tree.column("College", width=250)
        self.tree.column("Branch", width=150)
        self.tree.column("Category", width=100)
        self.tree.column("Min Rank", width=80)
        self.tree.column("Max Rank", width=80)
        self.tree.column("Chance", width=80)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=8, column=2, sticky=(tk.N, tk.S))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to get recommendations", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Configure grid weights for resizing
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def get_recommendations(self):
        """Generate recommendations based on user input"""
        if not self.model:
            messagebox.showerror("Error", "No model loaded. Please train a model first.")
            return
            
        try:
            # Get user inputs
            category = self.category_var.get().strip().upper()
            jee_rank = int(self.rank_var.get().strip())
            branch_pref = self.branch_var.get().strip()
            
            # Clear previous results
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Generate recommendations
            recommendations = []
            
            for college_branch, categories in self.model.items():
                # Split college and branch
                if " - " in college_branch:
                    college, branch = college_branch.split(" - ", 1)
                else:
                    college, branch = college_branch, "Unknown Branch"
                
                # Filter by branch preference
                if branch_pref != "Any" and branch_pref.lower() not in branch.lower():
                    continue
                    
                if category in categories:
                    min_rank = categories[category]['min_rank']
                    max_rank = categories[category]['max_rank']
                    
                    # Calculate chance of admission
                    if jee_rank <= min_rank:
                        chance = "High"
                    elif jee_rank <= max_rank:
                        chance = "Medium"
                    else:
                        chance = "Low"
                        
                    recommendations.append((college, branch, category, min_rank, max_rank, chance))
            
            # Sort by min rank (better colleges first)
            recommendations.sort(key=lambda x: x[3])
            
            # Add to treeview
            for rec in recommendations:
                self.tree.insert("", "end", values=rec)
                
            if not recommendations:
                self.status_label.config(text="No recommendations found. Try different criteria.", foreground="red")
                messagebox.showinfo("No Results", 
                    "No colleges found matching your criteria.\n\n"
                    f"Category: {category}\n"
                    f"JEE Rank: {jee_rank}\n"
                    f"Branch: {branch_pref}\n\n"
                    "Try adjusting your criteria or check if your category exists in the model.")
            else:
                self.status_label.config(text=f"Found {len(recommendations)} recommendations", foreground="green")
                
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid JEE rank (number).")
            self.status_label.config(text="Error: Please enter a valid JEE rank", foreground="red")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}", foreground="red")
            
    def debug_model(self):
        """Show debug information about the model"""
        if not self.model:
            messagebox.showerror("Error", "No model loaded.")
            return
            
        debug_text = f"Model contains {len(self.model)} college-branch combinations\n"
        debug_text += f"Available categories: {sorted(self.available_categories)}\n"
        debug_text += f"Available branches: {sorted(self.available_branches)}\n\n"
        
        # Show sample colleges
        debug_text += "Sample colleges:\n"
        for i, college_branch in enumerate(list(self.model.keys())[:10]):
            college, branch = college_branch.split(" - ", 1) if " - " in college_branch else (college_branch, "Unknown")
            debug_text += f"{i+1}. {college} - {branch}\n"
            for category, data in list(self.model[college_branch].items())[:2]:
                debug_text += f"   {category}: {data['min_rank']} - {data['max_rank']}\n"
        
        messagebox.showinfo("Model Debug Info", debug_text)
    
    def show_all_branches(self):
        """Show all available branches in the model"""
        if not self.available_branches:
            messagebox.showinfo("Branches", "No branches found in the model.")
            return
            
        branches_text = "All available branches:\n\n"
        for i, branch in enumerate(sorted(self.available_branches), 1):
            branches_text += f"{i}. {branch}\n"
        
        messagebox.showinfo("Available Branches", branches_text)
            
    def clear_form(self):
        """Clear all input fields"""
        if self.available_categories:
            if 'OPEN' in self.available_categories:
                self.category_var.set('OPEN')
            else:
                self.category_var.set(sorted(self.available_categories)[0])
        self.rank_var.set('')
        self.twelveth_var.set('')
        self.branch_var.set('Any')
        self.round_var.set('1')
        
        # Clear results
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.status_label.config(text="Ready to get recommendations", foreground="black")

if __name__ == "__main__":
    root = tk.Tk()
    app = CollegeRecommender(root)
    root.mainloop()