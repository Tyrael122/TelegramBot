# PIZZA BUYER HELPER
#### Video Demo:  <https://youtu.be/QnLYzywKPQg>
#### Description: A Telegram Bot to help the client order pizzas, and a site that displays the orders made through the Bot.


#### Summary
A Telegram Bot called [SalesOrganizer](https://t.me/SalesOrganizerBot) is made available to a client that wants to buy a pizza, allowing him to see the menu, add products to his cart and buy them. When buying, the payment is intented to be done at delivery, or through any other method the product owner wants. This is because the payment processors are paid, making an in app feature harder to implement.

There's also a Flask Web App that shows the orders done by the bot. When an order is completed, it's saved to a database which the Flask web app access. The page reloads by    default every 10 seconds, so as to get the latest orders automatically.

#### Telegram Bot API
The Telegram Bot has been done in Python, using the [Telegram API](https://core.telegram.org/bots/api). To make the communication between the Telegram API and the software, it's recommended to use a framework, as stated in Telegram's website:

> You can think of a framework as software that handles all the low-level logic for you, including the API calls, and lets you focus on your bot-specific logic.

The framework I used is called [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI). When imported, it's module is called "telebot".

In the framework being used, to capture a command (commands in Telegram are anything that starts with a slash, e.g. "/start") we have to specify a handler. The syntax to do that is `r@BOT_VARIABLE.message_handler(commands=['COMMAND_NAME'])`. So in the program, if we want to define a handler when the user types "/start" we should write `r@bot.message_handler(commands=['start'])`. The function defined right after the handler will be called when the user types in the command. A `message` object will also be passed in to the defined function, which will be the message that trigged the event.

##### Sending messages
A function (`show_start_menu(message, text, bot)`) defined in "helpers.py" has been created to send a message with the text passed to it and display the startup buttons. It is necessary because it avoids having to set the buttons everytime they should be displayed.

The syntax to send a message to the user's chat is ` BOT_VARIABLE.send_message(CHAT_ID, MESSAGE)`. You need to pass a chat ID. The chat ID of the received message can be easily taken with `message.chat.id`. You can also specify a parse_mode, to use Markdown features, with `parse_mode="Markdown"`. There's the possibility of passing a markup, which is just a way to show interactive things other than just the message, using `reply_markup=MARKUP_VARIABLE` You should define a markup with `markup = types.ReplyKeyboardMarkup()`.

Quoting the Telegram Docs:
> Whenever your bot sends a message, it can pass along a special keyboard with predefined reply options. Regular keyboards are represented by `ReplyKeyboardMarkup` object.

You can than add buttons to that markup with `markup.add(BUTTON)`.

##### Sending images
You can also send images with the command `BOT_VARIABLE.send_photo(CHAT_ID, IMAGE_FILE)`, used to send a product photo. Ideally, there would be a different image for every pizza or product, but to save time, I put a sample photo that's shown for all pizzas.


##### Receiving messages
You can wait for new messages with `bot.register_next_step_handler(SENT_MESSAGE, FUNCTION)`. This will wait for new messages after the sent message and when it receives one, it'll call the function specified in the second argument. So you need to store the message you just sent in a variable as to pass it to this function, as in
```python
sent_message = bot.send_message(CHAT_ID, TEXT)
bot.register_next_step_handler(sent_message, FUNCTION)
```

To handle several messages at once, you may think that just calling the function several times in a row will suffice:

```python
sent_message = bot.send_message(CHAT_ID, SOME_TEXT)
bot.register_next_step_handler(sent_message, FUNCTION)

sent_message = bot.send_message(CHAT_ID, SOME_OTHER_TEXT)
bot.register_next_step_handler(sent_message, FUNCTION)
```
But this will not work. What `register_next_step_handler()` seems to be doing is telling the bot to wait for any incoming messages, but only after the end of the function. So if there's any code below the `register_next_step_handler()` function, it's execution will not be paused to wait for the message, as one would expect. The solution is to put the code you want to execute thereafter _inside_ the function called by `register_next_step_handler()`. The framework's documentation has an [example](https://github.com/eternnoir/pyTelegramBotAPI/blob/master/examples/step_example.py) that does exactly that.


In `register_next_step_handler()`, you can also pass arguments to be called when the defined function is called, as in `bot.register_next_step_handler(SENT_MESSAGE, FUNCTION, FUNCTION_ARG)`.


#### Flask Web App
The website is made in Python using Flask and Jinja templating. It has a simple design and is intented to show all the orders made through the Bot. It reloads the page every 10 seconds and queries a database file ("orders.db") which has the user and his order  data, along with the products ordered by him.
