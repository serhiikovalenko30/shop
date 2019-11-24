from flask_restful import Resource
from flask import request, jsonify, abort

from models.models import Category, Product, Texts
from schemes.shop_schemes import TextsSchema, CategorySchema, ProductSchema


class TextsResource(Resource):
    def get(self, id=None):
        if not id:
            return TextsSchema().dump(Texts.objects, many=True)
        return TextsSchema().dump(Texts.objects(id=id).get())

    def post(self):
        item = Texts(**request.json).save()
        return TextsSchema().dump(item)

    def put(self, id):
        obj = Texts.objects(id=id).get()
        obj.update(**request.json)
        return TextsSchema().dump(obj.reload())

    def delete(self, id):
        if not id:
            abort(404, message='ID incorrect')
        TextsSchema().dump(Texts.objects(id=id).delete())


class CategoryResource(Resource):
    def get(self, id=None):
        if not id:
            return CategorySchema().dump(Category.objects, many=True)
        return CategorySchema().dump(Category.objects(id=id).get())

    def post(self, id=None):

        if id:
            category = Category.objects(id=id).get()
            sub_category = Category(**request.json).save()
            category.add_subcategory(sub_category)
            return CategorySchema().dump(sub_category)

        item = Category(**request.json).save()
        return CategorySchema().dump(item)

    def put(self, id):
        obj = Category.objects(id=id).get()
        obj.update(**request.json)
        return CategorySchema().dump(obj.reload())

    def delete(self, id):
        if not id:
            abort(404, message='ID incorrect')
        CategorySchema().dump(Category.objects(id=id).delete())


class ProductResource(Resource):
    def get(self, id=None):
        if not id:
            return ProductSchema().dump(Product.objects, many=True)
        return ProductSchema().dump(Product.objects(id=id).get())

    def post(self):
        category = request.json.pop('category')
        request.json['category'] = Category.objects(id=(category['id'])).get()
        item = Product(**request.json).save()
        return ProductSchema().dump(item)

    def put(self, id):
        obj = Product.objects(id=id).get()
        obj.update(**request.json)
        return ProductSchema().dump(obj.reload())

    def delete(self, id):
        if not id:
            abort(404, message='ID incorrect')
        ProductSchema().dump(Product.objects(id=id).delete())
