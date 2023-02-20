import datetime
from typing import Optional, Union
from bson import ObjectId
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


class Currency(BaseModel):
    symbol: Union[str, None] = None
    code: str = "USD"
    name: str = "US Dollar"


class Finance(BaseModel):
    target: float = 0
    now: float = 0
    currency: Currency


class Saving(Base):
    title: str = None
    owner: list[PyObjectId] = []
    description: str = None
    finance: Finance = None
    created_at: datetime.datetime = datetime.datetime.now()
    due_to: Optional[datetime.datetime] = None
    closed_at: Optional[datetime.datetime] = None


class ResponseSaving(Saving):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
