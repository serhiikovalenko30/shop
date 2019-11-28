from models.models import Category, Product, Texts
from random import choice, randint

category = []

for i in range(1, 3):
    category_ex = Category(**{
            'title': f'root {i}',
            'description': f'description root {i}'
        }).save()
    category.append(category_ex)

for i in category:
    i.add_subcategory(Category(**{
        'title': f'sub||{i.title}',
        'description': f'description sub'
    }))

for i in Category.objects(parent__ne=None):
    for x in range(1, 3):
        i.add_subcategory(Category(**{
            'title': f'sub-sub||{i.title}',
            'description': f'description sub-sub'
        }))

subcategory = []

for i in Category.objects():
    if not i.is_parent:
        subcategory.append(i)

for i in range(1, 18):
    item_ex = {
        'title': f'Product {i}',
        'description': f'Description {i}',
        'price': randint(1000, 10000),
        'category': choice(subcategory),
    }
    Product(**item_ex).save()

for i in range(18, 22):
    price = randint(1000, 10000)
    item_ex = {
        'title': f'Product {i}',
        'description': f'Description {i}',
        'price': price,
        'new_price': price * 0.5,
        'is_discount': True,
        'category': choice(subcategory),
    }
    Product(**item_ex).save()

Texts(**{'title': 'Greetings', 'body': 'Welcome shop'}).save()

Texts(**{'title': 'About', 'body': 'This is shop  ... '}).save()

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
