from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class Chemical(BaseModel):
    name: str

class Metabolite(BaseModel):
    name: str
    from_chemical: Chemical

class Organism(BaseModel):
    name: str
    metabolites: list[Metabolite] = Field(default_factory=list)

# Define structured output schema
class RelationshipType(str, Enum):
    ISOLATED_FROM = "ISOLATED_FROM"
    METABOLITE_OF = "METABOLITE_OF"
    PRODUCES = "PRODUCES"
    DEGRADED_BY = "DEGRADED_BY"
    BIOSYNTHESIZED_BY = "BIOSYNTHESIZED_BY"
    INHIBITS = "INHIBITS"
    PRECURSOR_OF = "PRECURSOR_OF"
    UPTAKEN_BY = "UPTAKEN_BY"
    MODIFIES = "MODIFIES"
    SEQUESTERS = "SEQUESTERS"
    CONTAINS = "CONTAINS"

class Relationship(BaseModel):
    entity1: str = Field(..., description="First entity (e.g., chemical, organism)")
    relation: RelationshipType = Field(..., description="Type of relationship")
    entity2: str = Field(..., description="Second entity (e.g., chemical, organism)")

class BioMedicalResponse(BaseModel):
    relationships: List[Relationship] = Field(
        default_factory=list,
        description="List of extracted relationships"
    )
    explanation: str = Field(
        ..., description="Concise natural language explanation of the relationships"
    )