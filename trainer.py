import pandas as pd
import numpy as np
import os
import json
import re
from fuzzywuzzy import fuzz, process
import warnings
import sys

# Set stdout encoding to utf-8 to handle Unicode characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings('ignore')

class CollegeDataTrainer:
    def __init__(self):
        self.admission_data = None  # Dataset A
        self.vfm_data = None        # Dataset B (Value for Money)
        self.model = {}
        self.college_mappings = {}
    
    def load_datasets(self):
        """Load both datasets from the data folder"""
        data_folder = "data"
        
        try:
            # Load Dataset A (Admission data)
            admission_files = []
            for file in os.listdir(data_folder):
                if file.endswith(('.csv', '.xlsx', '.xls')) and 'value for money' not in file.lower():
                    admission_files.append(file)
            
            if not admission_files:
                print("No admission data files found in data folder")
                return False
            
            data_a_list = []
            for file in admission_files:
                filepath = os.path.join(data_folder, file)
                try:
                    if file.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(filepath)
                    else:
                        df = pd.read_csv(filepath)
                    df['Source_File'] = file
                    data_a_list.append(df)
                    print(f"[SUCCESS] Loaded {file} with {len(df)} rows")
                except Exception as e:
                    print(f"[ERROR] Error loading {file}: {e}")
                    continue
            
            if data_a_list:
                self.admission_data = pd.concat(data_a_list, ignore_index=True)
                print(f"[SUCCESS] Combined Admission Data: {len(self.admission_data)} records")
            else:
                print("[ERROR] No admission data could be loaded")
                return False
            
            # Load Dataset B (Value for Money data)
            vfm_files = []
            for file in os.listdir(data_folder):
                if 'value for money' in file.lower():
                    vfm_files.append(file)
            
            if not vfm_files:
                print("[WARNING] No Value for Money file found")
                self.vfm_data = pd.DataFrame()
                return True
            
            vfm_file = vfm_files[0]
            vfm_path = os.path.join(data_folder, vfm_file)
            
            try:
                if vfm_file.endswith(('.xlsx', '.xls')):
                    self.vfm_data = pd.read_excel(vfm_path)
                else:
                    self.vfm_data = pd.read_csv(vfm_path)
                print(f"[SUCCESS] Loaded Value for Money data: {len(self.vfm_data)} records")
                print("VFM Data Columns:", self.vfm_data.columns.tolist())
            except Exception as e:
                print(f"[ERROR] Error loading VFM data: {e}")
                self.vfm_data = pd.DataFrame()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error loading datasets: {e}")
            return False
    
    def normalize_college_name(self, name):
        """Normalize college names for better matching"""
        if pd.isna(name) or not isinstance(name, str):
            return ""
        
        # Convert to uppercase and remove extra spaces
        name = name.upper().strip()
        
        # Common abbreviations and replacements
        replacements = {
            'IIT': 'INDIAN INSTITUTE OF TECHNOLOGY',
            'NIT': 'NATIONAL INSTITUTE OF TECHNOLOGY', 
            'IIIT': 'INDIAN INSTITUTE OF INFORMATION TECHNOLOGY',
            'B.TECH': 'BACHELOR OF TECHNOLOGY',
            'B.TECH.': 'BACHELOR OF TECHNOLOGY',
            'ENGINEERING': 'ENGG',
            'TECHNOLOGY': 'TECH',
            ' ': ' ',
            '(': '',
            ')': '',
            '&': 'AND'
        }
        
        for old, new in replacements.items():
            name = name.replace(old, new)
        
        # Remove special characters and extra spaces
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def extract_branch_from_program(self, program_name):
        """Extract branch name from academic program name"""
        if not isinstance(program_name, str):
            return "Other"
        
        program_upper = program_name.upper()
        
        # Enhanced branch patterns with priority
        branch_patterns = [
            ('Computer Science', r'(COMPUTER SCIENCE|CS|CSE|COMPUTER ENGG|COMPUTER)'),
            ('Electrical', r'(ELECTRICAL|EE|ELECTRICAL ENGG|ELECTRICAL ENGINEERING)'),
            ('Mechanical', r'(MECHANICAL|ME|MECH|MECHANICAL ENGG)'),
            ('Electronics', r'(ELECTRONICS|EC|ECE|ELECTRONICS ENGG|ELECTRONICS AND COMMUNICATION)'),
            ('Civil', r'(CIVIL|CE|CIVIL ENGG|CIVIL ENGINEERING)'),
            ('Information Technology', r'(INFORMATION TECHNOLOGY|IT|IT ENGG)'),
            ('Chemical', r'(CHEMICAL|CH|CHEMICAL ENGG|CHEMICAL ENGINEERING)'),
            ('Aerospace', r'(AEROSPACE|AE|AERONAUTICAL|AEROSPACE ENGG)'),
            ('Biotechnology', r'(BIOTECHNOLOGY|BT|BIO TECH|BIO TECHNOLOGY)'),
            ('Instrumentation', r'(INSTRUMENTATION|IC|INSTRUMENTATION ENGG|CONTROL)'),
            ('Metallurgy', r'(METALLURGY|MT|METALLURGICAL ENGG)'),
            ('Mining', r'(MINING|MN|MINING ENGG)'),
            ('Production', r'(PRODUCTION|INDUSTRIAL|PRODUCTION ENGG|INDUSTRIAL ENGG)'),
            ('Physics', r'(PHYSICS|ENGINEERING PHYSICS)'),
            ('Mathematics', r'(MATHEMATICS|MATHS|COMPUTATIONAL MATHEMATICS)'),
        ]
        
        for branch_name, pattern in branch_patterns:
            if re.search(pattern, program_upper):
                return branch_name
        
        return "Other"
    
    def extract_branch_from_course(self, course_name):
        """Extract branch name from course name in VFM data"""
        if not isinstance(course_name, str):
            return "Other"
        
        course_upper = course_name.upper()
        
        # Simplified extraction for VFM data
        branch_mapping = {
            'COMPUTER': 'Computer Science',
            'MECHANICAL': 'Mechanical',
            'CIVIL': 'Civil',
            'ELECTRONICS': 'Electronics',
            'ELECTRICAL': 'Electrical',
            'CHEMICAL': 'Chemical',
            'INFORMATION TECHNOLOGY': 'Information Technology',
            'IT': 'Information Technology',
            'BIOTECH': 'Biotechnology',
            'INSTRUMENTATION': 'Instrumentation',
            'METALLURGY': 'Metallurgy',
            'MINING': 'Mining',
            'PRODUCTION': 'Production',
            'INDUSTRIAL': 'Production',
            'PHYSICS': 'Physics',
        }
        
        for keyword, branch in branch_mapping.items():
            if keyword in course_upper:
                return branch
        
        return "Other"
    
    def create_college_mappings(self):
        """Create fuzzy mappings between college names in both datasets"""
        if self.vfm_data.empty:
            print("[WARNING] No VFM data available for mapping")
            return
        
        # Extract unique college names from both datasets
        colleges_admission = set(self.admission_data['Institute'].dropna().apply(self.normalize_college_name))
        
        # Extract from VFM data  
        colleges_vfm = set(self.vfm_data['Institute'].dropna().apply(self.normalize_college_name))
        
        print(f"[INFO] Colleges in Admission data: {len(colleges_admission)}")
        print(f"[INFO] Colleges in VFM data: {len(colleges_vfm)}")
        
        # Create fuzzy matches
        self.college_mappings = {}
        match_count = 0
        
        for college_a in colleges_admission:
            if not college_a:
                continue
            
            # Find best match in VFM data
            best_match, score = process.extractOne(college_a, list(colleges_vfm), scorer=fuzz.token_sort_ratio)
            
            if score >= 75:  # Good match threshold
                self.college_mappings[college_a] = {
                    'vfm_name': best_match,
                    'match_score': score
                }
                match_count += 1
                
                if match_count <= 10:  # Print first 10 matches
                    print(f" [MATCH] {college_a[:40]}... -> {best_match[:40]}... (score: {score})")
        
        print(f"[SUCCESS] Created {match_count} college mappings ({(match_count/len(colleges_admission))*100:.1f}% matched)")
    
    def get_vfm_score(self, college_name, branch):
        """Get VFM score for a college-branch combination"""
        if self.vfm_data.empty:
            return 3.0  # Default score
        
        college_normalized = self.normalize_college_name(college_name)
        
        # Check if we have a mapping for this college
        mapping = self.college_mappings.get(college_normalized)
        if not mapping:
            return 3.0  # No mapping found
        
        vfm_college_name = mapping['vfm_name']
        
        # Find matching records in VFM data
        vfm_records = self.vfm_data[
            self.vfm_data['Institute'].apply(self.normalize_college_name) == vfm_college_name
        ]
        
        if vfm_records.empty:
            return 3.0
        
        # Try to match by branch
        branch_scores = []
        for _, row in vfm_records.iterrows():
            vfm_course = row['Course']
            vfm_branch = self.extract_branch_from_course(vfm_course)
            vfm_score = row['Value for Money (Out of 5)']
            
            # Check branch match
            if vfm_branch == branch or vfm_branch in branch or branch in vfm_branch:
                branch_scores.append(vfm_score)
            elif vfm_branch == "Other" or branch == "Other":
                # If either is "Other", give partial weight
                branch_scores.append(vfm_score * 0.7)
        
        if branch_scores:
            # Return average score for matching branches
            return round(np.mean(branch_scores), 2)
        else:
            # Return college average if no branch match
            college_avg = vfm_records['Value for Money (Out of 5)'].mean()
            return round(college_avg * 0.8, 2)  # Slightly penalize for no branch match
    
    def preprocess_admission_data(self):
        """Preprocess the admission data with proper column handling"""
        print("[INFO] Preprocessing admission data...")
        
        processed_data = []
        
        for _, row in self.admission_data.iterrows():
            try:
                institute = str(row['Institute']) if pd.notna(row.get('Institute')) else "Unknown"
                program = str(row['Academic Program Name']) if pd.notna(row.get('Academic Program Name')) else "Unknown"
                seat_type = str(row['Seat Type']) if pd.notna(row.get('Seat Type')) else "OPEN"
                opening_rank = self.parse_rank(row.get('Opening Rank'))
                closing_rank = self.parse_rank(row.get('Closing Rank'))
                
                # Skip invalid ranks
                if opening_rank == 0 or closing_rank == 0:
                    continue
                
                # Extract branch
                branch = self.extract_branch_from_program(program)
                
                # Determine category from seat type
                category = self.map_seat_type_to_category(seat_type)
                
                processed_data.append({
                    'College': institute.strip(),
                    'Branch': branch,
                    'Category': category,
                    'Opening_Rank': opening_rank,
                    'Closing_Rank': closing_rank,
                    'Year': row.get('Year', 2023),
                    'Round': row.get('Round', 1),
                    'Source': row.get('Source_File', 'Unknown')
                })
                
            except (ValueError, TypeError, KeyError) as e:
                continue
        
        processed_df = pd.DataFrame(processed_data)
        
        # Filter out unknown colleges
        processed_df = processed_df[processed_df['College'] != "Unknown"]
        
        print(f"[SUCCESS] Processed {len(processed_df)} valid admission records")
        
        # Show sample of processed data
        print("[INFO] Sample processed records:")
        for i in range(min(3, len(processed_df))):
            rec = processed_df.iloc[i]
            print(f" {rec['College'][:30]}... | {rec['Branch']} | {rec['Category']} | {rec['Opening_Rank']}-{rec['Closing_Rank']}")
        
        return processed_df
    
    def parse_rank(self, rank_value):
        """Parse rank values that might contain special characters like 'P'"""
        if pd.isna(rank_value):
            return 0
        
        try:
            rank_str = str(rank_value).upper().replace('P', '').replace(' ', '')
            return int(float(rank_str)) if rank_str else 0
        except (ValueError, TypeError):
            return 0
    
    def map_seat_type_to_category(self, seat_type):
        """Map seat type to standardized category"""
        seat_type_upper = seat_type.upper()
        
        if 'OPEN' in seat_type_upper and 'PWD' not in seat_type_upper:
            return 'OPEN'
        elif 'OBC' in seat_type_upper:
            return 'OBC-NCL'
        elif 'SC' in seat_type_upper:
            return 'SC'
        elif 'ST' in seat_type_upper:
            return 'ST'
        elif 'EWS' in seat_type_upper:
            return 'EWS'
        else:
            return 'GENERAL'
    
    def train_model(self):
        """Train the recommendation model"""
        processed_data = self.preprocess_admission_data()
        
        if processed_data.empty:
            print("[ERROR] No valid data to train model")
            return False
        
        # Create college-branch combinations with statistics
        for _, row in processed_data.iterrows():
            college = row['College']
            branch = row['Branch']
            category = row['Category']
            
            key = f"{college} - {branch}"
            
            if key not in self.model:
                # Calculate VFM score for this college-branch
                vfm_score = self.get_vfm_score(college, branch)
                
                self.model[key] = {
                    'categories': {},
                    'value_for_money': vfm_score,
                    'college': college,
                    'branch': branch,
                    'data_points': 0
                }
            
            if category not in self.model[key]['categories']:
                self.model[key]['categories'][category] = {
                    'min_rank': float('inf'),
                    'max_rank': 0,
                    'count': 0,
                    'years': set(),
                    'rounds': set()
                }
            
            # Update category statistics
            cat_data = self.model[key]['categories'][category]
            cat_data['min_rank'] = min(cat_data['min_rank'], row['Opening_Rank'])
            cat_data['max_rank'] = max(cat_data['max_rank'], row['Closing_Rank'])
            cat_data['count'] += 1
            cat_data['years'].add(row['Year'])
            cat_data['rounds'].add(row['Round'])
            
            self.model[key]['data_points'] += 1
        
        # Filter out combinations with insufficient data
        self.model = {k: v for k, v in self.model.items() if v['data_points'] >= 1}
        
        print(f"[SUCCESS] Trained model with {len(self.model)} college-branch combinations")
        
        # Calculate statistics
        vfm_scores = [v['value_for_money'] for v in self.model.values()]
        avg_vfm = np.mean(vfm_scores)
        default_vfm_count = sum(1 for score in vfm_scores if score == 3.0)
        
        print(f"[STATS] VFM Statistics: Avg={avg_vfm:.2f}, Default={default_vfm_count}, Actual={len(vfm_scores)-default_vfm_count}")
        
        return True
    
    def save_model(self):
        """Save the trained model with metadata"""
        if not os.path.exists("models"):
            os.makedirs("models")
        
        # Convert sets to lists for JSON serialization
        model_copy = {}
        for key, value in self.model.items():
            model_copy[key] = {
                'categories': {},
                'value_for_money': value['value_for_money'],
                'college': value['college'],
                'branch': value['branch'],
                'data_points': value['data_points']
            }
            
            for cat, cat_data in value['categories'].items():
                model_copy[key]['categories'][cat] = {
                    'min_rank': cat_data['min_rank'],
                    'max_rank': cat_data['max_rank'],
                    'count': cat_data['count'],
                    'years': list(cat_data['years']),
                    'rounds': list(cat_data['rounds'])
                }
        
        model_data = {
            'model': model_copy,
            'college_mappings': self.college_mappings,
            'metadata': {
                'timestamp': pd.Timestamp.now().isoformat(),
                'total_combinations': len(self.model),
                'categories_available': list(set(
                    cat for cb in self.model.values() 
                    for cat in cb['categories'].keys()
                )),
                'vfm_stats': {
                    'average': np.mean([v['value_for_money'] for v in self.model.values()]),
                    'min': min([v['value_for_money'] for v in self.model.values()]),
                    'max': max([v['value_for_money'] for v in self.model.values()]),
                    'with_data': len([v for v in self.model.values() if v['value_for_money'] != 3.0])
                }
            }
        }
        
        model_path = os.path.join("models", "college_recommendation_model.json")
        
        with open(model_path, "w", encoding='utf-8') as f:
            json.dump(model_data, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Model saved to {model_path}")
        
        # Print summary
        print("\n" + "="*50)
        print("[SUCCESS] MODEL TRAINING SUMMARY")
        print("="*50)
        print(f"• College-Branch Combinations: {len(self.model)}")
        print(f"• VFM Data Coverage: {model_data['metadata']['vfm_stats']['with_data']}/{len(self.model)}")
        print(f"• Average VFM Score: {model_data['metadata']['vfm_stats']['average']:.2f}/5")
        print(f"• College Mappings Created: {len(self.college_mappings)}")
        
        # Show sample of model data with actual VFM scores
        print("\n[INFO] Sample College-Branch Combinations with VFM Scores:")
        sample_count = 0
        for key, data in self.model.items():
            if data['value_for_money'] != 3.0 and sample_count < 5:
                vfm_status = "ACTUAL DATA" if data['value_for_money'] != 3.0 else "DEFAULT"
                print(f" {key[:50]}... | VFM: {data['value_for_money']}/5 ({vfm_status})")
                sample_count += 1
        
        return model_path

def main():
    print("[INFO] Starting College Recommendation Trainer...")
    print("="*60)
    
    trainer = CollegeDataTrainer()
    
    # Load datasets
    if not trainer.load_datasets():
        print("[ERROR] Failed to load datasets. Please check your data folder.")
        return
    
    # Create college mappings
    trainer.create_college_mappings()
    
    # Train model
    if trainer.train_model():
        # Save model
        model_path = trainer.save_model()
        print(f"\n[SUCCESS] Training completed successfully!")
        print(f"[INFO] Model saved at: {model_path}")
    else:
        print("[ERROR] Training failed!")

if __name__ == "__main__":
    main()

