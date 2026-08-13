from database import SessionLocal, Base, engine
from models import User
from auth_utils import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

email = "manager@meetingminute.com"
password = "Manager123!"
existing_user = db.query(User).filter(User.email == email).first()

if existing_user:
    print(f"Manager account with email '{email}' already exists.")
else:
    manager_user = User(
        email=email,
        hashed_password=hash_password(password),
        role="manager"
    )
    db.add(manager_user)
    db.commit()

    print ("Manager account created successfully.")
    print (f"Email: {email}")
    print (f"Password: {password}")

db.close()
