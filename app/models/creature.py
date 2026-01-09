from pydantic import BaseModel
from typing import Optional, Dict

class CreatureBase(BaseModel):
    name: str
    grade: str
    type: str
    influence: str
    image: str

class CreatureCreate(CreatureBase):
    initial_bindStat: Dict[str, int] = {}
    initial_registrationStat: Dict[str, int] = {}

class CreatureUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    type: Optional[str] = None
    influence: Optional[str] = None
    image: Optional[str] = None

class CreatureLevelStatsCreate(BaseModel):
    creature_id: int
    level: int
    bindStat: Dict[str, int] = {}
    registrationStat: Dict[str, int] = {}