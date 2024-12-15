import sqlite3
import os
from datetime import datetime
from typing import List, Tuple

class ConversionHistoryDB:
    def __init__(self, db_path='conversion_history.db'):
        """
        Initialize the database connection and create table if not exists.
        
        Args:
        - db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """Create the conversions table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_path TEXT,
                    destination_path TEXT,
                    input_format TEXT,
                    output_format TEXT,
                    conversion_time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def log_conversion(self, source_path: str, destination_path: str, input_format: str, output_format: str):
        """
        Log a successful image conversion.
        
        Args:
        - source_path (str): Original image path
        - destination_path (str): Converted image path
        - input_format (str): Original image format
        - output_format (str): Converted image format
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversions 
                (source_path, destination_path, input_format, output_format) 
                VALUES (?, ?, ?, ?)
            ''', (source_path, destination_path, input_format, output_format))
            conn.commit()

    def get_conversion_history(self, limit: int = 100) -> List[Tuple]:
        """
        Retrieve recent conversion history.
        
        Args:
        - limit (int): Maximum number of records to retrieve
        
        Returns:
        - List of conversion records
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT source_path, destination_path, input_format, output_format, conversion_time 
                FROM conversions 
                ORDER BY conversion_time DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()

    def clear_history(self):
        """Clear all conversion history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conversions')
            conn.commit()