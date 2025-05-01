import psycopg2
from psycopg2 import OperationalError
import socket
import sys
import time

def test_connection():
    try:
        # Test DNS resolution first
        print("Testing DNS resolution...")
        try:
            host_ip = socket.gethostbyname('aws-0-ap-southeast-2.pooler.supabase.com')
            print(f"Successfully resolved host to IP: {host_ip}")
        except socket.gaierror as e:
            print(f"DNS resolution failed: {e}")
            return

        # Test database connection
        print("\nTesting database connection...")
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres.kgexeshuuoonbrgoyazp',
            password='6XB07HW15D81nxUR',
            host='aws-0-ap-southeast-2.pooler.supabase.com',
            port='6543',
            connect_timeout=30,
            sslmode='require',
            target_session_attrs='read-write',
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
            application_name='test_connection'
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
        print(f"\nDatabase connection error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check if your IP is whitelisted in Supabase Connection Pooling settings")
        print("2. Verify your project is active in Supabase dashboard")
        print("3. Try using a different network (like mobile hotspot)")
        print("4. Check if your firewall is blocking the connection")
        print("5. Verify the connection details in your Supabase dashboard")
        print("\nAdditional checks:")
        print("- Make sure your project is in the ap-southeast-2 region")
        print("- Check if your network allows outbound connections to port 6543")
        print("- Try temporarily disabling your firewall")

if __name__ == "__main__":
    test_connection() 