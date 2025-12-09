from pydantic import BaseModel

class ConditionResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
