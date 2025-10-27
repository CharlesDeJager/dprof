import pandas as pd
import json
import os
from typing import Dict, List, Any, Optional
import asyncio
from pathlib import Path

class FileConnector:
    """Handles connections and data reading from files (CSV, JSON, XLSX)"""
    
    def __init__(self):
        self.supported_extensions = {'.csv', '.json', '.xlsx', '.xls'}
    
    async def analyze_file_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze file structure and return available sheets/tables
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        structure = {
            "file_type": file_ext,
            "file_path": file_path,
            "sheets": []
        }
        
        try:
            if file_ext == '.csv':
                # CSV files have only one "sheet"
                df = pd.read_csv(file_path, nrows=0)  # Just read headers
                structure["sheets"] = [{
                    "name": "CSV_Data",
                    "columns": list(df.columns),
                    "column_count": len(df.columns)
                }]
            
            elif file_ext == '.json':
                # JSON can have multiple arrays
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, dict):
                    # Check for arrays within the JSON
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            if isinstance(value[0], dict):
                                columns = list(value[0].keys()) if value else []
                                structure["sheets"].append({
                                    "name": key,
                                    "columns": columns,
                                    "column_count": len(columns)
                                })
                elif isinstance(data, list) and len(data) > 0:
                    # Direct array
                    if isinstance(data[0], dict):
                        columns = list(data[0].keys())
                        structure["sheets"].append({
                            "name": "JSON_Array",
                            "columns": columns,
                            "column_count": len(columns)
                        })
            
            elif file_ext in ['.xlsx', '.xls']:
                # Excel files can have multiple sheets
                xl_file = pd.ExcelFile(file_path)
                for sheet_name in xl_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)
                    structure["sheets"].append({
                        "name": sheet_name,
                        "columns": list(df.columns),
                        "column_count": len(df.columns)
                    })
            
            return structure
            
        except Exception as e:
            raise Exception(f"Error analyzing file structure: {str(e)}")
    
    async def get_record_count(self, file_path: str, sheet_name: str) -> int:
        """
        Get the total number of records in a specific sheet/table
        """
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.csv':
                # Count lines in CSV (subtract 1 for header)
                with open(file_path, 'r') as f:
                    return sum(1 for line in f) - 1
            
            elif file_ext == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, dict) and sheet_name in data:
                    return len(data[sheet_name]) if isinstance(data[sheet_name], list) else 0
                elif isinstance(data, list) and sheet_name == "JSON_Array":
                    return len(data)
                else:
                    return 0
            
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=None)
                return len(df)
            
            return 0
            
        except Exception as e:
            raise Exception(f"Error getting record count: {str(e)}")
    
    async def read_data(self, file_path: str, sheet_name: str, max_records: Optional[int] = None) -> pd.DataFrame:
        """
        Read data from file with optional record limit
        """
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path, nrows=max_records)
            
            elif file_ext == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, dict) and sheet_name in data:
                    records = data[sheet_name][:max_records] if max_records else data[sheet_name]
                    df = pd.DataFrame(records)
                elif isinstance(data, list) and sheet_name == "JSON_Array":
                    records = data[:max_records] if max_records else data
                    df = pd.DataFrame(records)
                else:
                    df = pd.DataFrame()
            
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=max_records)
            
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            return df
            
        except Exception as e:
            raise Exception(f"Error reading data: {str(e)}")
    
    async def get_data_sample(self, file_path: str, sheet_name: str, sample_size: int = 100) -> pd.DataFrame:
        """
        Get a sample of data for quick preview
        """
        return await self.read_data(file_path, sheet_name, sample_size)