from typing import List, Self
from pydantic import BaseModel, TypeAdapter


class CustomBaseModel(BaseModel):

    @classmethod
    def load_list(cls, data: List[dict]) -> List[Self]:
        return TypeAdapter(List[cls]).validate_python(data)
    
    @classmethod
    def bulk_model_dump(cls, models: List[Self]):
        return [model.model_dump() for model in models]