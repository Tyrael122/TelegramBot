from Utilities.database import fetch_cart, insert_into_cart, delete_from_cart
from Utilities.helpers import show_start_menu, clean_product_name
from globals_vars import products_list, bot

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

            insert_into_cart(message, name, price, units)

            products = fetch_cart(message)

            total_price, total_units = 0, 0
            for cart_product in products:
                total_price += cart_product['price'] * cart_product['units']
                total_units += cart_product['units']

            bot.send_message(
                message.chat.id, f"Added {name} to the cart!\nCart Size: {total_units}\nCart total price: R${round(total_price, 2)}")

            output_message = "What else do you want me to do?"
        else:
            output_message = "Units must be greater than 0!"
    else:
        output_message = "That's not a valid number!"
    show_start_menu(message, output_message)

def remove_from_cart(message):
    input_name = clean_product_name(message.text)
    cart = fetch_cart(message)
    for product in cart:
        if product['name'] == input_name:
            delete_from_cart(product['product_id'])
            break
    show_start_menu(
        message, "Item sucessfully removed!\nWhat else do you want me to do?")
