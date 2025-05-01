import psycopg2
from psycopg2 import OperationalError

def test_connection():
    try:
        # Using the actual connection details from settings.py
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres.kgexeshuuoonbrgoyazp',
            password='6XB07HW15D81nxUR',
            host='aws-0-ap-southeast-2.pooler.supabase.com',
            port='6543',
            connect_timeout=10  # Adding a timeout parameter
        )
        print("Successfully connected to the database!")
        
        # Get database version
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        # Close the connection
        cur.close()
        conn.close()
        print("Connection closed successfully.")
        
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        print("\nTroubleshooting steps:")
        print("1. Go to your Supabase dashboard (https://supabase.com/dashboard)")
        print("2. Select your project")
        print("3. Go to Project Settings > Database")
        print("4. Under 'Connection Info', copy the 'Connection string'")
        print("5. Make sure your IP is allowed in 'Connection Pooling' settings")
        print("\nIf you're still having issues:")
        print("- Check if your Supabase project is active")
        print("- Try using the direct connection string from your dashboard")
        print("- Verify your IP is not blocked by any firewall")

if __name__ == "__main__":
    test_connection() 