from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProcessingMetric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    request_type = Column(String)  # text, srt, video_soft, video_hard
    status = Column(String)        # 'completed', 'failed', 'processing'
    
    # Performance
    audio_duration = Column(Float)  # Durée de l'échantillon (sec)
    compute_time = Column(Float)    # Temps de calcul total (sec)
    
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
