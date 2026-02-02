from app.schemas.metrics import ProcessingMetric
from sqlalchemy import func
from sqlalchemy.orm import Session


class MonitoringService:
    def __init__(self, db: Session):
        self.db = db

    def get_admin_stats(self):
        # Nombre total d'inférences
        total = self.db.query(ProcessingMetric).count()
        
        # Temps de calcul moyen
        avg_compute = self.db.query(func.avg(ProcessingMetric.compute_time)).scalar() or 0
        
        # Inférences par type et statut
        stats_by_type = self.db.query(
            ProcessingMetric.request_type, 
            func.count(ProcessingMetric.id)
        ).group_by(ProcessingMetric.request_type).all()

        failed_by_type = self.db.query(
            ProcessingMetric.request_type, 
            func.count(ProcessingMetric.id)
        ).filter(ProcessingMetric.status == 'failed').group_by(ProcessingMetric.request_type).all()

        return {
            "total_inferences": total,
            "avg_compute_time": round(avg_compute, 2),
            "stats_by_type": dict(stats_by_type),
            "failed_by_type": dict(failed_by_type),
            "unfinished_count": self.db.query(ProcessingMetric).filter(ProcessingMetric.status == 'processing').count()
        }
