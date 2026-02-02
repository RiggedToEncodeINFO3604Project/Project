from App.database import db

class Customer(db.Model):
    __tablename__='customers'
    name = db.Column(db.String(100), nullable=False, unique=True, primary_key=True)
    phone = db.Column(db.String(12), nullable=False, unique=True)