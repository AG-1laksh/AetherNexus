from fastapi import APIRouter, HTTPException
from models import EquipmentResponse
import database

router = APIRouter()

@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(equipment_id: str):
    """
    Looks up equipment by ID/name and returns its maintenance and
    failure history derived from the Knowledge Graph.
    """
    try:
        record = database.get_equipment_by_id(equipment_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Equipment '{equipment_id}' not found.")

        return EquipmentResponse(
            id=equipment_id.upper(),
            name=record["name"],
            location=record.get("location"),
            maintenance_count=record["maintenance_count"],
            failure_count=record["failure_count"],
            last_inspection=record.get("last_maintenance"),
            last_maintenance=record.get("last_maintenance"),
            status="operational" if record["failure_count"] == 0 else "under review",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
