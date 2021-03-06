from flask_restful import Resource
from flask_restful import reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    get_jwt_identity,
    fresh_jwt_required
)
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="price cannot be missing")

    parser.add_argument('store_id',
        type=int,
        required=True,
        help="store_id cannot be missing")

    @jwt_required
    def get(self,
    name):
        item = ItemModel.find_by_name(name)

        if item:
            return item.json()
        else:
            return {'message': 'Item not found'}, 404

    @fresh_jwt_required
    def post(self, name):

        if ItemModel.find_by_name(name):
            return {
                'error': 'Item with that name `{}` already exists'.format(name)
            }, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        item.save_to_db()

        return item.json(), 201

    @jwt_required
    def delete(self, name):
        # use claims here
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin priviledge required'}, 401

        item = ItemModel.find_by_name(name)

        if item:
            item.delete_from_db()
        # connection = sqlite3.connect('data.db')
        # cursor = connection.cursor()

        # query = 'DELETE FROM items WHERE name=?'
        # cursor.execute(query, (name, ))

        # connection.commit()
        # connection.close()

        return {'message': '{} Item Deleted'.format(name)}

    @jwt_required
    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']

        item.save_to_db()

        return item.json(), 201


class Items(Resource):

    @jwt_optional
    def get(self):
        user_id= get_jwt_identity()

        items = [item.json() for item in ItemModel.find_all()]

        if user_id:
            return {'items': items}, 200
        return {
            'items': [item['name'] for item in items],
            'message': 'More data available if you log in'
        }, 200
