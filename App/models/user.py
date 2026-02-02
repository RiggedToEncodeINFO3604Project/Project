from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False) #later assign customer, provider, admin =
    date_created = db.Column(db.DateTime, default=datetime.now())
    last_login = db.column(db.DateTime, default=datetime.now())
    #the logic for the date created and last login is missing, will fix once we get confirmation to go forward
    #Will add relationships once we confirm the uml class dia

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

