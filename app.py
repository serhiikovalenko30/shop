import telebot
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from flask import Flask, request, abort
import config
from cron import Cron
import keyboards
from keyboards import ReplyKB, InlineKB
from models import models

bot = telebot.TeleBot(config.TOKEN)
app = Flask(__name__)


# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''

# Process webhook calls
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@bot.message_handler(func=lambda message: message.text == 'Последнии новости')
def news(message):
    for i in models.Texts.objects(title__startswith='News'):
        bot.send_message(message.chat.id, i.body)


@bot.message_handler(func=lambda message: message.text == 'Информация о магазине')
def about(message):
    text = models.Texts.objects(title='About').get().body
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: message.text == 'История заказов')
def cart_history(message):
    user = models.User.objects(user_id=str(message.from_user.id)).get()

    if not user.get_archive_cart:
        return bot.send_message(message.chat.id, text='У вас нет истории покупок')

    carts_history = user.get_archive_cart

    counter = 1
    for carts in carts_history:
        for cart in carts.cart:
            bot.send_message(message.chat.id, text=f'Cart №{counter}')
            counter += 1
            for products in cart.product:
                product = models.Product.objects(id=products.id).get()
                bot.send_message(message.chat.id, text=f'Title: {product.title}')


@bot.message_handler(func=lambda message: message.text == 'Корзина')
def show_products_in_cart(message):
    user = models.User.objects(user_id=str(message.from_user.id)).get()

    if not models.Cart.objects(user=user.id, active=True):
        return bot.send_message(message.chat.id, text='У вас нет корзины')

    cart = models.Cart.objects(user=user.id, active=True).get()

    if len(cart.product) == 0:
        return bot.send_message(message.chat.id, text='У Вас пустая корзина')

    for products in cart.product:
        product = models.Product.objects(id=products.id).get()
        keyboard = InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text='Удалить товар',
                                                    callback_data='del_' + str(products.id))
        keyboard.add(button)

        bot.send_message(message.chat.id,
                         text=f'Title: {product.title}\n'
                              f'Description: {product.description}\n'
                              f'{"Price (sales):" if product.is_discount else "Price:"}  {product.get_price}',
                         reply_markup=keyboard)

    kb = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(text='Купить товары', callback_data='buy_' + str(user.id))
    kb.add(button)
    bot.send_message(message.chat.id, text=f'Total sum: {cart.sum_product(user.id)}', reply_markup=kb)


@bot.message_handler(func=lambda message: message.text == 'Продукты со скидкой')
def sales(message):
    products = models.Product.objects(is_discount=True)

    for product in products:
        kb = InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text='Добавить в корзину',
                                                    callback_data='cart_' + str(product.id))
        kb.add(button)

        bot.send_photo(message.chat.id, product.photo.read(),
                       parse_mode='HTML',
                       caption=f'Title: {product.title}\n'
                               f'Description: {product.description}\n'
                               f'{"Price (sales):" if product.is_discount else "Price:"}  {product.get_price}',
                       reply_markup=kb)


@bot.message_handler(commands=['start'])
def start(message):

    if not models.User.objects(user_id=str(message.from_user.id)):
        models.User(**{'user_id': str(message.from_user.id), 'user_name': message.from_user.username}).save()

    greetings_str = models.Texts.objects(title='Greetings').get().body
    keyboard = ReplyKB().generate_kb(*keyboards.beginning_kb.values())
    bot.send_message(message.chat.id, greetings_str, reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == keyboards.beginning_kb['products'])
def show_categories(message):
    """
    :param message:
    :return: listed root categories
    """
    kb = keyboards.InlineKB(key='root', lookup_field='id', named_arg='category')
    bot.send_message(message.chat.id, 'Выберите категорию', reply_markup=kb.generate_kb())


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'category')
def show_products_or_sub_categories(call):
    """
    :param call:
    :return: listed sub categories || listed products
    """
    obj_id = call.data.split('_')[1]
    category = models.Category.objects(id=obj_id).get()
    if category.is_parent:
        kb = keyboards.InlineKB(
            iterable=category.subcategory,
            lookup_field='id',
            named_arg='category'
        )
        kb.generate_kb()
        kb.add(InlineKeyboardButton(text='<<', callback_data=f'back_{category.id}'))

        bot.edit_message_text(text=category.title, chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=kb)
    else:
        products = category.get_products()
        for product in products:
            kb = InlineKeyboardMarkup()
            button = telebot.types.InlineKeyboardButton(text='Добавить в корзину',
                                                        callback_data='cart_' + str(product.id))
            kb.add(button)

            bot.send_photo(call.message.chat.id, product.photo.read(),
                           parse_mode='HTML',
                           caption=f'Title: {product.title}\n'
                                   f'Description: {product.description}\n'
                                   f'{"Price (sales):" if product.is_discount else "Price:"}  {product.get_price}',
                           reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'back')
def go_back(call):
    obj_id = call.data.split('_')[1]
    category = models.Category.objects(id=obj_id).get()

    if category.is_root:
        kb = keyboards.InlineKB(key='root', lookup_field='id', named_arg='category')
        kb.generate_kb()
    else:
        kb = keyboards.InlineKB(
            iterable=category.parent.subcategory,
            lookup_field='id',
            named_arg='category'
        )
        kb.generate_kb()
        kb.add(InlineKeyboardButton(text=f'<<', callback_data=f'back_{category.parent.id}'))

    text = 'Категории' if not category.parent else category.parent.title
    bot.edit_message_text(text=text, chat_id=call.message.chat.id,
                          message_id=call.message.message_id, reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'cart')
def add_product_to_cart(call):
    product = models.Product.objects(id=call.data.split('_')[1]).get()
    user = models.User.objects(user_id=str(call.from_user.id)).get()

    if not user.get_cart:
        models.Cart(**{'user': user}).save()

    cart = models.Cart.objects(user=user.id, active=True).get()
    cart.add_product(product)
    cart.save

    bot.send_message(call.message.chat.id, f'{product.title} добавлен в корзину')


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'buy')
def buy_cart(call):
    user = models.User.objects(user_id=str(call.from_user.id)).get()
    cart = models.Cart.objects(user=user.id, active=True).get()

    if not user.get_archive_cart:
        models.HistoryCart(**{'user': user}).save()

    history_cart = models.HistoryCart.objects(user=user.id).get()
    history_cart.add_cart(cart)

    cart.update(active=False)

    bot.send_message(call.message.chat.id, 'Корзина купленна')


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'del')
def delete_product_by_cart(call):
    user = models.User.objects(user_id=str(call.from_user.id)).get()
    product = models.Product.objects(id=call.data.split('_')[1]).get()
    models.Cart.objects(user=user.id, active=True).update_one(pull__product=product)  # deletes everything
    bot.send_message(call.message.chat.id, text='Товар(ы) удален(ы)')


@Cron.cron_decorator()
def is_banned_check():
    for user in models.User.objects():
        try:
            bot.send_chat_action(user.user_id, 'typing')
            models.User.objects(user_id=user.user_id).update_one(set__is_block=False)
        except telebot.apihelper.ApiException:
            models.User.objects(user_id=user.user_id).update_one(set__is_block=True)


cron = Cron(is_banned_check)


if __name__ == '__main__':
    import time

    bot.remove_webhook()
    # time.sleep(1)
    # bot.set_webhook(config.webhook_url,
    #                 certificate=open('webhook_cert.pem', 'r'))
    # cron.run()
    # app.run(debug=True)
    bot.polling(none_stop=True)