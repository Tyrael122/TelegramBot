# This file contains the database functions used in the project.
from sqlite3 import connect, Row


def connect_to_database():
    connection = connect("orders.db")
    connection.row_factory = Row
    db = connection.cursor()

    return db, connection


def fetch_cart_id(message):
    db, connection = connect_to_database()

    cart_id = db.execute("SELECT cart_id FROM carts WHERE user_id = ?",
                         (message.chat.id,)).fetchall()[0][0]

    db.close()
    connection.close()

    return cart_id


def fetch_cart(message):
    db, connection = connect_to_database()

    products = db.execute(
        "SELECT price, units, name, product_id FROM products WHERE cart_id = (SELECT cart_id FROM carts WHERE user_id = ?)", (message.chat.id,)).fetchall()

    db.close()
    connection.close()

    return products


def insert_into_cart(message, name, price, units):
    db, connection = connect_to_database()

    # Fetches the cart id of the user
    cart_id = fetch_cart_id(message)

    # Checks if the user has a cart. If not, creates one.
    if cart_id == None:
        db.execute("INSERT INTO carts (user_id) VALUES (?)",
                   (message.chat.id,))
        connection.commit()
        cart_id = fetch_cart_id(message)

    db.execute("INSERT INTO products (name, price, units, cart_id) VALUES (?, ?, ?, ?)",
               (name, price, units, cart_id))
    connection.commit()

    db.close()
    connection.close()


def delete_from_cart(product_id):
    db, connection = connect_to_database()

    db.execute("DELETE FROM products WHERE product_id = ?",
               (product_id,))
    connection.commit()

    db.close()
    connection.close()
