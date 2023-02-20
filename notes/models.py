from pydantic import BaseModel
from typing import Union
from bson.json_util import ObjectId
from datetime import datetime


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


class CreateNote(Base):
    content: str = None
    owner: list[PyObjectId] = []

    def remove_owner(self, v):
        if ObjectId.is_valid(v):
            self.owner.remove(v)
            return True
        return False


class Note(CreateNote):
    updated_at: Union[datetime, None] = None
    created_at: datetime = datetime.now()

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
