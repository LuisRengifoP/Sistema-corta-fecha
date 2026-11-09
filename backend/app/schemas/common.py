from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base para schemas de lectura: habilita from_attributes."""

    model_config = ConfigDict(from_attributes=True)
