from flask_restx import Api
from .admin import api as admin_ns
from .user import api as user_ns
from .workflow import api as workflow_ns
# Import other namespaces as needed

authorizations = {
    "jsonWebToken": {"type": "apiKey", "in": "header", "name": "Authorization"}
}

api = Api(
    title='ComfyUi API',
    version='1.0',
    description='Backend Api for ComfyUI',
    authorizations=authorizations,
)

api.add_namespace(admin_ns, path='/admin')
api.add_namespace(user_ns, path='/user')
api.add_namespace(workflow_ns, path='/workflow')
# Add other namespaces as needed

