# database.py


from urllib.parse import quote_plus
from datetime import datetime
import os
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func, or_, update
from sqlalchemy.orm import sessionmaker, relationship, synonym, declarative_base



USER = os.getenv("SUPABASE_USER")                      
PASSWORD = os.getenv("SUPABASE_PASSWORD", "")
HOST = os.getenv("SUPABASE_HOST")                      
PORT = int(os.getenv("SUPABASE_PORT", "6543"))
DBNAME = os.getenv("SUPABASE_DB") or os.getenv("SUPABASE_DBNAME") or "postgres"

# Basic validation
missing = [k for k, v in {
    "SUPABASE_USER": USER,
    "SUPABASE_PASSWORD": PASSWORD,
    "SUPABASE_HOST": HOST,
}.items() if not v]
if missing:
    raise ValueError(f"Missing Supabase settings: {', '.join(missing)}")

def _connect():
# Connect exactly like the working db_connection_test.py
    return psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        sslmode="require",
    )
engine = create_engine("postgresql+psycopg2://", pool_pre_ping=True, creator=_connect)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 4. USER TABLE DEFINITION ("MODEL") ---
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    facebook_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)    

    subscription_tier = Column('tier', String, default='beta', nullable=False)
    tier = synonym('subscription_tier')
    subscription_expires_at = Column(DateTime, nullable=True) # For time-based trials
    stripe_customer_id = Column(String, unique=True, nullable=True, index=True)
    
    report_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, default=datetime.utcnow)

# -- Invite codes 

class InviteCode(Base):
    __tablename__ = "invite_codes"
    id = Column(Integer, primary_key=True)
    code_text = Column(String, unique=True, nullable=False, index=True)
    grants_tier = Column(String, nullable=False)          # e.g., 'pro' | 'agency'
    max_uses = Column(Integer, nullable=True)
    use_count = Column(Integer, nullable=False, server_default='0')
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserInviteCode(Base):
    __tablename__ = "user_invite_codes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invite_code_id = Column(Integer, ForeignKey("invite_codes.id"), nullable=False)
    used_at = Column(DateTime(timezone=True), server_default=func.now())

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
    print(f"--- DB: Querying for user with facebook_id: {facebook_id}")
    user = db.query(User).filter(User.facebook_id == facebook_id).first()
    if user:
        print(f"--- DB: Found user: {user.name}")
    else:
        print("--- DB: User not found.")
    return user

def create_user(db, facebook_id: str, name: str, email: str):
    """Create a new user record in the DB."""
    print(f"--- DB: Attempting to create new user '{name}' with email '{email}'")
    new_user = User(
        facebook_id=facebook_id,
        name=name,
        email=email,
        subscription_tier='beta'
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"--- DB: Successfully created and committed user with ID: {new_user.id}")
        return new_user
    except Exception as e:
        print(f"--- DB: ERROR! Failed to commit new user. Rolling back. Error: {e}")
        db.rollback()
        return None

def redeem_invite_code(db, user: User, code_text: str):
    # single-row atomic UPDATE … RETURNING to avoid race conditions on use_count
    stmt = (
        update(InviteCode)
        .where(InviteCode.code_text == code_text)
        .where(or_(InviteCode.expires_at.is_(None), InviteCode.expires_at > func.now()))
        .where(or_(InviteCode.max_uses.is_(None), InviteCode.use_count < InviteCode.max_uses))
        .values(use_count=InviteCode.use_count + 1)
        .returning(InviteCode.id, InviteCode.grants_tier)
    )
    row = db.execute(stmt).first()
    if not row:
        return False, "Invalid or expired code, or usage limit reached."

    invite_code_id, grants_tier = row
    # upgrade user tier
    user.subscription_tier = grants_tier
    db.add(UserInviteCode(user_id=user.id, invite_code_id=invite_code_id))
    db.commit()
    db.refresh(user)
    return True, grants_tier

# Run : python -c "from database import init_db; init_db()"