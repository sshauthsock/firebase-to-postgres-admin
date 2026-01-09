from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.creature_service import (
    get_all_creatures,
    get_creature_by_id,
    create_creature,
    update_creature,
    delete_creature,
    create_or_update_level_stats
)
from app.models.creature import CreatureCreate, CreatureUpdate, CreatureLevelStatsCreate

router = APIRouter(prefix="/creatures", tags=["creatures"])


@router.get("")
def get_creatures(
    name: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    influence: Optional[str] = Query(None)
):
    try:
        return get_all_creatures(name, grade, type, influence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{creature_id}")
def get_creature_details(creature_id: int):
    try:
        creature = get_creature_by_id(creature_id)
        if not creature:
            raise HTTPException(status_code=404, detail=f"Creature {creature_id} not found")
        return creature
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
def create_creature_endpoint(create: CreatureCreate):
    try:
        creature_data = {
            "name": create.name,
            "grade": create.grade,
            "type": create.type,
            "influence": create.influence,
            "image": create.image,
            "initial_bindStat": create.initial_bindStat,
            "initial_registrationStat": create.initial_registrationStat
        }
        new_id = create_creature(creature_data)
        return {"status": "success", "id": new_id}
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
            raise HTTPException(status_code=409, detail="Creature with this name already exists")
        raise HTTPException(status_code=500, detail=error_msg)


@router.put("/{creature_id}")
def update_creature_endpoint(creature_id: int, update: CreatureUpdate):
    try:
        updates = update.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        success = update_creature(creature_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail=f"Creature {creature_id} not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{creature_id}")
def delete_creature_endpoint(creature_id: int):
    try:
        success = delete_creature(creature_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Creature {creature_id} not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stats")
def create_or_update_level_stats_endpoint(create: CreatureLevelStatsCreate):
    try:
        stats_data = {
            "creature_id": create.creature_id,
            "level": create.level,
            "bindStat": create.bindStat,
            "registrationStat": create.registrationStat
        }
        create_or_update_level_stats(stats_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
