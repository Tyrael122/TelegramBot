from telebot import types

from Utilities.helpers import show_start_menu
from Utilities.database import fetch_cart

from Utilities.Processors.buy import process_client_name
from Utilities.Processors.cart import ask_products_units, remove_from_cart
from Utilities.Processors.photo import show_product_photo

from globals_vars import bot, products_list

@bot.message_handler(commands=['start'])
def send_start(message):
    show_start_menu(
        message, "Hi! I'm a virtual assistent and I'll help you to buy our pizzas! What do you want me to do?")

# Shows the menu


@bot.message_handler(regexp='Show me the menu')
def show_menu(message):
    output_message = ""
    for product in products_list:
        output_message += f"{product['pizza_name']} *(R${product['pizza_price']})*:\n{product['pizza_description']}\n\n"

    bot.send_message(message.chat.id, output_message, parse_mode="Markdown")


# Adds a new product to the cart
@bot.message_handler(regexp='Add product to cart')
def select_product_name(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    for product in products_list:
        markup.add(types.InlineKeyboardButton(
            product['pizza_name'] + " - R$ " + product['pizza_price']))

    sent_message = bot.send_message(
        message.chat.id, "Choose a pizza:", parse_mode="Markdown", reply_markup=markup)
    bot.register_next_step_handler(sent_message, ask_products_units)


# Buy all the products in the cart and adds them to the database
@bot.message_handler(regexp='Buy all products in cart')
def buy_products_in_cart(message):
    cart = fetch_cart(message)
    if len(cart) > 0:
        client_data = {}
        sent_message = bot.send_message(message.chat.id, "What's your name?")
        bot.register_next_step_handler(
            sent_message, process_client_name, client_data)
    else:
        bot.send_message(message.chat.id, "Your cart is empty!")

# Shows the photo of a product


@bot.message_handler(regexp='See a product photo')
def see_product_photo(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for product in products_list:
        markup.add(types.InlineKeyboardButton(
            product['pizza_name'] + " - R$ " + product['pizza_price']))
    sent_message = bot.send_message(
        message.chat.id, "Choose a pizza:", parse_mode="Markdown", reply_markup=markup)

    bot.register_next_step_handler(sent_message, show_product_photo)


# Shows all products in the cart.
@bot.message_handler(regexp='Show my cart')
def see_cart(message):
    cart = fetch_cart(message)
    if len(cart) > 0:
        total_price = 0
        output_message = ""

        for product in cart:
            output_message += f"{product['name']} - *R${product['price']}* - Units: {product['units']}\n"
            total_price += product['price'] * product['units']

        output_message += f"*Total: R$ {round(total_price, 2)}*"

        bot.send_message(message.chat.id, output_message,
                         parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Your cart is empty!")


# Removes a product from the cart.
@bot.message_handler(regexp='Remove a product from cart')
def select_item_to_remove(message):
    cart = fetch_cart(message)
    if len(cart) > 0:
        markup = types.ReplyKeyboardMarkup(row_width=2)

        for product in cart:
            markup.add(types.InlineKeyboardButton(
                f"{product['name']} - R${product['price']} - Units: {product['units']}\n"))
        sent_message = bot.send_message(
            message.chat.id, "Choose an item to remove:", reply_markup=markup)
        bot.register_next_step_handler(sent_message, remove_from_cart)
    else:
        bot.send_message(message.chat.id, "Your cart is empty!")


# Starts the bot.
bot.infinity_polling()
