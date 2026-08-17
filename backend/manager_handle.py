#Source 1
#https://docs.sqlalchemy.org/en/20/orm/session_basics.html
# used to communicate with database, session establishes all communications
#Source 2
#https://www.geeksforgeeks.org/python/hashing-passwords-in-python-with-bcrypt
# password hashing used from the auth utils


from database import SessionLocal, Base, engine
from models import User   
from auth_utils import hash_password

#make sure the required database tables exist and open new database session
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# default login detials for the manager
email = "manager@meetingminute.com"
password = "Manager123!"

#before creating the manager, check the database so that duplicate account would not be created upon running this file
existing_user = db.query(User).filter(User.email == email).first()

#no need to create a new account one already exists
if existing_user:
    print(f"Manager account with email '{email}' already exists.")
else:
    #create manager account with hashed password
    manager_user = User(
        email=email,
        hashed_password=hash_password(password),
        role="manager"
    )
    #new manager added and saved in the database file
    db.add(manager_user)
    db.commit()

    #upon running this script success message is printed out in the terminal.

    print ("Manager account created successfully.")
    print (f"Email: {email}")
    print (f"Password: {password}")

#session closed
db.close()
