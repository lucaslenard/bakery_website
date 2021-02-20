from flask import Flask, render_template
from database.connector import connect_to_database, execute_query
from database.data_handler import format_data

app = Flask(__name__)
db_connection = connect_to_database()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/all_products')
def load_products():
    # Load up all products form database
    # query = "SELECT * FROM items;"

    query = "SELECT items.id, items.product_name, items.price, items.stock_quantity, vendors.vendor_name " \
            "FROM items LEFT OUTER JOIN vendors ON items.vendor_id=vendors.id;"
    results = execute_query(db_connection, query)
    response = results.fetchall()

    # TODO: Set vendor name to in house if NULL
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
    items = {
        "bakery_101": "Beginner Baking 101",
        "bakery_301": "Advanced Baking 301"
    }
    return render_template('enrolled_classes.html', data=items)


@app.route('/shopping_cart')
def cart():
    items = {
        "donuts": "Donuts",
        "bread": "Bread",
        "hamburger_buns": "Hamburger Buns"
    }
    return render_template('shopping_cart.html', data=items)


@app.route('/previous_orders')
def orders():
    # Add in links to orders and utilize redirect with the order_id
    orders = {
        "00001": "Order 00001 on 1/12/21 for 3 items",
        "00002": "Order 00002 on 1/14/21 for 2 items"
    }
    return render_template('order_history.html', data=orders)


@app.route('/payment_information')
def payment_info():

    card_info = {
        "card_holder_name": "Lucas Test",
        "card_number": "123454321",
        "security_number": "270",
        "expiration_date": "2022-01-01"
    }
    return render_template('payment_info.html', data=card_info)


@app.route('/address_information')
def address_info():
    address_info = {
        "recipient_name": "Lucas Test",
        "street_address": "100 Test Ave.",
        "city": "Testing Village",
        "state": "Test Virginia",
        "zip": "00011"
    }
    return render_template('address_info.html', data=address_info)


@app.route('/edit_accounts')
def admin_edit_accounts():
    return render_template('edit_accounts.html')


@app.route('/edit_products')
def admin_edit_products():
    return render_template('edit_products.html')


@app.route('/edit_classes')
def admin_edit_classes():
    return render_template('edit_classes.html')


@app.route('/edit_orders')
def admin_edit_orders():
    return render_template('edit_orders.html')


@app.route('/edit_enrollments')
def admin_edit_enrollments():
    return render_template('edit_enrollments.html')
