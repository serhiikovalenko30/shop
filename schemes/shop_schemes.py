from marshmallow import fields, Schema, validates, ValidationError


class PropertiesSchema(Schema):
    weight = fields.Float()


class TextsSchema(Schema):
    id = fields.String()
    title = fields.String()
    body = fields.String()


class CategorySchema(Schema):
    id = fields.String()
    title = fields.String()
    description = fields.String()
    subcategory = fields.Nested('self', many=True, only=('id', 'title'))
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
    # photo = fields.Field()  # dont work by image
