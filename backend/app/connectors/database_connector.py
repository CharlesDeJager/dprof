import pandas as pd
from sqlalchemy import create_engine, text, inspect
from typing import Dict, List, Any, Optional
import asyncio
import cx_Oracle
import pyodbc

class DatabaseConnector:
    """Handles connections to Oracle and SQL Server databases"""
    
    def __init__(self):
        self.supported_db_types = {'oracle', 'sqlserver'}
        self._connection_pool = {}
    
    async def connect_and_get_tables(self, db_type: str, host: str, port: int, 
                                   database: str, username: str, password: str) -> List[Dict[str, Any]]:
        """
        Connect to database and return list of available tables
        """
        if db_type.lower() not in self.supported_db_types:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        connection_string = self._build_connection_string(
            db_type.lower(), host, port, database, username, password
        )
        
        try:
            engine = create_engine(connection_string)
            
            # Test connection
            with engine.connect() as conn:
                # Get table information
                inspector = inspect(engine)
                tables = []
                
                for table_name in inspector.get_table_names():
                    columns = inspector.get_columns(table_name)
                    tables.append({
                        "name": table_name,
                        "columns": [col['name'] for col in columns],
                        "column_count": len(columns),
                        "column_types": {col['name']: str(col['type']) for col in columns}
                    })
                
                # Store connection for later use
                connection_key = f"{db_type}_{host}_{port}_{database}_{username}"
                self._connection_pool[connection_key] = {
                    "engine": engine,
                    "connection_string": connection_string
                }
                
                return tables
                
        except Exception as e:
            raise Exception(f"Database connection error: {str(e)}")
    
    def _build_connection_string(self, db_type: str, host: str, port: int, 
                               database: str, username: str, password: str) -> str:
        """
        Build database connection string based on database type
        """
        if db_type == 'oracle':
            # Oracle connection string
            return f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}"
        
        elif db_type == 'sqlserver':
            # SQL Server connection string using pyodbc
            driver = "{ODBC Driver 17 for SQL Server}"  # or appropriate driver
            return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver={driver}"
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    async def get_record_count(self, connection_info: Dict[str, Any], table_name: str) -> int:
        """
        Get total record count for a table
        """
        connection_string = self._build_connection_string(
            connection_info['connection_type'],
            connection_info['host'],
            connection_info['port'],
            connection_info['database'],
            connection_info['username'],
            connection_info['password']
        )
        
        try:
            engine = create_engine(connection_string)
            
            with engine.connect() as conn:
                query = text(f"SELECT COUNT(*) FROM {table_name}")
                result = conn.execute(query)
                count = result.scalar()
                return count
                
        except Exception as e:
            raise Exception(f"Error getting record count: {str(e)}")
    
    async def read_data(self, connection_info: Dict[str, Any], table_name: str, 
                       max_records: Optional[int] = None, offset: int = 0) -> pd.DataFrame:
        """
        Read data from database table with optional limits
        """
        connection_string = self._build_connection_string(
            connection_info['connection_type'],
            connection_info['host'],
            connection_info['port'],
            connection_info['database'],
            connection_info['username'],
            connection_info['password']
        )
        
        try:
            engine = create_engine(connection_string)
            
            # Build query with limit and offset
            if connection_info['connection_type'] == 'oracle':
                if max_records:
                    if offset > 0:
                        query = f"""
                        SELECT * FROM (
                            SELECT a.*, ROWNUM rnum FROM (
                                SELECT * FROM {table_name}
                            ) a WHERE ROWNUM <= {offset + max_records}
                        ) WHERE rnum > {offset}
                        """
                    else:
                        query = f"SELECT * FROM {table_name} WHERE ROWNUM <= {max_records}"
                else:
                    query = f"SELECT * FROM {table_name}"
            
            elif connection_info['connection_type'] == 'sqlserver':
                if max_records:
                    query = f"SELECT * FROM {table_name} ORDER BY (SELECT NULL) OFFSET {offset} ROWS FETCH NEXT {max_records} ROWS ONLY"
                else:
                    query = f"SELECT * FROM {table_name}"
            
            df = pd.read_sql(query, engine)
            return df
            
        except Exception as e:
            raise Exception(f"Error reading data: {str(e)}")
    
    async def get_table_schema(self, connection_info: Dict[str, Any], table_name: str) -> Dict[str, Any]:
        """
        Get detailed schema information for a table
        """
        connection_string = self._build_connection_string(
            connection_info['connection_type'],
            connection_info['host'],
            connection_info['port'],
            connection_info['database'],
            connection_info['username'],
            connection_info['password']
        )
        
        try:
            engine = create_engine(connection_string)
            inspector = inspect(engine)
            
            columns = inspector.get_columns(table_name)
            primary_keys = inspector.get_pk_constraint(table_name)
            indexes = inspector.get_indexes(table_name)
            
            schema_info = {
                "table_name": table_name,
                "columns": columns,
                "primary_keys": primary_keys.get('constrained_columns', []),
                "indexes": indexes
            }
            
            return schema_info
            
        except Exception as e:
            raise Exception(f"Error getting table schema: {str(e)}")
    
    def close_connections(self):
        """
        Close all database connections
        """
        for connection_key, connection_data in self._connection_pool.items():
            try:
                connection_data['engine'].dispose()
            except:
                pass
        
        self._connection_pool.clear()