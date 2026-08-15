import os
from datetime import datetime, timedelta

from passlib.context import CryptContext
from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

# Sets up passlib to use bcrypt. Bcrypt is an adaptive hashing algorithm,
# meaning it is deliberately slow so that brute-force attacks take longer.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # Turns a plain password into a hash. This is what we save in the database,
    # so the real password is never stored anywhere.
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Checks a login attempt against the stored hash.
    # A hash cannot be reversed, so we hash the attempt and compare instead.
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# Token settings
# ---------------------------------------------------------------------------

# Loads the values from our .env file. The secret key is kept out of the code
# and out of GitHub, so it cannot be read by anyone who sees the repository.
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# The algorithm used to sign the token, and how long a login lasts.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    # Builds the JWT that is handed to the user when they log in.
    to_encode = data.copy()

    # Adds an expiry time so an old token cannot be reused forever.
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Signing with the secret key means the token cannot be edited by the user.
    # If someone changed their role to "manager" inside it, the signature breaks.
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# Reading the token on protected routes
# ---------------------------------------------------------------------------

# HTTPBearer reads the token straight from the Authorization header.
# We use this instead of OAuth2PasswordBearer because our /login route accepts
# a JSON body rather than an OAuth2 form. It also means the Swagger "Authorize"
# button shows a single box to paste the token into, which makes testing easier.
bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # Any route that adds Depends(get_current_user) will run this first.
    # If the token is missing, expired or tampered with, the request is rejected.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # HTTPBearer hands back an object, so we pull the token string out of it.
    token = credentials.credentials

    try:
        # Checks the signature and expiry, then reads the contents back out.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # "sub" is the standard JWT field for the subject, which here is the email.
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        # This dictionary is what the route functions receive as current_user.
        return {"email": email, "role": payload.get("role")}

    except JWTError:
        # Covers an expired token, a bad signature, or anything unreadable.
        raise credentials_exception
