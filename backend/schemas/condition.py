from pydantic import BaseModel


class ConditionResponse(BaseModel):
    id: int
    name: str
    sort_order: int

    class Config:
        from_attributes = True
