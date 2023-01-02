from Utilities.helpers import show_start_menu
from globals_vars import bot


def show_product_photo(message):
    product = message.text
    bot.send_photo(message.chat.id, open('product_images/pizza.jpg', 'rb'))
    show_start_menu(message, "What else do you want me to do?", bot)
    # In a perfect world, I would have different images for each product, so I would do this:
    #bot.send_photo(message.chat.id, open(f'product_images/{message.text.lower()}.jpg', 'rb'))
    # Accessing the image for that product, using the product's name.
