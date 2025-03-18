import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv
import openai

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def get_table_info(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_info = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        columns_str = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
        schema_info.append(f"Table {table_name}: {columns_str}")
    
    conn.close()
    return "\n".join(schema_info)

def main():
    db_path = "db/org_structure_db1.sqlite"
    schema = get_table_info(db_path)
    print("Database schema:")
    print(schema)

    prompt = f"""
You are an expert in SQLite. You work in a IT company.
Given a database schema with organisation structure, generate a SQL query to carry out the task.

Schema:
{schema}

Task:
Which employee is responsible for maintaining the most systems?

Return only the SQL query, no explanations.
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    query = response.choices[0].message.content.strip()
    print(f"\nGenerated query: {query}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        print("\nResults:")
        for row in results:
            print(row)
        conn.close()
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")

if __name__ == "__main__":
    main()