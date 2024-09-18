from flask_restx import Namespace, Resource, reqparse
from app.services.user_service import create_user, authenticate_user

api = Namespace('User', description='User related operations')

user_parser = reqparse.RequestParser()
user_parser.add_argument('email', type=str, required=True, help='Email is required')
user_parser.add_argument('password', type=str, required=True, help='Password is required')

@api.route('/register')
class UserRegister(Resource):
    @api.expect(user_parser)  
    def post(self):
        """Login Existing User"""
        args = user_parser.parse_args()  
        return create_user(args)

@api.route('/login')
class UserLogin(Resource):
    @api.expect(user_parser)  
    def post(self):
        """Register New User"""
        args = user_parser.parse_args()  
        return  authenticate_user(args)