# data_diagnostic.py
import pandas as pd
import os

def analyze_data_structure():
    data_folder = r"C:\college recomendation sysstem\data"
    
    # Find all CSV files
    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the data folder.")
        return
    
    # Analyze the first few files
    for file in csv_files[:3]:  # Analyze first 3 files
        filepath = os.path.join(data_folder, file)
        print(f"\n=== Analyzing {file} ===")
        
        try:
            # Try reading with different encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(filepath, encoding=encoding, nrows=5)
                    print(f"Successfully read with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            print(f"Shape: {df.shape}")
            print("Columns:")
            for i, col in enumerate(df.columns):
                print(f"  {i}: {col}")
            
            print("\nFirst few rows:")
            for i in range(min(3, len(df))):
                print(f"Row {i}: {df.iloc[i].tolist()}")
                
        except Exception as e:
            print(f"Error reading {file}: {str(e)}")

if __name__ == "__main__":
    analyze_data_structure()