from telebot import types
from datetime import datetime
from Utilities.database import connect_to_database, fetch_cart_id
from Utilities.helpers import show_start_menu
from globals_vars import bot


def process_client_name(message, client_data):
    client_data['name'] = message.text
    sent_message = bot.send_message(
        message.chat.id, "What's your shipping address?")
    bot.register_next_step_handler(
        sent_message, process_client_address, client_data)


def process_client_address(message, client_data):
    client_data['address'] = message.text

    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    markup.add(types.KeyboardButton(
        "Share your phone with us", request_contact=True))

    sent_message = bot.send_message(
        message.chat.id, "Would you give us access to your phone number, so as to call you if necessary? You can also write your custom phone number if you want.", reply_markup=markup)
    bot.register_next_step_handler(
        sent_message, process_client_phone, client_data)


def process_client_phone(message, client_data):
    # If the user didn't share the phone number, the message will be a string.
    if message.contact is None:
        client_data['phone'] = message.text
    else:
        phone_number = message.contact.phone_number
        # Brazil's international code. Not needed if in Brazil.
        phone_number = phone_number.strip('55')
        client_data['phone'] = phone_number

    # Adding the order and clearing the cart
    add_to_database(message, client_data)

    show_start_menu(
        message, "Great! Your pizza will be delivered soon to your address! The payment will be done on delivery.")


def add_to_database(message, client_data):
    db, connection = connect_to_database()

    # Inserting the order
    db.execute("INSERT INTO orders (user_id, timestamp) VALUES (?, ?)",
               (message.chat.id, datetime.now()))
    connection.commit()

    order_id = db.execute(
        "SELECT MAX(order_id) FROM orders").fetchall()[0][0]

    # Updating the products with the order ID
    cart_id = fetch_cart_id(message)
    db.execute("UPDATE products SET order_id = ? WHERE cart_id = ?",
               (order_id, cart_id))
    connection.commit()

    # Inserting the user data
    db.execute("INSERT INTO users (user_id, name, phone, address, order_id) VALUES (?, ?, ?, ?, ?)",
               (message.chat.id, client_data['name'], client_data['phone'], client_data['address'], order_id))
    connection.commit()

    # Clearing the cart
    db.execute(
        "UPDATE products SET cart_id = NULL WHERE order_id = ?", (order_id,))
    connection.commit()

    db.close()
    connection.close()
