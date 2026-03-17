import psycopg2
import os

def get_db_connection():
    # It tries to use the environment variable first, but falls back to your Render URL
    db_url = os.environ.get("DB_URL", "postgresql://kikay_flask_app_db_user:WCP29OzgspBntopEFbE2puALC5J2nPVG@dpg-d6rop4ea2pns73fros6g-a/kikay_flask_app_db")
    
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    grade DECIMAL(5, 2) NOT NULL,
                    section VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Render PostgreSQL initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
