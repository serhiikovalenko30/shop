from marshmallow import fields, Schema, validates, ValidationError


class PropertiesSchema(Schema):
    weight = fields.String()


class TextsSchema(Schema):
    id = fields.String()
    title = fields.String()
    body = fields.String()


class CategorySchema(Schema):
    id = fields.String()
    title = fields.String()
    description = fields.String()
    subcategory = fields.List(fields.Nested('self'))
    parent = fields.Nested('self')


class ProductSchema(Schema):
    id = fields.String()
    title = fields.String()
    description = fields.String()
    price = fields.Integer()
    new_price = fields.Integer()
    is_discount = fields.Boolean()
    properties = fields.Nested(PropertiesSchema)
    category = fields.Nested(CategorySchema)
    photo = fields.Field()
