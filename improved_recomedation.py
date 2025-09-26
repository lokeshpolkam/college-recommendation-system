import pandas as pd
import numpy as np
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
import re
import sys

# Set stdout encoding to utf-8 to handle Unicode characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class CollegeRecommender:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 College Recommendation System 2025")
        self.root.geometry("1200x900")
        self.root.configure(bg='#0f0f23')
        
        # Configure modern style
        self.setup_style()
        
        self.model = None
        self.model_data = None
        self.available_categories = set()
        self.available_branches = set()
        self.load_model()
        self.setup_ui()
    
    def setup_style(self):
        """Configure modern dark theme styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = '#0f0f23'
        fg_color = '#ffffff'
        accent_color = '#00d4aa'
        button_color = '#1a1a2e'
        entry_color = '#16213e'
        
        # Configure styles
        style.configure('Title.TLabel', 
                       background=bg_color, 
                       foreground=accent_color, 
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Modern.TLabel', 
                       background=bg_color, 
                       foreground=fg_color, 
                       font=('Segoe UI', 11))
        
        style.configure('Modern.TFrame', 
                       background=bg_color)
        
        style.configure('Modern.TButton',
                       background=button_color,
                       foreground=fg_color,
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat',
                       borderwidth=2)
        
        style.map('Modern.TButton',
                  background=[('active', accent_color),
                             ('pressed', '#00b894')])
        
        style.configure('Modern.TCombobox',
                       background=entry_color,
                       foreground=fg_color,
                       fieldbackground=entry_color,
                       borderwidth=1,
                       relief='flat')
        
        style.configure('Modern.TEntry',
                       background=entry_color,
                       foreground=fg_color,
                       fieldbackground=entry_color,
                       borderwidth=1,
                       relief='flat')
        
        # Treeview styling
        style.configure('Modern.Treeview',
                       background='#1a1a2e',
                       foreground=fg_color,
                       fieldbackground='#1a1a2e',
                       borderwidth=0,
                       font=('Segoe UI', 10))
        
        style.configure('Modern.Treeview.Heading',
                       background=accent_color,
                       foreground='#000000',
                       font=('Segoe UI', 11, 'bold'),
                       relief='flat')
        
        style.map('Modern.Treeview',
                  background=[('selected', accent_color)],
                  foreground=[('selected', '#000000')])
    
    def vfm_to_stars(self, vfm_score):
        """Convert VFM score to star representation"""
        try:
            score = float(vfm_score)
            full_stars = int(score)
            half_star = 1 if (score - full_stars) >= 0.5 else 0
            empty_stars = 5 - full_stars - half_star
            
            star_display = "★" * full_stars
            if half_star:
                star_display += "☆"
            star_display += "☆" * empty_stars
            
            return f"{star_display} ({score:.1f})"
        except (ValueError, TypeError):
            return "☆☆☆☆☆ (3.0)"
    
    def load_model(self):
        """Load the most recent trained model"""
        models_dir = "models"
        if not os.path.exists(models_dir):
            messagebox.showerror("🚫 Error", "No models found. Please run trainer.py first.")
            return False
        
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.json')]
        if not model_files:
            messagebox.showerror("🚫 Error", "No models found. Please run trainer.py first.")
            return False
        
        # Look for the correct model file created by trainer.py
        model_path = os.path.join(models_dir, "college_recommendation_model.json")
        if not os.path.exists(model_path):
            messagebox.showerror("🚫 Error", "College recommendation model not found. Please run trainer.py first.")
            return False
        
        try:
            with open(model_path, "r", encoding='utf-8') as f:
                self.model_data = json.load(f)
            
            # Extract the actual model from the loaded data
            self.model = self.model_data.get('model', {})
            
            # Extract available categories and branches from the model
            for college_branch, data in self.model.items():
                if 'categories' in data:
                    self.available_categories.update(data['categories'].keys())
                
                if 'branch' in data:
                    self.available_branches.add(data['branch'])
                elif " - " in college_branch:
                    branch = college_branch.split(" - ")[1]
                    self.available_branches.add(branch)
            
            print(f"🎯 Loaded model with {len(self.model)} college-branch combinations")
            print("📊 Available categories:", sorted(self.available_categories))
            print("🔬 Available branches:", sorted(self.available_branches))
            
        except Exception as e:
            messagebox.showerror("🚫 Error", f"Failed to load model: {str(e)}")
            return False
        
        return True
    
    def setup_ui(self):
        """Set up the futuristic user interface"""
        main_frame = ttk.Frame(self.root, style='Modern.TFrame', padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header with gradient effect
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 30), sticky=(tk.W, tk.E))
        
        # Title with emoji
        ttk.Label(header_frame, text="🚀 AI COLLEGE PREDICTOR 2025", 
                 style='Title.TLabel').grid(row=0, column=0, pady=10)
        
        ttk.Label(header_frame, text="💡 Smart Recommendations Based on JEE Rankings & Value Analysis", 
                 style='Modern.TLabel', font=('Segoe UI', 12, 'italic')).grid(row=1, column=0, pady=(0, 10))
        
        # Input section with modern cards
        input_frame = ttk.LabelFrame(main_frame, text="📝 STUDENT PROFILE", style='Modern.TFrame', padding="20")
        input_frame.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E), padx=(0, 0))
        
        # Create two columns for inputs
        left_inputs = ttk.Frame(input_frame, style='Modern.TFrame')
        left_inputs.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 30))
        
        right_inputs = ttk.Frame(input_frame, style='Modern.TFrame')
        right_inputs.grid(row=0, column=1, sticky=(tk.W, tk.N))
        
        # Left column inputs
        ttk.Label(left_inputs, text="🎯 Category:", style='Modern.TLabel').grid(row=0, column=0, sticky=tk.W, pady=8)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(left_inputs, textvariable=self.category_var, width=20, style='Modern.TCombobox')
        category_combo['values'] = sorted(self.available_categories) if self.available_categories else ['OPEN', 'OBC-NCL', 'SC', 'ST', 'EWS']
        category_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        if 'OPEN' in self.available_categories:
            category_combo.set('OPEN')
        elif self.available_categories:
            category_combo.set(sorted(self.available_categories)[0])
        
        ttk.Label(left_inputs, text="📊 JEE Main Rank:", style='Modern.TLabel').grid(row=1, column=0, sticky=tk.W, pady=8)
        self.rank_var = tk.StringVar()
        ttk.Entry(left_inputs, textvariable=self.rank_var, width=20, style='Modern.TEntry').grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        
        ttk.Label(left_inputs, text="📈 12th Percentage:", style='Modern.TLabel').grid(row=2, column=0, sticky=tk.W, pady=8)
        self.twelveth_var = tk.StringVar()
        ttk.Entry(left_inputs, textvariable=self.twelveth_var, width=20, style='Modern.TEntry').grid(row=2, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        
        # Right column inputs
        ttk.Label(right_inputs, text="🔬 Preferred Branch:", style='Modern.TLabel').grid(row=0, column=0, sticky=tk.W, pady=8)
        self.branch_var = tk.StringVar()
        branch_combo = ttk.Combobox(right_inputs, textvariable=self.branch_var, width=25, style='Modern.TCombobox')
        
        branch_values = ['🌟 Any Branch'] + [f"🔹 {branch}" for branch in sorted(self.available_branches)] if self.available_branches else [
            '🌟 Any Branch', '🔹 Computer Science', '🔹 Electrical', '🔹 Mechanical', '🔹 Electronics', '🔹 Civil'
        ]
        
        branch_combo['values'] = branch_values
        branch_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        branch_combo.set('🌟 Any Branch')
        
        ttk.Label(right_inputs, text="🔄 Counselling Round:", style='Modern.TLabel').grid(row=1, column=0, sticky=tk.W, pady=8)
        self.round_var = tk.StringVar(value="1")
        round_combo = ttk.Combobox(right_inputs, textvariable=self.round_var, width=25, style='Modern.TCombobox')
        round_combo['values'] = ('1️⃣ Round 1', '2️⃣ Round 2', '3️⃣ Round 3', '4️⃣ Round 4', '5️⃣ Round 5', '6️⃣ Round 6')
        round_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        
        # Action buttons with modern styling
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="🎯 GET SMART RECOMMENDATIONS", 
                  command=self.get_recommendations, style='Modern.TButton', width=25).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="🔄 CLEAR ALL", 
                  command=self.clear_form, style='Modern.TButton', width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="🔧 DEBUG MODEL", 
                  command=self.debug_model, style='Modern.TButton', width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="📋 ALL BRANCHES", 
                  command=self.show_all_branches, style='Modern.TButton', width=15).pack(side=tk.LEFT, padx=10)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="🎯 AI RECOMMENDATIONS", style='Modern.TFrame', padding="15")
        results_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview for results with modern columns
        columns = ("College", "Branch", "Category", "Min Rank", "Max Rank", "Admission Chance", "Value for Money")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=18, style='Modern.Treeview')
        
        # Set column widths and alignments
        self.tree.column("College", width=250, anchor=tk.W)
        self.tree.column("Branch", width=150, anchor=tk.W)
        self.tree.column("Category", width=80, anchor=tk.CENTER)
        self.tree.column("Min Rank", width=90, anchor=tk.CENTER)
        self.tree.column("Max Rank", width=90, anchor=tk.CENTER)
        self.tree.column("Admission Chance", width=120, anchor=tk.CENTER)
        self.tree.column("Value for Money", width=180, anchor=tk.CENTER)
        
        # Set column headings with emojis
        headings = {
            "College": "🏛️ COLLEGE",
            "Branch": "🔬 BRANCH",
            "Category": "🎯 CATEGORY",
            "Min Rank": "📊 MIN RANK",
            "Max Rank": "📈 MAX RANK",
            "Admission Chance": "🎲 CHANCE",
            "Value for Money": "⭐ VALUE FOR MONEY"
        }
        
        for col in columns:
            self.tree.heading(col, text=headings[col], anchor=tk.CENTER)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        
        # Scrollbar with modern styling
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Modern status bar
        status_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        status_frame.grid(row=4, column=0, columnspan=3, pady=15, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="🚀 Ready for AI-powered recommendations!", 
                                     style='Modern.TLabel', font=('Segoe UI', 11, 'bold'))
        self.status_label.pack(side=tk.LEFT)
        
        # Configure grid weights for responsive design
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def get_recommendations(self):
        """Generate AI-powered recommendations"""
        if not self.model:
            messagebox.showerror("🚫 Error", "No AI model loaded. Please train a model first.")
            return
        
        try:
            # Get user inputs and clean them
            category = self.category_var.get().strip().upper()
            jee_rank_str = self.rank_var.get().strip()
            branch_pref = self.branch_var.get().strip()
            
            # Clean branch preference
            if branch_pref.startswith('🌟 Any'):
                branch_pref = "Any"
            elif branch_pref.startswith('🔹 '):
                branch_pref = branch_pref[2:]
            
            if not jee_rank_str:
                messagebox.showerror("⚠️ Input Required", "Please enter your JEE Main rank.")
                return
            
            jee_rank = int(jee_rank_str)
            
            if jee_rank <= 0:
                messagebox.showerror("⚠️ Invalid Input", "Please enter a valid JEE rank (positive number).")
                return
            
            # Clear previous results
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.status_label.config(text="🔄 AI analyzing your profile and generating recommendations...", 
                                   foreground='#00d4aa')
            self.root.update()
            
            # Generate recommendations
            recommendations = []
            
            for college_branch, data in self.model.items():
                college = data.get('college', 'Unknown College')
                branch = data.get('branch', 'Unknown Branch')
                vfm_score = data.get('value_for_money', 3.0)
                categories = data.get('categories', {})
                
                # Filter by branch preference
                if branch_pref != "Any" and branch_pref.lower() not in branch.lower():
                    continue
                
                if category in categories:
                    cat_data = categories[category]
                    min_rank = cat_data['min_rank']
                    max_rank = cat_data['max_rank']
                    
                    # Calculate detailed admission chances
                    if jee_rank <= min_rank:
                        chance = "🟢 HIGH"
                        chance_score = 3
                    elif jee_rank <= max_rank:
                        # Calculate medium chance percentage
                        position = (jee_rank - min_rank) / (max_rank - min_rank)
                        if position <= 0.5:
                            chance = "🟡 GOOD"
                            chance_score = 2
                        else:
                            chance = "🟠 MEDIUM"
                            chance_score = 1.5
                    else:
                        # Calculate low chance
                        overflow = (jee_rank - max_rank) / max_rank
                        if overflow <= 0.2:  # Within 20% of max rank
                            chance = "🟠 LOW"
                            chance_score = 1
                        else:
                            chance = "🔴 VERY LOW"
                            chance_score = 0.5
                    
                    # Convert VFM to stars
                    vfm_stars = self.vfm_to_stars(vfm_score)
                    
                    recommendations.append((
                        college, branch, category, 
                        f"{min_rank:,}", f"{max_rank:,}", 
                        chance, vfm_stars, 
                        chance_score, vfm_score  # For sorting
                    ))
            
            # Sort by admission chance and VFM score
            recommendations.sort(key=lambda x: (-x[7], -x[8]))  # Higher chance and VFM first
            
            # Add to treeview (exclude sorting values)
            for rec in recommendations:
                display_rec = rec[:7]  # Exclude sorting values
                self.tree.insert("", "end", values=display_rec)
            
            if not recommendations:
                self.status_label.config(text="❌ No colleges found matching your criteria. Try adjusting filters.", 
                                       foreground='#e74c3c')
                messagebox.showinfo("🔍 No Results",
                    f"No colleges found for your profile:\n\n"
                    f"📊 Category: {category}\n"
                    f"🎯 JEE Rank: {jee_rank:,}\n"
                    f"🔬 Branch: {branch_pref}\n\n"
                    f"💡 Try adjusting your criteria or check available categories.")
            else:
                high_chance = len([r for r in recommendations if '🟢 HIGH' in r[5] or '🟡 GOOD' in r[5]])
                self.status_label.config(
                    text=f"✅ Found {len(recommendations)} recommendations • {high_chance} high-probability matches", 
                    foreground='#27ae60')
        
        except ValueError:
            messagebox.showerror("⚠️ Input Error", "Please enter a valid JEE rank (numbers only).")
            self.status_label.config(text="❌ Please enter a valid numeric JEE rank", foreground='#e74c3c')
        except Exception as e:
            messagebox.showerror("🚫 System Error", f"An unexpected error occurred:\n{str(e)}")
            self.status_label.config(text=f"❌ System error: {str(e)}", foreground='#e74c3c')
    
    def debug_model(self):
        """Show detailed AI model information"""
        if not self.model:
            messagebox.showerror("🚫 Error", "No AI model loaded.")
            return
        
        debug_text = f"🤖 AI MODEL ANALYTICS\n"
        debug_text += f"{'='*50}\n\n"
        debug_text += f"📊 Total College-Branch Combinations: {len(self.model)}\n"
        debug_text += f"🎯 Available Categories: {sorted(self.available_categories)}\n"
        debug_text += f"🔬 Available Branches: {len(self.available_branches)} branches\n\n"
        
        if self.model_data and 'metadata' in self.model_data:
            metadata = self.model_data['metadata']
            debug_text += f"⏰ Model Training Time: {metadata.get('timestamp', 'Unknown')}\n"
            debug_text += f"🎯 Total Combinations: {metadata.get('total_combinations', 'Unknown')}\n"
            if 'vfm_stats' in metadata:
                vfm_stats = metadata['vfm_stats']
                debug_text += f"⭐ Average VFM Score: {vfm_stats.get('average', 0):.2f}/5.0\n"
                debug_text += f"📈 VFM Range: {vfm_stats.get('min', 0):.1f} - {vfm_stats.get('max', 0):.1f}\n"
                debug_text += f"📊 Colleges with Real VFM Data: {vfm_stats.get('with_data', 0)}\n"
            debug_text += "\n"
        
        debug_text += f"🏛️ SAMPLE COLLEGE DATA:\n"
        debug_text += f"{'-'*40}\n"
        
        for i, (college_branch, data) in enumerate(list(self.model.items())[:8]):
            college = data.get('college', 'Unknown')[:30]
            branch = data.get('branch', 'Unknown')
            vfm = data.get('value_for_money', 3.0)
            vfm_stars = self.vfm_to_stars(vfm)
            debug_text += f"{i+1}. {college}... - {branch}\n"
            debug_text += f"   ⭐ VFM: {vfm_stars}\n"
            
            categories = data.get('categories', {})
            for category, cat_data in list(categories.items())[:2]:
                debug_text += f"   🎯 {category}: {cat_data['min_rank']:,} - {cat_data['max_rank']:,}\n"
            debug_text += "\n"
        
        messagebox.showinfo("🤖 AI Model Analytics", debug_text)
    
    def show_all_branches(self):
        """Display all available engineering branches"""
        if not self.available_branches:
            messagebox.showinfo("🔬 Branches", "No branches found in the AI model.")
            return
        
        branches_text = f"🔬 AVAILABLE ENGINEERING BRANCHES\n"
        branches_text += f"{'='*40}\n\n"
        
        # Group branches by category
        cs_branches = [b for b in self.available_branches if 'computer' in b.lower() or 'information' in b.lower()]
        core_branches = [b for b in self.available_branches if any(word in b.lower() for word in ['mechanical', 'electrical', 'civil', 'chemical'])]
        electronics_branches = [b for b in self.available_branches if 'electronic' in b.lower() or 'communication' in b.lower()]
        other_branches = [b for b in self.available_branches if b not in cs_branches + core_branches + electronics_branches]
        
        if cs_branches:
            branches_text += "💻 COMPUTER & IT BRANCHES:\n"
            for i, branch in enumerate(sorted(cs_branches), 1):
                branches_text += f"  {i}. 🔹 {branch}\n"
            branches_text += "\n"
        
        if core_branches:
            branches_text += "⚙️ CORE ENGINEERING BRANCHES:\n"
            for i, branch in enumerate(sorted(core_branches), 1):
                branches_text += f"  {i}. 🔹 {branch}\n"
            branches_text += "\n"
        
        if electronics_branches:
            branches_text += "📡 ELECTRONICS BRANCHES:\n"
            for i, branch in enumerate(sorted(electronics_branches), 1):
                branches_text += f"  {i}. 🔹 {branch}\n"
            branches_text += "\n"
        
        if other_branches:
            branches_text += "🔬 OTHER SPECIALIZED BRANCHES:\n"
            for i, branch in enumerate(sorted(other_branches), 1):
                branches_text += f"  {i}. 🔹 {branch}\n"
        
        messagebox.showinfo("🔬 Engineering Branches Database", branches_text)
    
    def clear_form(self):
        """Reset all input fields to default values"""
        if self.available_categories:
            if 'OPEN' in self.available_categories:
                self.category_var.set('OPEN')
            else:
                self.category_var.set(sorted(self.available_categories)[0])
        
        self.rank_var.set('')
        self.twelveth_var.set('')
        self.branch_var.set('🌟 Any Branch')
        self.round_var.set('1️⃣ Round 1')
        
        # Clear results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.status_label.config(text="🚀 Ready for AI-powered recommendations!", foreground='#ffffff')

if __name__ == "__main__":
    root = tk.Tk()
    app = CollegeRecommender(root)
    root.mainloop()
