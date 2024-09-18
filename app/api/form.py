from flask_restx import Namespace, Resource, reqparse, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app.models import Form, Workflow, Admin
from app.core.db import db

api = Namespace("form", description="Form management")


# Helper function to get exposed parameters
def get_exposed_inputs(json_data):
    exposed_params = {}
    for node_id, node_data in json_data.items():
        title = node_data.get("_meta", {}).get("title", "")
        if "exposed" in title.lower():
            exposed_params[node_id] = node_data.get("inputs", {})
    return exposed_params


# Swagger models
exposed_params_model = api.model(
    "ExposedParamsRequest",
    {
        "workflow_id": fields.Integer(
            required=True, description="ID of the associated workflow"
        ),
    },
)

select_params_model = api.model(
    "SelectParamsRequest",
    {
        "workflow_id": fields.Integer(
            required=True, description="ID of the associated workflow"
        ),
        "selected_params": fields.Raw(
            required=True,
            description="Dictionary with node IDs as keys and list of parameter names as values",
        ),
    },
)

create_form_model = api.model(
    "CreateFormRequest",
    {
        "workflow_id": fields.Integer(
            required=True, description="ID of the associated workflow"
        ),
        "name": fields.String(required=True, description="Form name"),
        "form_link": fields.String(required=True, description="Form link"),
        "form_data": fields.Raw(
            required=True, description="Form data (selected exposed parameters)"
        ),
    },
)

update_form_model = api.model(
    "UpdateFormRequest",
    {
        "form_data": fields.Raw(
            required=True, description="Updated form data (exposed parameters)"
        )
    },
)


# Step 1: Retrieve Exposed Parameters
@api.route("/exposed_params")
class ExposedParamsResource(Resource):
    @api.doc(security="jsonWebToken")
    @jwt_required()
    @api.expect(exposed_params_model)
    def post(self):
        """Retrieve all exposed parameters of the specified workflow."""
        data = request.get_json()
        workflow_id = data.get("workflow_id")

        # Get the admin
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            return {"message": "Admin not found"}, 404

        # Get the workflow
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return {"message": "Workflow not found"}, 404

        # Check ownership
        if workflow.admin_id != admin.id:
            return {
                "message": "You do not have permission to access this workflow"
            }, 403

        # Get the workflow data
        json_data = workflow.workflow_data

        # Get all exposed parameters
        exposed_params = get_exposed_inputs(json_data)

        return jsonify(exposed_params)


@api.route("/select_exposed_params")
class SelectExposedParamsResource(Resource):
    @api.doc(security="jsonWebToken")
    @jwt_required()
    @api.expect(select_params_model)
    def post(self):
        """
        example usage
        curl -X 'POST' \
  'http://127.0.0.1:5000/form/select_exposed_params' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'Content-Type: application/json' \
  -d '{
  "workflow_id": 1,
  "selected_params": {
    "node_number": 14,
    "key": "upload"
  }
}'
            """
        data = request.get_json()
        workflow_id = data.get("workflow_id")
        selected_param = data.get("selected_params")

        # Get the admin
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            return {"message": "Admin not found"}, 404

        # Get the workflow
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return {"message": "Workflow not found"}, 404

        # Check ownership
        if workflow.admin_id != admin.id:
            return {
                "message": "You do not have permission to access this workflow"
            }, 403

        # Get the workflow data
        json_data = workflow.workflow_data

        # Modify the selected parameter
        node_number = str(selected_param["node_number"])
        key = selected_param["key"]

        if node_number in json_data and "inputs" in json_data[node_number]:
            if key in json_data[node_number]["inputs"]:
                value = json_data[node_number]["inputs"][key]
                if isinstance(value, str):
                    json_data[node_number]["inputs"][key] = f"${{{key}}}"
                elif isinstance(value, int):
                    json_data[node_number]["inputs"][key] = f"%({key})d"
                elif isinstance(value, float):
                    json_data[node_number]["inputs"][key] = f"%({key})f"

        # Update the workflow data in the database
        workflow.workflow_data = json_data
        db.session.commit()

        return jsonify(json_data)


# Step 3: Create a form with the specified exposed parameters
@api.route("/create_form")
class CreateFormResource(Resource):
    @api.doc(security="jsonWebToken")
    @jwt_required()
    @api.expect(create_form_model)
    def post(self):
        """Create a new form with the selected exposed parameters."""
        data = request.get_json()
        workflow_id = data.get("workflow_id")
        name = data.get("name")
        form_link = data.get("form_link")
        form_data = data.get("form_data")

        # Get the admin
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            return {"message": "Admin not found"}, 404

        # Get the workflow
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return {"message": "Workflow not found"}, 404

        # Check ownership
        if workflow.admin_id != admin.id:
            return {
                "message": "You do not have permission to access this workflow"
            }, 403

        # Create a new Form instance
        new_form = Form(
            workflow_id=workflow_id, name=name, form_link=form_link, form_data=form_data
        )

        db.session.add(new_form)
        db.session.commit()

        return {"message": "Form created successfully", "form_id": new_form.id}, 201


# Endpoint to retrieve, update, and delete a specific form
@api.route("/<int:form_id>")
class FormDetailResource(Resource):
    @api.doc(security="jsonWebToken")
    @jwt_required()
    def get(self, form_id):
        """Retrieve the specified form."""
        # Get the admin
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            return {"message": "Admin not found"}, 404

        # Get the form
        form = Form.query.get(form_id)
        if not form:
            return {"message": "Form not found"}, 404

        # Check ownership
        if form.workflow.admin_id != admin.id:
            return {"message": "You do not have permission to access this form"}, 403

        # Format the response
        form_data = {
            "id": form.id,
            "workflow_id": form.workflow_id,
            "name": form.name,
            "form_link": form.form_link,
            "form_data": form.form_data,
        }

        return jsonify(form_data)

    @api.doc(security="jsonWebToken")
    @jwt_required()
    @api.expect(update_form_model)
    def put(self, form_id):
        """Update the exposed parameters of the form."""
        data = request.get_json()
        new_form_data = data.get("form_data")

        # Get the admin
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            return {"message": "Admin not found"}, 404

        # Get the form
        form = Form.query.get(form_id)
        if not form:
            return {"message": "Form not found"}, 404

        # Check ownership
        if form.workflow.admin_id != admin.id:
            return {"message": "You do not have permission to update this form"}, 403

        # Update the form data
        form.form_data = new_form_data
        db.session.commit()

        return {"message": "Form updated successfully"}, 200

    @api.doc(security="jsonWebToken")
    @jwt_required()
    def delete(self, form_id):
        """Delete the specified form."""
        # Get the admin
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            return {"message": "Admin not found"}, 404

        # Get the form
        form = Form.query.get(form_id)
        if not form:
            return {"message": "Form not found"}, 404

        # Check ownership
        if form.workflow.admin_id != admin.id:
            return {"message": "You do not have permission to delete this form"}, 403

        db.session.delete(form)
        db.session.commit()

        return {"message": "Form deleted successfully"}, 200


# Endpoint to retrieve all forms
@api.route("/")
class FormListResource(Resource):
    @api.doc(security="jsonWebToken")
    @jwt_required()
    def get(self):
        """Retrieve all forms associated with the admin."""
        # Get the admin
        admin_email = get_jwt_identity()
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            return {"message": "Admin not found"}, 404

        # Retrieve all forms associated with the admin's workflows
        forms = Form.query.join(Workflow).filter(
            Workflow.admin_id == admin.id).all()

        # Format the response
        form_list = []
        for form in forms:
            form_list.append(
                {
                    "id": form.id,
                    "workflow_id": form.workflow_id,
                    "name": form.name,
                    "form_link": form.form_link,
                    "form_data": form.form_data,
                }
            )

        return jsonify(form_list)
