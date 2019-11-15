from models import Category, Product
from random import choice, randint

# subcategory = []
# category = []
#
# for i in range(1, 7):
#     subcategory_ex = Category(**{
#         'title': f'sub category number {i}',
#         'description': f'description by sub category number {i}'
#     }).save()
#     subcategory.append(subcategory_ex)
#
# for i in range(1, 4):
#     subcategory_ex = Category(**{
#         'title': f'category number {i}',
#         'description': f'description by category number {i}',
#         'subcategory': [subcategory[i-1], subcategory[i+2]],
#         'parent': True
#     }).save()
#     category.append(subcategory_ex)
#
# for i in range(1, 20):
#     item_ex = {
#         'title': f'Product number {i}',
#         'description': f'Description by product number {i}',
#         'price': randint(100, 1000),
#         'category': choice(subcategory),
#     }
#     Product(**item_ex).save()



# for i in range (5):
#     o = Category(**{
#             'title': f'root {i}',
#             'description': f'description by category number {i}'
#         }).save()
#     o.add_subcategory(Category(**{'title': f'sub {i}', 'description': f'description{i}'}))

# ob = Category.objects(parent__ne=None)
#
# for i in ob:
#     i.add_subcategory(Category(**{'title': f'sub sub {i}', 'description': f'description{i}'}))


