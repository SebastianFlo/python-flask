import os

from flask import Flask
from flask import jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST

# from datetime import timedelta

# database is created based on this
# from security import authenticate, identity
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, Items
from resources.store import Store, Stores

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.secret_key = 'jose'  # this should be a secret
api = Api(app)

jwt = JWTManager(app)

@jwt.token_in_blacklist_loader
def check_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1: # This should be in a db
        return { 'is_admin': True}
    return {'is_admin': False}

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token has expired',
        'error': {
            'message': 'token_expired'
        }
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed',
        'error': {
            'message': 'invalid_token'
        }
    }), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token',
        'error': {
            'message': 'unauthorized'
        }
    }), 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(error):
    return jsonify({
        'description': 'Fresh token required',
        'error': {
            'message': 'needs_fresh_token'
        }
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'The token has been revoked',
        'error': {
            'message': 'revoked_token'
        }
    }), 401


port = 5000

api.add_resource(Item, '/items/<string:name>')
api.add_resource(Items, '/items')
api.add_resource(Store, '/stores/<string:name>')
api.add_resource(Stores, '/stores')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=port, debug=True)
