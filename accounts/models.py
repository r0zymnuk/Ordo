from pydantic import BaseModel, Field
from typing import Union
from bson.json_util import ObjectId


class Base(BaseModel):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PyObjectId(ObjectId):
    """ Custom Type for reading MongoDB IDs """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid object_id")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(Base):
    username: str
    email: Union[str, None] = None
    name: Union[str, None] = None
    full_name: Union[str, None] = None
    currency: str = "USD"


class ResponseUser(User):
    id: Union[PyObjectId, None] = Field(default_factory=PyObjectId, alias="_id")


class UserInDB(ResponseUser):
    hashed: str
