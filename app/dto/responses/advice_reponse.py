from pydantic import BaseModel, Field


class AdviceModel(BaseModel):
    name: str
    desc: str
