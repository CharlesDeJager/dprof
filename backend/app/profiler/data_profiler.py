import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable
import asyncio
import concurrent.futures
import re
from collections import Counter
from datetime import datetime
import math

from ..connectors.file_connector import FileConnector
from ..connectors.database_connector import DatabaseConnector

class DataProfiler:
    """
    Core data profiling engine with parallel processing capabilities
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.file_connector = FileConnector()
        self.db_connector = DatabaseConnector()
        
    async def profile_file_data(self, file_path: str, tables: List[str], 
                               max_records: Optional[int] = None,
                               progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Profile data from files with parallel processing
        """
        results = {}
        total_tables = len(tables)
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.settings.max_threads) as executor:
            # Submit all profiling tasks
            futures = {}
            for i, table in enumerate(tables):
                future = executor.submit(
                    self._profile_single_table_file,
                    file_path, table, max_records
                )
                futures[future] = (table, i)
            
            # Collect results as they complete
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                table_name, table_index = futures[future]
                try:
                    profile_result = future.result()
                    results[table_name] = profile_result
                    completed += 1
                    
                    if progress_callback:
                        progress = int((completed / total_tables) * 100)
                        progress_callback(progress)
                        
                except Exception as e:
                    results[table_name] = {"error": str(e)}
        
        return results
    
    async def profile_database_data(self, connection_info: Dict[str, Any], tables: List[str],
                                  max_records: Optional[int] = None,
                                  progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Profile data from database with parallel processing
        """
        results = {}
        total_tables = len(tables)
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.settings.max_threads) as executor:
            # Submit all profiling tasks
            futures = {}
            for i, table in enumerate(tables):
                future = executor.submit(
                    self._profile_single_table_database,
                    connection_info, table, max_records
                )
                futures[future] = (table, i)
            
            # Collect results as they complete
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                table_name, table_index = futures[future]
                try:
                    profile_result = future.result()
                    results[table_name] = profile_result
                    completed += 1
                    
                    if progress_callback:
                        progress = int((completed / total_tables) * 100)
                        progress_callback(progress)
                        
                except Exception as e:
                    results[table_name] = {"error": str(e)}
        
        return results
    
    def _profile_single_table_file(self, file_path: str, table_name: str, 
                                 max_records: Optional[int] = None) -> Dict[str, Any]:
        """
        Profile a single table from file data (synchronous for thread pool)
        """
        try:
            # Get data using the async method in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            df = loop.run_until_complete(
                self.file_connector.read_data(file_path, table_name, max_records)
            )
            loop.close()
            
            return self._profile_dataframe(df, table_name)
            
        except Exception as e:
            return {"error": str(e)}
    
    def _profile_single_table_database(self, connection_info: Dict[str, Any], table_name: str,
                                     max_records: Optional[int] = None) -> Dict[str, Any]:
        """
        Profile a single table from database (synchronous for thread pool)
        """
        try:
            # Get data using the async method in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            df = loop.run_until_complete(
                self.db_connector.read_data(connection_info, table_name, max_records)
            )
            loop.close()
            
            return self._profile_dataframe(df, table_name)
            
        except Exception as e:
            return {"error": str(e)}
    
    def _profile_dataframe(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """
        Comprehensive profiling of a pandas DataFrame
        """
        total_records = len(df)
        
        profile_result = {
            "table_name": table_name,
            "total_records": total_records,
            "total_columns": len(df.columns),
            "profiled_at": datetime.now().isoformat(),
            "columns": {}
        }
        
        # Profile each column in parallel using thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.settings.max_threads) as executor:
            column_futures = {}
            
            for column in df.columns:
                future = executor.submit(self._profile_column, df[column], column, total_records)
                column_futures[future] = column
            
            # Collect column profiling results
            for future in concurrent.futures.as_completed(column_futures):
                column_name = column_futures[future]
                try:
                    column_profile = future.result()
                    profile_result["columns"][column_name] = column_profile
                except Exception as e:
                    profile_result["columns"][column_name] = {"error": str(e)}
        
        return profile_result
    
    def _profile_column(self, series: pd.Series, column_name: str, total_records: int) -> Dict[str, Any]:
        """
        Detailed profiling of a single column
        """
        profile = {
            "column_name": column_name,
            "data_type": self._determine_data_type(series),
            "total_values": total_records
        }
        
        # Basic statistics
        null_count = series.isnull().sum()
        blank_count = self._count_blanks(series)
        non_null_series = series.dropna()
        
        profile.update({
            "null_count": int(null_count),
            "null_percentage": round((null_count / total_records) * 100, 2),
            "blank_count": int(blank_count),
            "blank_percentage": round((blank_count / total_records) * 100, 2),
            "non_null_count": int(len(non_null_series)),
            "distinct_count": int(series.nunique()),
            "distinct_percentage": round((series.nunique() / total_records) * 100, 2)
        })
        
        # Type-specific profiling
        if profile["data_type"] in ["int64", "float64", "numeric"]:
            profile.update(self._profile_numeric_column(non_null_series))
        
        elif profile["data_type"] in ["object", "string"]:
            profile.update(self._profile_string_column(non_null_series))
        
        elif profile["data_type"] in ["datetime64", "date"]:
            profile.update(self._profile_datetime_column(non_null_series))
        
        elif profile["data_type"] == "bool":
            profile.update(self._profile_boolean_column(non_null_series))
        
        # Additional insights
        profile.update(self._generate_additional_insights(series, non_null_series))
        
        return profile
    
    def _determine_data_type(self, series: pd.Series) -> str:
        """
        Determine the most appropriate data type for a series
        """
        dtype_str = str(series.dtype).lower()
        
        if 'int' in dtype_str:
            return 'int64'
        elif 'float' in dtype_str:
            return 'float64'
        elif 'datetime' in dtype_str:
            return 'datetime64'
        elif 'bool' in dtype_str:
            return 'bool'
        else:
            # Check if string column contains mostly numeric values
            non_null_series = series.dropna()
            if len(non_null_series) > 0:
                try:
                    pd.to_numeric(non_null_series)
                    return 'numeric'
                except:
                    pass
                
                try:
                    pd.to_datetime(non_null_series)
                    return 'date'
                except:
                    pass
            
            return 'object'
    
    def _count_blanks(self, series: pd.Series) -> int:
        """
        Count blank values (empty strings, whitespace-only strings)
        """
        if series.dtype == 'object':
            return series.astype(str).str.strip().eq('').sum()
        return 0
    
    def _profile_numeric_column(self, series: pd.Series) -> Dict[str, Any]:
        """
        Profile numeric columns
        """
        try:
            numeric_series = pd.to_numeric(series, errors='coerce').dropna()
            
            if len(numeric_series) == 0:
                return {"min_value": None, "max_value": None, "average": None, "median": None}
            
            return {
                "min_value": float(numeric_series.min()),
                "max_value": float(numeric_series.max()),
                "average": round(float(numeric_series.mean()), 6),
                "median": float(numeric_series.median()),
                "standard_deviation": round(float(numeric_series.std()), 6),
                "quartile_25": float(numeric_series.quantile(0.25)),
                "quartile_75": float(numeric_series.quantile(0.75)),
                "zero_count": int((numeric_series == 0).sum()),
                "negative_count": int((numeric_series < 0).sum()),
                "positive_count": int((numeric_series > 0).sum())
            }
        except Exception:
            return {"min_value": None, "max_value": None, "average": None, "median": None}
    
    def _profile_string_column(self, series: pd.Series) -> Dict[str, Any]:
        """
        Profile string columns including pattern analysis
        """
        if len(series) == 0:
            return {"patterns": [], "avg_length": 0, "min_length": 0, "max_length": 0}
        
        string_series = series.astype(str)
        
        # Length statistics
        lengths = string_series.str.len()
        
        profile = {
            "avg_length": round(lengths.mean(), 2),
            "min_length": int(lengths.min()),
            "max_length": int(lengths.max()),
            "most_common_values": self._get_most_common_values(series, 10),
            "patterns": self._analyze_string_patterns(string_series)
        }
        
        return profile
    
    def _profile_datetime_column(self, series: pd.Series) -> Dict[str, Any]:
        """
        Profile datetime columns
        """
        try:
            datetime_series = pd.to_datetime(series, errors='coerce').dropna()
            
            if len(datetime_series) == 0:
                return {"min_date": None, "max_date": None}
            
            return {
                "min_date": datetime_series.min().isoformat(),
                "max_date": datetime_series.max().isoformat(),
                "date_range_days": (datetime_series.max() - datetime_series.min()).days,
                "most_common_dates": [
                    dt.isoformat() for dt in datetime_series.value_counts().head(5).index.tolist()
                ]
            }
        except Exception:
            return {"min_date": None, "max_date": None}
    
    def _profile_boolean_column(self, series: pd.Series) -> Dict[str, Any]:
        """
        Profile boolean columns
        """
        try:
            bool_series = series.astype(bool)
            true_count = bool_series.sum()
            false_count = len(bool_series) - true_count
            
            return {
                "true_count": int(true_count),
                "false_count": int(false_count),
                "true_percentage": round((true_count / len(bool_series)) * 100, 2),
                "false_percentage": round((false_count / len(bool_series)) * 100, 2)
            }
        except Exception:
            return {"true_count": 0, "false_count": 0}
    
    def _analyze_string_patterns(self, string_series: pd.Series, max_patterns: int = 20) -> List[Dict[str, Any]]:
        """
        Analyze common patterns in string data
        """
        if len(string_series) == 0:
            return []
        
        # Generate patterns by replacing digits and letters with placeholders
        patterns = []
        
        for value in string_series.head(1000):  # Analyze first 1000 for performance
            try:
                # Create pattern by replacing specific characters
                pattern = re.sub(r'\d', '9', str(value))  # Replace digits with 9
                pattern = re.sub(r'[a-zA-Z]', 'A', pattern)  # Replace letters with A
                patterns.append(pattern)
            except:
                continue
        
        # Count pattern frequencies
        pattern_counts = Counter(patterns)
        
        # Convert to list of dictionaries with examples
        pattern_list = []
        for pattern, count in pattern_counts.most_common(max_patterns):
            # Find examples that match this pattern
            examples = []
            for original, gen_pattern in zip(string_series.head(1000), patterns):
                if gen_pattern == pattern and len(examples) < 3:
                    examples.append(str(original))
            
            pattern_list.append({
                "pattern": pattern,
                "count": count,
                "percentage": round((count / len(patterns)) * 100, 2),
                "examples": examples
            })
        
        return pattern_list
    
    def _get_most_common_values(self, series: pd.Series, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most common values in the series
        """
        if len(series) == 0:
            return []
        
        value_counts = series.value_counts().head(limit)
        total_count = len(series)
        
        return [
            {
                "value": str(value),
                "count": int(count),
                "percentage": round((count / total_count) * 100, 2)
            }
            for value, count in value_counts.items()
        ]
    
    def _generate_additional_insights(self, series: pd.Series, non_null_series: pd.Series) -> Dict[str, Any]:
        """
        Generate additional insights and quality indicators
        """
        insights = {}
        
        # Data quality score (0-100)
        quality_score = 100
        
        # Penalize for nulls
        null_percentage = (series.isnull().sum() / len(series)) * 100
        if null_percentage > 0:
            quality_score -= min(null_percentage, 30)
        
        # Penalize for blanks
        blank_percentage = (self._count_blanks(series) / len(series)) * 100
        if blank_percentage > 0:
            quality_score -= min(blank_percentage, 20)
        
        # Reward for diversity
        diversity_score = (series.nunique() / len(series)) * 100
        if diversity_score > 80:
            quality_score += 5
        elif diversity_score < 10:
            quality_score -= 10
        
        insights["data_quality_score"] = max(0, round(quality_score, 1))
        
        # Completeness
        insights["completeness"] = round(((len(series) - series.isnull().sum()) / len(series)) * 100, 2)
        
        # Uniqueness
        insights["uniqueness"] = round((series.nunique() / len(series)) * 100, 2)
        
        # Potential issues
        issues = []
        if null_percentage > 50:
            issues.append("High null percentage")
        if blank_percentage > 20:
            issues.append("High blank percentage")
        if diversity_score < 5:
            issues.append("Low data diversity")
        
        insights["potential_issues"] = issues
        
        return insights