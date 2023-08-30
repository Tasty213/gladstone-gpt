from pydantic import BaseModel


class Canvass(BaseModel):
    userId: str
    firstName: str
    lastName: str
    postcode: str
    email: str
    voterIntent: str
    time: str
