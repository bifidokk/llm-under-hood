import sqlite3
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import openai
import sys
import signal

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
    questions = [
        "Which employee is responsible for maintaining the most systems?",
        "How many systems are there that have only one owner or one maintainer?",
        "Which systems does the busiest employee (maintains the most systems) maintain?",
        "If Elena Becker (Database Administrator) were to leave suddenly, which specific systems would she no longer be able to maintain?",
        "How many other systems are directly connected to the Enterprise Service Bus (ESB)?",
        "Which department has the highest number of employees listed as system owners or maintainers?",
        "How many systems are maintained by employees outside of the 'IT Department'?",
        "If Maximilian Hofer (Senior Data Scientist) left the company, which systems would lose their last owner?",
        "How many other systems have a direct dependency on the Transportation Management System (TMS)?",
        "How many employees are listed as both owners and maintainers of the same system?",
        "If the Customer Relationship Management (CRM) system failed while its maintainer was on vacation, how many other systems that depend on it would be impacted directly and indirectly?",
    ]

    db_path = "db/org_structure_db1.sqlite"
    schema = get_table_info(db_path)
    print("Database schema:")
    print(schema)

    prompt = f"""
You are an expert in SQLite. You work in a IT company.
Given a database schema with organisation structure, generate SQL queries for multiple tasks. Do not use WITH RECURSIVE in queries. Do not make up fields, use provided database schema.

Schema:
{schema}

Tasks:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions))}

Return a JSON array where each element is an object containing:
1. "question": the original question
2. "query": the SQL query to answer that question

Return only the JSON array, no explanations.
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    queries = json.loads(response.choices[0].message.content.strip())
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for item in queries:
            print(f"\nQuestion: {item['question']}")
            print(f"Query: {item['query']}")
            try:
                cursor.execute(item['query'])
                results = cursor.fetchall()
                print("Results:")
                for row in results:
                    print(row)
            except sqlite3.Error as e:
                print(f"Error executing query: {e}")
            print("-" * 50)
            
        conn.close()
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

def signal_handler(sig, frame):
    print('\nExiting gracefully...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    main()