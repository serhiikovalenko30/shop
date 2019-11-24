from flask import Flask
from flask_restful import Api

from resources.shop_resources import CategoryResource, ProductResource, TextsResource


app = Flask(__name__)
api = Api(app)

api.add_resource(CategoryResource,  '/category/', '/category/<string:id>')
api.add_resource(ProductResource, '/product/', '/product/<string:id>')
api.add_resource(TextsResource, '/text/', '/text/<string:id>')


if __name__ == '__main__':
    app.run()
