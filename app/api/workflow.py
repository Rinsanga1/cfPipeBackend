from flask_restx import Namespace, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Workflow, Admin
from app.core.db import db
import json
import werkzeug

api = Namespace('workflow', description='Workflow management')

# Request parser for workflow creation
parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Workflow name is required', location='form')
parser.add_argument('file', type=werkzeug.datastructures.FileStorage, required=True, help='JSON file is required', location='files')

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('workflow_id', type=int, required=True, help='ID of the workflow to delete', location='args')

@api.route('/')
class WorkflowResource(Resource):
    @api.doc(security="jsonWebToken")
    @jwt_required()
    @api.expect(parser)
    def post(self):
        """Upload a new workflow as a JSON file."""
        args = parser.parse_args()
        name = args['name']
        file = args['file']
        
        try:
            workflow_data = json.load(file)
        except json.JSONDecodeError:
            return {'message': 'Invalid JSON format'}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        
        if not admin:
            return {'message': 'Admin not found'}, 404
        
        new_workflow = Workflow(name=name, workflow_data=workflow_data, admin_id=admin.id)
        
        db.session.add(new_workflow)
        db.session.commit()
        
        return {'message': 'Workflow uploaded successfully', 'workflow_id': new_workflow.id}, 201
    
    @api.doc(security="jsonWebToken")
    @jwt_required()
    @api.expect(delete_parser)
    def delete(self):
        """Delete a workflow by ID."""
        args = delete_parser.parse_args()
        workflow_id = args['workflow_id']
        
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        
        if not admin:
            return {'message': 'Admin not found'}, 404
        
        workflow = Workflow.query.get(workflow_id)
        
        if not workflow:
            return {'message': 'Workflow not found'}, 404
        
        if workflow.admin_id != admin.id:
            return {'message': 'You do not have permission to delete this workflow'}, 403
        

        db.session.delete(workflow)
        db.session.commit()
        
        return {'message': 'Workflow deleted successfully'}, 200
    
    @api.doc(security="jsonWebToken")
    @jwt_required()
    def get(self):
        """Retrieve all workflows."""
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        
        if not admin:
            return {'message': 'Admin not found'}, 404
        
        workflows = Workflow.query.all()
        
        # Format the response
        workflow_list = []
        workflow_list = []
        for workflow in workflows:
            workflow_list.append({
                'id': workflow.id,
                'admin_id': workflow.admin_id,
                'name': workflow.name
            })
        
        return {'workflows': workflow_list}, 200