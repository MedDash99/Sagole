# repo/backend/seed.py
from app.database import SessionLocal, engine
from app.models import User
from sqlalchemy.orm import Session

def seed_data():
    db: Session = SessionLocal()
    try:
        # Check if users already exist
        if db.query(User).count() == 0:
            print("Seeding database with initial users...")
            # In a real app, hash the passwords!
            admin_user = User(
                username='admin',
                email='admin@example.com',
                full_name='Admin User',
                password='adminpassword', # HASH THIS IN A REAL APP
                role='admin'
            )
            regular_user = User(
                username='user',
                email='user@example.com',
                full_name='Regular User',
                password='userpassword', # HASH THIS IN A REAL APP
                role='user'
            )
            db.add(admin_user)
            db.add(regular_user)
            db.commit()
            print("Database seeded successfully.")
        else:
            print("Database already seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()