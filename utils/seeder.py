from models.models import Category, Product, Texts
from random import choice, randint

category = []

for i in range(1, 3):
    category_ex = Category(**{
            'title': f'root category {i}',
            'description': f'description by root category {i}'
        }).save()
    category.append(category_ex)

for i in category:
    i.add_subcategory(Category(**{
        'title': f'sub category by {i.title}',
        'description': f'description by sub category {i.title}'
    }))

for i in Category.objects(parent__ne=None):
    for x in range(1, 3):
        i.add_subcategory(Category(**{
            'title': f'sub-sub category by {i.title}',
            'description': f'description by sub-sub category {i.title}'
        }))

subcategory = []

for i in Category.objects():
    if not i.is_parent:
        subcategory.append(i)

for i in range(1, 20):
    item_ex = {
        'title': f'Product {i}',
        'description': f'Description by product {i}',
        'price': randint(100, 1000),
        'category': choice(subcategory),
    }
    Product(**item_ex).save()


Texts(**{'title': 'Greetings', 'body': 'Welcome shop'}).save()

Texts(**{'title': 'About', 'body': 'This shop is best'}).save()

for i in range(1, 6):
    news_ex = {
        'title': f'News {i}',
        'body': f'Body news {i}'
    }
    Texts(**news_ex).save()


for product in Product.objects:
    photo = open('product.jpg', 'rb')
    product.photo.put(photo, content_type='image/jpeg')
    product.save()
