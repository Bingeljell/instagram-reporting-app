# database.py

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote_plus

# --- 1. LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

# --- 2. ROBUST DATABASE CONNECTION SETUP ---
# Fetch individual, safe connection parameters from the .env file
USER = os.getenv("SUPABASE_USER")
PASSWORD = os.getenv("SUPABASE_PASSWORD")
HOST = os.getenv("SUPABASE_HOST")
PORT = os.getenv("SUPABASE_PORT")
DBNAME = os.getenv("SUPABASE_DBNAME")

# Check if all necessary variables are present
if not all([USER, PASSWORD, HOST, PORT, DBNAME]):
    raise ValueError("Missing one or more required Supabase environment variables (SUPABASE_USER, SUPABASE_PASSWORD, etc.)")

# URL-encode the password to handle any special characters safely.
# This is a best practice even if the password is URL-safe.
encoded_password = quote_plus(PASSWORD)

# Construct the final, safe DATABASE_URL for SQLAlchemy
DATABASE_URL = f"postgresql://{USER}:{encoded_password}@{HOST}:{PORT}/{DBNAME}"

# --- 3. SQLAlchemy ENGINE & SESSION SETUP ---
# This part remains the same, but now uses our robustly constructed URL.
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print("❌ Failed to create SQLAlchemy engine. Please check your DATABASE_URL.")
    print(f"Error: {e}")
    # Exit or handle the error appropriately if the script continues
    exit()

# --- 4. USER TABLE DEFINITION ("MODEL") ---
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    facebook_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    tier = Column(String, default='beta', nullable=False)
    report_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, default=datetime.utcnow)

# --- 5. DATABASE INTERACTION FUNCTIONS ---

def get_db():
    """Dependency to get a DB session for a single transaction."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create the database tables if they don't exist."""
    print("Attempting to initialize the database and create tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"❌ An error occurred during database initialization: {e}")

def get_user_by_facebook_id(db, facebook_id: str):
    """Retrieve a user from the DB by their Facebook ID."""
    return db.query(User).filter(User.facebook_id == facebook_id).first()

def create_user(db, facebook_id: str, name: str, email: str):
    """Create a new user record in the DB."""
    new_user = User(
        facebook_id=facebook_id,
        name=name,
        email=email,
        tier='beta' # All new users start on the 'beta' tier
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# This allows the init_db command to be run from the terminal as before.
# Example: python -c "from database import init_db; init_db()"