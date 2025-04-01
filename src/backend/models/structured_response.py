from pydantic import BaseModel, Field


class Chemical(BaseModel):
    name: str

class Metabolite(BaseModel):
    name: str
    from_chemical: Chemical

class Organism(BaseModel):
    name: str
    metabolites: list[Metabolite] = Field(default_factory=list)