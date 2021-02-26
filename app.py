from flask import Flask, render_template, redirect, request
from database.connector import connect_to_database, execute_query
from database.data_handler import format_data

app = Flask(__name__)

# TODO: Update to use the user_id from session
username = "admin"


@app.route('/')
def index():
    return render_template('index.html')


####################################################################################
#
# Login/Register page
#
####################################################################################


@app.route('/login_register')
def user_login_register():
    return render_template('login.html')


####################################################################################
#
# Saved Payment Information page
#
####################################################################################


@app.route('/payment_information')
def payment_info():
    query = f"SELECT * FROM payment_information WHERE user_id=(SELECT id from users WHERE username='{username}');"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["name", "card_number", "security_number", "expiration_date"])

    return render_template('payment_info.html', data=data)


@app.route('/edit_payment_information')
def edit_payment_info():
    query = "SELECT id, user_id, name, card_number, security_code, expiration_date FROM payment_information;"
    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["name", "card_number", "security_code", "expiration_date"])

    return render_template('payment_info.html', data=data)


@app.route('/add_payment_information', methods=["POST"])
def add_payment_info():
    name = request.form.get("customer_name")
    card_number = request.form.get("card_number")
    security_number = request.form.get("security_number")
    expiration_date = request.form.get("expiration_date")

    query = f"INSERT INTO payment_information (user_id, name, card_number, security_number, expiration_date) " \
            f"VALUES ((SELECT id from users WHERE username='{username}'), '{name}', '{card_number}', '{security_number}', '{expiration_date}');"

    execute_query(query)

    return redirect(request.referrer)


####################################################################################
#
# Saved Address Information page
#
####################################################################################


@app.route('/address_information')
def address_info():
    query = f"SELECT * FROM addresses WHERE user_id=(SELECT id from users WHERE username='{username}');"
    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["street_address", "secondary_street_address", "city", "state", "zip_code"])

    return render_template('address_info.html', data=data)


@app.route('/edit_address_information')
def edit_address_info():
    query = "SELECT id, user_id, street_address, secondary_street_address, city, state, zip_code;"
    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["street_address", "secondary_street_address", "city", "state", "zip_code"])

    return render_template('address_info.html', data=data)


@app.route('/add_address_information', methods=["POST"])
def add_address_info():
    street_address = request.form.get("street_address_1")
    secondary_street_address = request.form.get("street_address_2")
    city = request.form.get("city")
    state = request.form.get("state")
    zip_code = request.form.get("zip_code")

    query = f"INSERT INTO addresses (user_id, street_address, secondary_street_address, city, state, zip_code) " \
            f"VALUES ((SELECT id from users WHERE username='{username}'), '{street_address}', '{secondary_street_address}', '{city}', '{state}', '{zip_code}');"

    execute_query(query)

    return redirect(request.referrer)


####################################################################################
#
# Previous Orders page
#
####################################################################################


@app.route('/previous_orders')
def orders():
    query = f"SELECT * FROM orders WHERE user_id=(SELECT id from users WHERE username='{username}');"

    results = execute_query(query)
    response = results.fetchall()

    # TODO: Fix the format_data to replace boolean with checkbox somehow?
    data = format_data(response, ["id", "date", "total_cost", "fulfilled"])
    # TODO: Add in links to orders and utilize redirect with the order_id

    return render_template('order_history.html', data=data)


####################################################################################
#
# All Bakery Products page
#
####################################################################################


@app.route('/all_products')
def load_products():
    query = "SELECT items.id, items.product_name, items.price, items.stock_quantity, vendors.vendor_name " \
            "FROM items LEFT OUTER JOIN vendors ON items.vendor_id=vendors.id;"
    results = execute_query(query)
    response = results.fetchall()

    # TODO: Set vendor name to "Homemade" if NULL
    data = format_data(response, ["product_name", "vendor_name", "price", "stock_quantity"])

    return render_template('products.html', data=data)


####################################################################################
#
# Shopping Cart page
#
####################################################################################


@app.route('/shopping_cart')
def cart():
    # TODO: Need to update to utilize session to pull ids
    items = {
        "donuts": "Donuts",
        "bread": "Bread",
        "hamburger_buns": "Hamburger Buns"
    }
    return render_template('shopping_cart.html', data=items)


####################################################################################
#
# All Classes page
#
####################################################################################


@app.route('/classes')
def load_classes():
    query = "SELECT id, class_name, date, instructor, available_seats, price FROM classes;"
    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "date", "instructor", "available_seats", "price"])

    return render_template('classes.html', data=data)


@app.route('/enroll_in_class', methods=["POST"])
def enroll_class():
    class_id = request.form["enroll"]
    query = f"INSERT INTO enrollments (user_id, class_id, course_result) " \
            f"VALUES ((SELECT id from users WHERE username='{username}'), {int(class_id)}, 'Not Taken');"

    execute_query(query)

    return redirect(request.referrer)


####################################################################################
#
# Enrolled Classes page
#
####################################################################################


@app.route('/class_enrollments')
def enrolled_classes():
    query = f"SELECT enrollments.id, enrollments.course_result, classes.class_name, classes.date, classes.instructor " \
            f"FROM enrollments INNER JOIN classes ON enrollments.class_id=classes.id " \
            f"WHERE enrollments.user_id=(SELECT id from users WHERE username='{username}');"
    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "date", "instructor", "course_result"])

    return render_template('enrolled_classes.html', data=data)


####################################################################################
#
# Edit Accounts page
#
####################################################################################


@app.route('/edit_accounts')
def admin_edit_accounts():
    query = "SELECT * FROM users;"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["first_name", "last_name", "username", "password", "email_address", "admin"])

    headers = ["First Name", "Last Name", "Username", "Password", "Email", "Admin", "Action(s)"]
    button = ["edit", "delete", "add"]
    title = "Admin Tools - Accounts"
    page = "edit_accounts"
    add = {"first_name": "text", "last_name": "text", "username": "text", "password": "text", "email": "text",
           "admin": "checkbox"}

    return render_template('tables.html', data=data, headers=headers, button=button, title=title, page=page, add=add)


@app.route('/add_edit_accounts', methods=["POST"])
def add_user_account():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    user_name = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    checkbox = request.form.get("admin")

    if checkbox is not None:
        admin = True
    else:
        admin = False

    # TODO: Check that username isn't already in use

    query = f"INSERT INTO users (first_name, last_name, username, password, email_address, admin) " \
            f"VALUES ('{first_name}', '{last_name}', '{user_name}', '{password}', '{email}', {admin});"

    execute_query(query)

    return redirect(request.referrer)


# Delete for Edit Accounts
@app.route('/delete_edit_accounts', methods=["POST"])
def delete_account():
    item_id = request.form.get("remove_item")

    query = f"DELETE FROM users WHERE id={int(item_id)};"

    execute_query(query)

    return redirect(request.referrer)


####################################################################################
#
# Edit Products page
#
####################################################################################


@app.route('/edit_products')
def admin_edit_products():
    query = "SELECT items.id, items.product_name, items.price, items.stock_quantity, vendors.vendor_name " \
            "FROM items LEFT OUTER JOIN vendors ON items.vendor_id=vendors.id;"
    results = execute_query(query)
    response = results.fetchall()

    # TODO: Set vendor name to "Homemade" if NULL
    data = format_data(response, ["product_name", "vendor_name", "price", "stock_quantity"])

    headers = ["Item Name", "Vendor", "Cost", "Quantity Available", "Action(s)"]
    button = ["edit", "delete", "add"]
    title = "Admin Tools - Products"
    page = "edit_products"
    add = {"item_name": "text", "vendor": "text", "price": "number", "quantity": "number"}

    return render_template('tables.html', data=data, headers=headers, button=button, title=title, page=page, add=add)


# Add for Edit Products
@app.route('/add_edit_products', methods=["POST"])
def add_new_product():
    item_name = request.form.get("item_name")
    vendor = request.form.get("vendor") or None
    cost = request.form.get("price")
    quantity = request.form.get("quantity")

    if vendor is None:
        query = f"INSERT INTO items (product_name, price, stock_quantity) " \
                f"VALUES ('{item_name}', {int(cost)}, {int(quantity)});"

    else:
        query = f"SELECT id from vendors where vendor_name='{vendor}';"
        results = execute_query(query)
        vendor_id = results.fetchall()

        if not vendor_id:
            query = f"INSERT INTO vendors (vendor_name) VALUES ('{vendor}');"
            execute_query(query)
            query = f"SELECT id from vendors where vendor_name='{vendor}';"
            results = execute_query(query)
            vendor_id = results.fetchall()

        vendor_id = vendor_id[0]["id"]
        query = f"INSERT INTO items (vendor_id, product_name, price, stock_quantity) " \
                f"VALUES ({int(vendor_id)}, '{item_name}', {int(cost)}, {int(quantity)});"

    execute_query(query)

    return redirect(request.referrer)


# Delete for Edit Products
@app.route('/delete_edit_products', methods=["POST"])
def delete_product():
    print("In the function")
    item_id = request.form.get("remove_item")
    print(item_id)

    query = f"DELETE FROM items WHERE id={int(item_id)};"

    execute_query(query)

    return redirect(request.referrer)


####################################################################################
#
# Edit Classes page
#
####################################################################################


@app.route('/edit_classes')
def admin_edit_classes():
    query = "SELECT id, class_name, date, instructor, available_seats, price FROM classes;"
    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "date", "instructor", "available_seats", "price"])

    headers = ["Class Name", "Class Date", "Instructor", "Available Seats", "Price", "Action(s)"]
    button = ["edit", "delete", "add"]
    title = "Admin Tools - Classes"
    page = "edit_classes"
    add = {"class_name": "text", "date": "date", "instructor": "text", "available_seats": "number", "price": "number"}

    return render_template('tables.html', data=data, headers=headers, button=button, title=title, page=page, add=add)


####################################################################################
#
# Edit Orders page
#
####################################################################################


@app.route('/edit_orders')
def admin_edit_orders():
    query = "SELECT orders.id, orders.date, orders.fulfilled, orders.total_cost, users.first_name, users.last_name " \
            "FROM orders INNER JOIN users ON orders.user_id=users.id;"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["id", "first_name", "last_name", "date", "total_cost", "fulfilled"])

    headers = ["Order Number", "First Name", "Last Name", "Order Date", "Total Cost", "Fulfilled", "Action(s)"]
    button = ["view", "edit", "delete"]
    title = "Admin Tools - Orders"
    page = "edit_orders"

    return render_template('tables.html', data=data, headers=headers, button=button, title=title, page=page)


####################################################################################
#
# Edit Enrollments page
#
####################################################################################


@app.route('/edit_enrollments')
def admin_edit_enrollments():
    query = f"SELECT enrollments.id, enrollments.course_result, classes.class_name, classes.date, classes.instructor, " \
            f"users.first_name, users.last_name FROM enrollments " \
            f"INNER JOIN classes ON enrollments.class_id=classes.id " \
            f"INNER JOIN users ON enrollments.user_id=users.id;"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "first_name", "last_name", "date", "instructor", "course_result"])
    headers = ["Class Name", "First Name", "Last Name", "Class Date", "Instructor", "Course Result", "Action(s)"]
    button = ["edit", "delete"]
    title = "Admin Tools - Enrollments"
    page = "edit_enrollments"

    return render_template('tables.html', data=data, headers=headers, button=button, title=title, page=page)
