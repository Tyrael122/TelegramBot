"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template, redirect, request
import sqlite3

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app



@app.route('/')
def index():
    """Renders a sample page."""
    connection = sqlite3.connect("orders.db")
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    orders = db.execute("SELECT order_id, product_id, timestamp FROM orders").fetchall()

    users = []
    for order in orders:

        user = {}

        query = db.execute("SELECT name, phone, address FROM users WHERE order_id = ?", (order["order_id"],)).fetchall()[0]

        for key in query.keys():
            print(query[key])
            user[key] = query[key]
            

        query = db.execute("SELECT name, price, units, product_id FROM products WHERE order_id = ?", (order["product_id"],)).fetchall()

        if len(query) == 0:
            db.execute("DELETE FROM orders WHERE order_id = ?", (order["order_id"],))
            connection.commit()
            db.execute("DELETE FROM users WHERE order_id = ?", (order["order_id"],))
            connection.commit()
            continue

        products = []
        for product in query:
            product_data = {}
            for key in product.keys():
                product_data[key] = product[key]
            products.append(product_data)
        
        user["products"] = products

        users.append(user)

       
    db.close()
    connection.close()
    return render_template("index.html", users=users)

@app.route('/done', methods=['POST'])
def order_completed():
    # Removes the order from the database.
    connection = sqlite3.connect("orders.db")
    db = connection.cursor()

    db.execute("DELETE FROM products WHERE product_id = ?", (request.form.get('completed_order_id'),))
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
