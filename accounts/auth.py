from passlib.context import CryptContext
from .models import UserInDB, ResponseUser
import re
from db import client
from random import choices
from string import ascii_letters, digits


def generate_username():
    ran = ''.join(choices(ascii_letters + digits, k=16))
    return ran


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    if "@" in username:
        user_dict = client["user"].find_one({"email": username})
    else:
        user_dict = client["user"].find_one({"username": username})
    if user_dict is None:
        return False
    return UserInDB(**user_dict)


def authenticate_user(username, password):
    user = get_user(username)
    if not user:
        return False

    if not verify_password(password, user.hashed):
        return False
    return ResponseUser(**user.dict(exclude_defaults=True))


def check_username(username):
    if "@" in username:
        user = client["user"].count_documents({"email": username})
        if user > 0:
            return "email"
    else:
        user = client["user"].count_documents({"username": username})
        if user > 0:
            return "username"
    return True


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


def check_if_email(email):
    # pass the regular expression
    # and the string into the fullmatch() method
    if re.fullmatch(regex, email):
        return True
    else:
        return False
