from app.core.db import db

class Workflow(db.Model):
    __tablename__ = 'workflow'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    workflow_data = db.Column(db.JSON, nullable=False)  # To store JSON data
    

    admin = db.relationship('Admin', backref=db.backref('workflows', lazy=True))