import datetime
from typing import Optional
from typing import Union

from bson.json_util import ObjectId
from pydantic import BaseModel, Field


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


class ToDo(BaseModel):
    id: Union[PyObjectId, None] = Field(default_factory=PyObjectId, alias="_id")
    status: str = "In work..."
    description: Optional[str] = None
    task: str
    owner: PyObjectId = None
    created_at: datetime.datetime = datetime.datetime.now()
    due_to: Union[datetime.datetime, None] = None
