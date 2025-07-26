from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field

class SimpleQuestData(BaseModel):
    """Modello base per parsing iniziale"""
    destination: str = Field(..., description="Luogo da raggiungere")
    required_item: Optional[str] = Field(None, description="Oggetto richiesto")
    success_condition: str = Field(..., description="Condizione di successo")
    obstacle: str = Field(..., description="Ostacolo principale")
    obstacle_key: str = Field(..., description="Chiave dell'ostacolo")


class EnhancedQuestData(BaseModel):
    """Modello avanzato per PDDL completo"""
    locations: List[str] = Field(default_factory=list, description="Tutti i luoghi")
    items: List[str] = Field(default_factory=list, description="Tutti gli oggetti")
    obstacles: Dict[str, str] = Field(default_factory=dict, description="Mapping location->obstacle")
    connections: List[Tuple[str, str]] = Field(default_factory=list, description="Collegamenti tra luoghi")
    initial_location: str = Field(default="start", description="Posizione iniziale")
    goal_conditions: List[str] = Field(default_factory=list, description="Condizioni di goal")
    branching_factor: Optional[Dict[str, int]] = Field(default=None, description="Limiti sul branching factor")
    depth_constraints: Optional[Dict[str, int]] = Field(default=None, description="Limiti sulla profondità")