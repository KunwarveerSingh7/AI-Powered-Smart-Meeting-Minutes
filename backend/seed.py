from database import SessionLocal
from auth_utils import hash_password
import models

db = SessionLocal()

existing = (
    db.query(models.User)
    .filter(models.User.email == "manager@example.com")
    .first()
)

if existing:
    print("Manager already exists, id:", existing.id)
else:
    manager = models.User(
        email="manager@example.com",
        hashed_password=hash_password("Test1234"),
        role="manager",
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    print("Created manager, id:", manager.id)

db.close()