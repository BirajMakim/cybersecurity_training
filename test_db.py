import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybersecurity_training.settings')
django.setup()

from django.db import connection

def test_db_connection():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Successfully connected to PostgreSQL version: {version[0]}")
            
            # Test a simple query
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            print(f"Connected to database: {db_name[0]}")
            
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    test_db_connection() 