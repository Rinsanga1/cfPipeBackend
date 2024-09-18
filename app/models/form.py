from app.core.db import db

class Form(db.Model):
    __tablename__ = 'form'

    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    form_link = db.Column(db.String(256), nullable=False)
    form_data = db.Column(db.JSON, nullable=False)


    workflow = db.relationship('Workflow', backref=db.backref('forms', lazy=True))
