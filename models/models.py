from mongoengine import *

connect('shop')


class Texts(Document):
    title = StringField(unique=True)
    body = StringField(max_length=4096)


class Properties(DynamicEmbeddedDocument):
    weight = FloatField(min_value=0)


class Category(Document):
    title = StringField(max_length=255, required=True)
    description = StringField(max_length=512)
    subcategory = ListField(ReferenceField('self'))
    #archived is_root = BooleanField(default=False)
    parent = ReferenceField('self')

    @classmethod
    def get_root_category(cls):
        #archived return cls.objects(is_root=True)
        return cls.objects(parent=None)

    @property
    def is_parent(self):
        return bool(self.subcategory)

    @property
    def is_root(self):
        return not bool(self.parent)

    @property
    def get_products(self, **kwargs):
        return Product.objects(category=self, **kwargs)

    def add_subcategory(self, obj):
        obj.parent = self
        obj.save()
        self.subcategory.append(obj)
        self.save()


class Product(Document):
    title = StringField(max_length=255)
    description = StringField(max_length=1024)
    price = IntField(min_value=0)
    new_price = IntField(min_value=0)
    is_discount = BooleanField(default=False)
    properties = EmbeddedDocumentField(Properties)
    category = ReferenceField(Category)
    photo = FileField()

    @property
    def get_price(self):
        if self.is_discount:
            return str(self.new_price / 100)
        return str(self.price / 100)

    @classmethod
    def get_discount_products(cls, **kwargs):
        return cls.objects(is_discount=True, **kwargs)


class User(Document):
    user_id = StringField(max_length=124)
    user_name = StringField(max_length=124)

    @property
    def get_cart(self):
        return Cart.objects(user=self, active=True)

    @property
    def get_archive_cart(self):
        return HistoryCart.objects(user=self)


class Cart(Document):
    user = ReferenceField(User)
    product = ListField(ReferenceField(Product))
    active = BooleanField(default=True)

    def sum_product(self, user):
        products_sum = 0
        cart = Cart.objects(user=user, active=True).get()
        for product in cart.product:
            products_sum += float(product.get_price)
        return products_sum

    def add_product(self, obj):
        # obj.parent = self
        # obj.save()
        self.product.append(obj)
        self.save()


class HistoryCart(Document):
    user = ReferenceField(User)
    cart = ListField(ReferenceField(Cart))

    def add_cart(self, obj):
        self.cart.append(obj)
        self.save()
