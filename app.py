from flask import Flask, render_template
from database.connector import connect_to_database, execute_query


app = Flask(__name__)
db_connection = connect_to_database()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/all_products')
def load_products():
    # Load up all products form database
    query = "SELECT * FROM items;"
    results = execute_query(db_connection, query)
    items = results.fetchall()
    print(items)


    items = {
        "donuts": "Donuts",
        "bread": "Bread",
        "hamburger_buns": "Hamburger Buns",
        "kringle": "Racine Kringle",
        "hot_dog_buns": "Hot Dog Buns"
    }

    return render_template('products.html', data=items)


@app.route('/classes')
def load_classes():
    items = {
        "bakery_101": "Beginner Baking 101",
        "bakery_102": "Beginner Baking 102",
        "bakery_201": "Intermediate Baking 201",
        "bakery_301": "Advanced Baking 301"
    }
    return render_template('classes.html', data=items)


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
