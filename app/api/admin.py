from flask_restx import Namespace, Resource, reqparse
from flask_jwt_extended import create_access_token
from app.models import Admin

api = Namespace('admin', description='Admin authentication and JWT generation')

parser = reqparse.RequestParser()
parser.add_argument('email', type=str, required=True, help='Admin email is required')
parser.add_argument('password', type=str, required=True, help='Admin password is required')

@api.route('/token')
class AdminToken(Resource):
    @api.expect(parser)
    def post(self):
        """Generate a JWT token for an authenticated admin."""
        args = parser.parse_args() 
        email = args['email']
        password = args['password']
        
        
        admin = Admin.query.filter_by(email=email).first()
        
        
        if not admin or not admin.check_password(password):
            return {'message': 'Invalid credentials'}, 401
        
        
        access_token = create_access_token(identity=email)
        return {'access_token': access_token}, 200
