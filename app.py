from flask import Flask, render_template
from database.connector import connect_to_database, execute_query
from database.data_handler import format_data

app = Flask(__name__)
db_connection = connect_to_database()

# TODO: Update to use the user_id from session
username = "admin"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/all_products')
def load_products():

    query = "SELECT items.id, items.product_name, items.price, items.stock_quantity, vendors.vendor_name " \
            "FROM items LEFT OUTER JOIN vendors ON items.vendor_id=vendors.id;"
    results = execute_query(db_connection, query)
    response = results.fetchall()

    # TODO: Set vendor name to "Homemade" if NULL
    data = format_data(response, ["product_name", "vendor_name", "price", "stock_quantity"])

    return render_template('products.html', data=data)


@app.route('/classes')
def load_classes():
    query = "SELECT id, class_name, date, instructor, available_seats, price FROM classes;"
    results = execute_query(db_connection, query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "date", "instructor", "available_seats", "price"])

    return render_template('classes.html', data=data)


@app.route('/login_register')
def user_login_register():
    return render_template('login.html')


@app.route('/class_enrollments')
def enrolled_classes():

    query = f"SELECT enrollments.id, enrollments.course_result, classes.class_name, classes.date, classes.instructor " \
            f"FROM enrollments INNER JOIN classes ON enrollments.class_id=classes.id " \
            f"WHERE enrollments.user_id=(SELECT id from users WHERE username='{username}');"
    results = execute_query(db_connection, query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "date", "instructor", "course_result"])

    return render_template('enrolled_classes.html', data=data)


@app.route('/shopping_cart')
def cart():
    # TODO: Need to update to utilize session to pull ids
    items = {
        "donuts": "Donuts",
        "bread": "Bread",
        "hamburger_buns": "Hamburger Buns"
    }
    return render_template('shopping_cart.html', data=items)


@app.route('/previous_orders')
def orders():

    query = f"SELECT * FROM orders WHERE user_id=(SELECT id from users WHERE username='{username}');"

    results = execute_query(db_connection, query)
    response = results.fetchall()

    # TODO: Fix the format_data to replace boolean with checkbox somehow?
    data = format_data(response, ["id", "date", "total_cost", "fulfilled"])
    # TODO: Add in links to orders and utilize redirect with the order_id

    return render_template('order_history.html', data=data)


@app.route('/payment_information')
def payment_info():
    query = f"SELECT * FROM payment_information WHERE user_id=(SELECT id from users WHERE username='{username}');"

    results = execute_query(db_connection, query)
    response = results.fetchall()

    data = format_data(response, ["name", "card_number", "security_number", "expiration_date"])

    return render_template('payment_info.html', data=data)


@app.route('/address_information')
def address_info():
    query = f"SELECT * FROM addresses WHERE user_id=(SELECT id from users WHERE username='{username}');"
    results = execute_query(db_connection, query)
    response = results.fetchall()

    data = format_data(response, ["street_address", "secondary_street_address", "city", "state", "zip_code"])

    return render_template('address_info.html', data=data)


@app.route('/edit_accounts')
def admin_edit_accounts():
    query = "SELECT * FROM users;"

    results = execute_query(db_connection, query)
    response = results.fetchall()

    data = format_data(response, ["first_name", "last_name", "username", "password", "email_address", "admin"])

    return render_template('edit_accounts.html', data=data)


@app.route('/edit_products')
def admin_edit_products():
    query = "SELECT items.id, items.product_name, items.price, items.stock_quantity, vendors.vendor_name " \
            "FROM items LEFT OUTER JOIN vendors ON items.vendor_id=vendors.id;"
    results = execute_query(db_connection, query)
    response = results.fetchall()

    # TODO: Set vendor name to "Homemade" if NULL
    data = format_data(response, ["product_name", "vendor_name", "price", "stock_quantity"])

    return render_template('edit_products.html', data=data)


@app.route('/edit_classes')
def admin_edit_classes():

    query = "SELECT id, class_name, date, instructor, available_seats, price FROM classes;"
    results = execute_query(db_connection, query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "date", "instructor", "available_seats", "price"])

    return render_template('edit_classes.html', data=data)


@app.route('/edit_orders')
def admin_edit_orders():
    query = "SELECT orders.id, orders.date, orders.fulfilled, orders.total_cost, users.first_name, users.last_name " \
            "FROM orders INNER JOIN users ON orders.user_id=users.id;"

    results = execute_query(db_connection, query)
    response = results.fetchall()

    data = format_data(response, ["id", "first_name", "last_name", "date", "total_cost", "fulfilled"])

    return render_template('edit_orders.html', data=data)


@app.route('/edit_enrollments')
def admin_edit_enrollments():

    query = f"SELECT enrollments.id, enrollments.course_result, classes.class_name, classes.date, classes.instructor, " \
            f"users.first_name, users.last_name FROM enrollments " \
            f"INNER JOIN classes ON enrollments.class_id=classes.id " \
            f"INNER JOIN users ON enrollments.user_id=users.id;"

    results = execute_query(db_connection, query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "first_name", "last_name", "date", "instructor", "course_result"])

    return render_template('edit_enrollments.html', data=data)
