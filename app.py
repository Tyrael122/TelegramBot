"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template, redirect, request
from TelegramBot.Utilities.database import connect_to_database

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.route('/')
def index():
    db, connection = connect_to_database()
    orders = db.execute(
        "SELECT order_id, timestamp FROM orders").fetchall()

    # Creates an empty list of users and appends to it a user for every order.
    users = []
    for order in orders:

        user = {} # The user's empty data.

        # Gets the user's data from the database.
        query = db.execute(
            "SELECT name, phone, address FROM users WHERE order_id = ?", (order["order_id"],)).fetchall()[0]

        # Add the user's data to the user's dictionary.
        for key in query.keys():
            user[key] = query[key]

        # Gets the products related to that order.
        query = db.execute(
            "SELECT name, price, units, product_id FROM products WHERE order_id = ?", (order["order_id"],)).fetchall()

        # If there are no longer any products related to that order, delete both the order and the user data.
        if len(query) == 0:
            db.execute("DELETE FROM orders WHERE order_id = ?",
                       (order["order_id"],))
            connection.commit()
            db.execute("DELETE FROM users WHERE order_id = ?",
                       (order["order_id"],))
            connection.commit()
            continue # Goes to the next order.

        products = [] # The empty list of products.
        for product in query:
            product_data = {} # A dictionary to append to the list of products.
            for key in product.keys(): # Stores the product info into the dictionary.
                product_data[key] = product[key]
            products.append(product_data)

        user["products"] = products # Adds the list of products to the user's dictionary.

        users.append(user) # Adds the user to the list of users.

    db.close()
    connection.close()
    return render_template("index.html", users=users)


@app.route('/done', methods=['POST'])
def order_completed():
    # Removes the order from the database when dismissed.
    db, connection = connect_to_database()
    
    db.execute("DELETE FROM products WHERE product_id = ?",
               (request.form.get('completed_order_id'),))
    connection.commit()

    db.close()
    connection.close()

    return redirect('/')


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
