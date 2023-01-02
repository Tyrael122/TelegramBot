import telebot
import sqlite3
import os
from datetime import datetime
from telebot import types
from helpers import *

# Creates the bot based on the bot token.
bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_KEY'))

# Loads the list of products based on the JSON file.
products_list = load_products()

# The cart and the client data are initially empty.
cart = []
client_data = {}



@bot.message_handler(commands=['start'])
def send_start(message):
    show_start_menu(
        message, "Hi! I'm a virtual assistent and I'll help you to buy our pizzas! What do you want me to do?", bot)


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

# Asks the user for how many units they want to buy


def ask_products_units(message):
    input_name = clean_product_name(message.text)

    for product in products_list:
        if product['pizza_name'] == input_name:
            sent_message = bot.send_message(
                message.chat.id, "How many units do you want?")
            bot.register_next_step_handler(sent_message, add_to_cart, product)


# Adds the product to the cart
def add_to_cart(message, product):
    if message.text.isdigit():
        units = int(message.text)
        if units > 0:
            name = product['pizza_name']
            price = float(product['pizza_price'])

            product = {"product_name": name,
                       "product_price": price, "quantity": units}

            cart.append(product)

            total_price, total_units = 0, 0
            for product in cart:
                total_price += product['product_price'] * product['quantity']
                total_units += product['quantity']

            bot.send_message(
                message.chat.id, f"Added {name} to the cart!\nCart Size: {total_units}\nCart total price: R${round(total_price, 2)}")

            show_start_menu(message, "What else do you want me to do?", bot)
        else:
            bot.send_message(message.chat.id, "Units must be greater than 0!")

    else:
        bot.send_message(message.chat.id, "That's not a valid number!")


@bot.message_handler(regexp='Buy all products in cart')
def buy_products_in_cart(message):
    if len(cart) > 0:
        sent_message = bot.send_message(message.chat.id, "What's your name?")
        bot.register_next_step_handler(sent_message, process_client_name)
    else:
        bot.send_message(message.chat.id, "Your cart is empty!")


def process_client_name(message):
    client_data['name'] = message.text
    sent_message = bot.send_message(
        message.chat.id, "What's your shipping address?")
    bot.register_next_step_handler(sent_message, process_client_address)


def process_client_address(message):
    client_data['address'] = message.text

    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    markup.add(types.KeyboardButton(
        "Share your phone with us", request_contact=True))
    sent_message = bot.send_message(
        message.chat.id, "Would you give us access to your phone number, so as to call you if necessary?", reply_markup=markup)
    bot.register_next_step_handler(sent_message, process_client_phone)


def process_client_phone(message):
    phone_number = message.contact.phone_number
    phone_number = phone_number.strip('55') # Brazil's international code. Not needed if in Brazil.
    client_data['phone'] = phone_number

    connection = sqlite3.connect("orders.db")
    db = connection.cursor()

    max_order_id = db.execute(
        "SELECT MAX(order_id) FROM orders").fetchall()[0][0]
    if max_order_id is not None:
        order_id = max_order_id + 1
    else:
        order_id = 1

    for product in cart:
        db.execute("INSERT INTO products (name, price, units, order_id) VALUES (?, ?, ?, ?)",
                   (product['product_name'], product['product_price'], product['quantity'], order_id))
    connection.commit()

    db.execute("INSERT INTO orders (user_id, product_id, timestamp) VALUES (?, ?, ?)",
               (message.chat.id, order_id, datetime.now()))

    connection.commit()

    db.execute("INSERT INTO users (user_id, name, phone, address, order_id) VALUES (?, ?, ?, ?, ?)",
               (message.chat.id, client_data['name'], client_data['phone'], client_data['address'], order_id))
    connection.commit()

    db.close()
    connection.close()
    cart.clear()

    show_start_menu(message, "Great! Your pizza will be delivered soon to your address! The payment will be done on delivery.", bot)

@bot.message_handler(regexp='See a product photo')
def see_product_photo(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for product in products_list:
        markup.add(types.InlineKeyboardButton(
            product['pizza_name'] + " - R$ " + product['pizza_price']))
    sent_message = bot.send_message(
        message.chat.id, "Choose a pizza:", parse_mode="Markdown", reply_markup=markup)

    bot.register_next_step_handler(sent_message, show_product_photo)


def show_product_photo(message):
    product = message.text
    bot.send_photo(message.chat.id, open('product_images/pizza.jpg', 'rb'))
    show_start_menu(message, "What else do you want me to do?", bot)
    # In a perfect world, I would have different images for each product, so I would do this:
    #bot.send_photo(message.chat.id, open(f'product_images/{message.text.lower()}.jpg', 'rb'))
    # Accessing the image for that product, using the product's name.


# Shows all products in the cart.
@bot.message_handler(regexp='Show my cart')
def see_cart(message):
    outupt_message = ""
    if not len(cart) == 0:
        total_price = 0
        for product in cart:
            outupt_message += f"{product['product_name']} - *R${product['product_price']}* - Units: {product['quantity']}\n"
            total_price += product['product_price'] * product['quantity']

        outupt_message += f"*Total: R$ {round(total_price, 2)}*"

        bot.send_message(message.chat.id, outupt_message,
                         parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Your cart is empty!")


@bot.message_handler(regexp='Remove a product from cart')
def select_item_to_remove(message):
    if len(cart) > 0:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        for product in cart:
            markup.add(types.InlineKeyboardButton(
                f"{product['product_name']} - R${product['product_price']} - Units: {product['quantity']}\n"))
        sent_message = bot.send_message(
            message.chat.id, "Choose an item to remove:", reply_markup=markup)
        bot.register_next_step_handler(sent_message, remove_from_cart)
    else:
        bot.send_message(message.chat.id, "Your cart is empty!")


def remove_from_cart(message):
    input_name = clean_product_name(message.text)
    for product in cart:
        if product['product_name'] == input_name:
            cart.remove(product)
            break
    show_start_menu(
        message, "Item sucessfully removed!\nWhat else do you want me to do?", bot)


# Starts the bot.
bot.infinity_polling()
