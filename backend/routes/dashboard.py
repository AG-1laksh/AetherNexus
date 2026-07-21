from fastapi import APIRouter, HTTPException
from models import DashboardResponse, MostFailedEquipment
import database

router = APIRouter()

@router.get("/", response_model=DashboardResponse)
async def get_dashboard():
    """
    Aggregated stats for the Dashboard page: document/equipment/maintenance
    totals plus chart data derived from the Knowledge Graph.
    """
    try:
        stats = database.get_dashboard_stats()
        if stats is None:
            raise HTTPException(status_code=503, detail="Graph database is unavailable.")

        most_failed = None
        if stats["equipment_failures"]:
            top = stats["equipment_failures"][0]
            most_failed = MostFailedEquipment(id=top["name"], name=top["name"], failures=top["failures"])

        return DashboardResponse(
            totals=stats["totals"],
            most_failed_equipment=most_failed,
            charts={
                "equipment_failures": stats["equipment_failures"],
                "documents_uploaded": stats["documents_uploaded"],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
