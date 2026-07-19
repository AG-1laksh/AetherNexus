import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

class ExcelParser:
    def __init__(self):
        pass

    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from an Excel file.
        Reads all sheets and converts them to Markdown tables.
        """
        # Read all sheets into a dictionary of DataFrames
        dfs = pd.read_excel(str(file_path), sheet_name=None)
        
        results = []
        for sheet_name, df in dfs.items():
            if df.empty:
                continue
                
            # Convert DataFrame to CSV format string
            # fillna("") ensures NaN values don't show up as string "nan"
            csv_str = df.fillna("").to_csv(index=False)
            
            # Prepend the sheet name as a heading
            text = f"## Sheet: {sheet_name}\n\n{csv_str}"
            
            results.append({
                "sheet_name": sheet_name,
                "text": text,
                "source": "digital"
            })
            
        return results

def parse_excel(file_path: Path) -> List[Dict[str, Any]]:
    parser = ExcelParser()
    return parser.parse(file_path)
