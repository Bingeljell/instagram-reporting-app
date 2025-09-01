# add_test_user.py

from database import SessionLocal, User
from datetime import datetime

print("--- Attempting to add a test user to the database ---")

# Get a new database session
db = SessionLocal()

try:
    # Define the test user's data
    test_user_facebook_id = "test_facebook_id_12345"
    test_user_name = "John Doe (Test)"
    test_user_email = "test.user@example.com"

    # Check if this test user already exists
    existing_user = db.query(User).filter(User.facebook_id == test_user_facebook_id).first()

    if existing_user:
        print(f"User '{test_user_name}' already exists. Updating their last login time.")
        existing_user.last_login_at = datetime.utcnow()
    else:
        print(f"Creating new test user: '{test_user_name}'")
        # Create a new User object
        new_user = User(
            facebook_id=test_user_facebook_id,
            name=test_user_name,
            email=test_user_email,
            tier='beta',
            report_count=0,
            last_login_at=datetime.utcnow()
        )
        # Add the new user to the session
        db.add(new_user)
    
    # Commit the transaction to save the changes
    db.commit()
    
    print("\n🎉 SUCCESS! The transaction was completed.")
    print("Please check your 'users' table in the Supabase dashboard.")

except Exception as e:
    print(f"\n❌ FAILED to add test user.")
    print(f"Error: {e}")
    # If an error occurs, roll back the transaction
    db.rollback()
finally:
    # Always close the session
    db.close()
    print("Database session closed.")