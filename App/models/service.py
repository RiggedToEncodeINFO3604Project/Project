from App.database import db

class Service(db.Model):
    __tablename__='services'
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False) #maybe we use this instead
    provided_by = db.Column(db.String(100), db.ForeignKey('providers.business_name'), nullable=False) #this isn't in class dia, i added it
    price = db.Column(db.Float, nullable=False)
    
    