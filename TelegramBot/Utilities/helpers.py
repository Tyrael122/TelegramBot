from telebot import types
import json


# Reads the list of products from a json file


def load_products():
    with open("pizzas.json", "r") as pizzasJson:
        data = pizzasJson.readlines()
        products_list = json.loads(data[0])
        return products_list

# Returns the product name stripped of what comes after the hifen (it should be the details).


def clean_product_name(product_name):
    return product_name[0:product_name.find(' -')]

from globals_vars import bot

# Takes a text to show and displays the startup buttons.
def show_start_menu(message, text):
    markup = types.ReplyKeyboardMarkup(row_width=2)

    menu_btn = types.KeyboardButton('Show me the menu \U0001F4C4')
    cart_btn = types.KeyboardButton('Show my cart \U0001F6CD')
    add_cart_btn = types.KeyboardButton('Add product to cart \u2795')
    buy_cart_btn = types.KeyboardButton('Buy all products in cart \U0001F4B5')
    see_photo_btn = types.KeyboardButton('See a product photo \U0001F4F7')
    remove_cart_btn = types.KeyboardButton(
        'Remove a product from cart \U0001F5D1')

    markup.add(menu_btn, cart_btn, add_cart_btn,
               buy_cart_btn, see_photo_btn, remove_cart_btn)
    bot.send_message(message.chat.id, text=text, reply_markup=markup)
