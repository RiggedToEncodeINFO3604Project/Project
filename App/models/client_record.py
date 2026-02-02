from App.database import db
from datetime import datetime
from uuid import uuid

class ClientRecord(db.Model):
    __tablename__='client_records'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())) #had to AI this, couldn't remember how to
    total_visits = db.Column(db.Integer, nullable=False, default=0)
    last_visit = db.Column(db.DateTime, default=datetime.now()) #same thing, no logic til we confirm
    