import os
from typing import List, Tuple, Optional

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


class Database:
    def __init__(self):
        load_dotenv()
        self.conn = None
        self.init_connection()
        self.create_table()
    
    def init_connection(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'quotes_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password'),
            port=os.getenv('DB_PORT', '5432')
        )
    
    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id SERIAL PRIMARY KEY,
                    page_num INTEGER,
                    quote TEXT,
                    author VARCHAR(255),
                    tags TEXT,
                    author_birth_date VARCHAR(100),
                    source_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
    
    def save_quotes(self, quotes_data: List[Tuple], source_url): 
        if not quotes_data:
            return 0
        
        with self.conn.cursor() as cur:
            data_to_insert = [
                (page_num, quote, author, tags, birth_date, source_url)
                for page_num, quote, author, tags, birth_date in quotes_data
            ]
            
            execute_values(cur, """
                INSERT INTO quotes (page_num, quote, author, tags, author_birth_date, source_url)
                VALUES %s
            """, data_to_insert)
            
            self.conn.commit()
            
            return len(quotes_data)
    
    def get_all_quotes(self):
        with self.conn.cursor() as cur:
            query = """
                SELECT id, page_num, quote, author, tags, author_birth_date, source_url, created_at
                FROM quotes
            """
    
            cur.execute(query)
            rows = cur.fetchall()
            
            return [
                {
                    "id": row[0],
                    "page_num": row[1],
                    "quote": row[2],
                    "author": row[3],
                    "tags": row[4],
                    "author_birth_date": row[5],
                    "source_url": row[6],
                    "created_at": row[7].isoformat() if row[7] else None
                }
                for row in rows
            ]
    
    def clean_db(self):
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE quotes RESTART IDENTITY")
            self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()
            
