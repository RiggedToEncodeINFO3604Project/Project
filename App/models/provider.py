from App.database import db

class Provider(db.Model):
    __tablename__='providers'
    business_name = db.Column(db.String(100), primary_key=True, unique=True, nullable=False) 
    bio = db.Column(db.String(500), nullable=False) #idk how big to make the string, clarify with group
    address = db.Column(db.String(100), nullable=False) #not gonna do unique incase some buiidings have 2 businesses
    is_onboarded = db.Column(db.Boolean, default=True) #i don't think this is needed, once again requires clarification
    
     