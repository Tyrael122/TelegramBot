# This file contains the global variables used in the project.

import telebot
import os
from Utilities.helpers import load_products

# Creates the bot based on the bot token.
bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_KEY'))

# Loads the list of products based on the JSON file.
products_list = load_products()
