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
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError as e:
                        raise Exception(f"Invalid JSON format: {str(e)}")
                
                if isinstance(data, dict):
                    # Check for arrays within the JSON
                    arrays_found = False
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            # Handle both array of objects and array of primitives
                            if isinstance(value[0], dict):
                                columns = list(value[0].keys()) if value else []
                                structure["sheets"].append({
                                    "name": key,
                                    "columns": columns,
                                    "column_count": len(columns)
                                })
                                arrays_found = True
                            else:
                                # Array of primitives - treat as single column
                                structure["sheets"].append({
                                    "name": key,
                                    "columns": [key],
                                    "column_count": 1
                                })
                                arrays_found = True
                    
                    if not arrays_found:
                        # If no arrays found, treat the object itself as data
                        if data:
                            columns = list(data.keys())
                            structure["sheets"].append({
                                "name": "JSON_Object",
                                "columns": columns,
                                "column_count": len(columns)
                            })
                        
                elif isinstance(data, list):
                    if len(data) > 0:
                        # Direct array
                        if isinstance(data[0], dict):
                            columns = list(data[0].keys())
                            structure["sheets"].append({
                                "name": "JSON_Array",
                                "columns": columns,
                                "column_count": len(columns)
                            })
                        else:
                            # Array of primitives
                            structure["sheets"].append({
                                "name": "JSON_Array",
                                "columns": ["value"],
                                "column_count": 1
                            })
                    else:
                        # Empty array
                        structure["sheets"].append({
                            "name": "JSON_Array",
                            "columns": [],
                            "column_count": 0
                        })
                else:
                    # Single primitive value
                    structure["sheets"].append({
                        "name": "JSON_Value",
                        "columns": ["value"],
                        "column_count": 1
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
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError as e:
                        raise Exception(f"Invalid JSON format: {str(e)}")
                
                if isinstance(data, dict):
                    if sheet_name in data:
                        value = data[sheet_name]
                        return len(value) if isinstance(value, list) else 1
                    elif sheet_name == "JSON_Object":
                        return 1
                    else:
                        return 0
                elif isinstance(data, list) and sheet_name == "JSON_Array":
                    return len(data)
                elif sheet_name == "JSON_Value":
                    return 1
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
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError as e:
                        raise Exception(f"Invalid JSON format: {str(e)}")
                
                if isinstance(data, dict):
                    if sheet_name in data:
                        # Data is nested under a key
                        value = data[sheet_name]
                        if isinstance(value, list):
                            records = value[:max_records] if max_records else value
                            if len(records) > 0:
                                if isinstance(records[0], dict):
                                    df = pd.DataFrame(records)
                                else:
                                    # Array of primitives
                                    df = pd.DataFrame({sheet_name: records})
                            else:
                                df = pd.DataFrame()
                        else:
                            # Single value
                            df = pd.DataFrame({sheet_name: [value]})
                    elif sheet_name == "JSON_Object":
                        # Treat the entire object as a single record
                        df = pd.DataFrame([data])
                    else:
                        df = pd.DataFrame()
                        
                elif isinstance(data, list) and sheet_name == "JSON_Array":
                    records = data[:max_records] if max_records else data
                    if len(records) > 0:
                        if isinstance(records[0], dict):
                            df = pd.DataFrame(records)
                        else:
                            # Array of primitives
                            df = pd.DataFrame({"value": records})
                    else:
                        df = pd.DataFrame()
                        
                elif sheet_name == "JSON_Value":
                    # Single primitive value
                    df = pd.DataFrame({"value": [data]})
                    
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