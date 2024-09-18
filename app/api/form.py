from flask_restx import Namespace, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Form, Workflow, Admin
from app.core.db import db
import json
import werkzeug

api = Namespace('form', description='Form management')


parser = reqparse.RequestParser()
parser.add_argument('workflow_id', type=int, required=True, help='ID of the associated workflow', location='form')
parser.add_argument('name', type=str, required=True, help='Form name is required', location='form')
parser.add_argument('form_link', type=str, required=True, help='Form link is required', location='form')
parser.add_argument('file', type=werkzeug.datastructures.FileStorage, required=True, help='JSON file is required', location='files')

# Request parser for deleting a form
delete_parser = reqparse.RequestParser()
delete_parser.add_argument('form_id', type=int, required=True, help='ID of the form to delete', location='args')

@api.route('/')
class FormResource(Resource):
    @api.doc(security="jsonWebToken")
    @jwt_required()
    @api.expect(parser)
    def post(self):
        """Upload a new form associated with a workflow."""
        args = parser.parse_args()
        workflow_id = args['workflow_id']
        name = args['name']
        form_link = args['form_link']
        file = args['file']
        
        try:
            form_data = json.load(file)
        except json.JSONDecodeError:
            return {'message': 'Invalid JSON format'}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        # Check if the workflow exists
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return {'message': 'Workflow not found'}, 404
        
        # Get the admin ID from the JWT token
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        
        if not admin:
            return {'message': 'Admin not found'}, 404
        
        # Create a new Form instance
        new_form = Form(workflow_id=workflow_id, name=name, form_link=form_link, form_data=form_data)
        
        db.session.add(new_form)
        db.session.commit()
        
        return {'message': 'Form uploaded successfully', 'form_id': new_form.id}, 201
    
    @api.doc(security="jsonWebToken")
    @jwt_required()
    @api.expect(delete_parser)
    def delete(self):
        """Delete a form by ID."""
        args = delete_parser.parse_args()
        form_id = args['form_id']
        
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        
        if not admin:
            return {'message': 'Admin not found'}, 404
        
        form = Form.query.get(form_id)
        
        if not form:
            return {'message': 'Form not found'}, 404
        
        # Check if the form is associated with the admin's workflow (optional)
        if form.workflow.admin_id != admin.id:
            return {'message': 'You do not have permission to delete this form'}, 403
        
        db.session.delete(form)
        db.session.commit()
        
        return {'message': 'Form deleted successfully'}, 200
    
    @api.doc(security="jsonWebToken")
    @jwt_required()
    def get(self):
        """Retrieve all forms."""
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        
        if not admin:
            return {'message': 'Admin not found'}, 404
        
        forms = Form.query.all()
        
        # Format the response
        form_list = []
        for form in forms:
            form_list.append({
                'id': form.id,
                'workflow_id': form.workflow_id,
                'name': form.name,
                'form_link': form.form_link,
                'form_data': form.form_data
            })
        
        retur