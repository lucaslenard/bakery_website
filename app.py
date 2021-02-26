from flask import Flask, render_template, redirect, request, session
from database.connector import execute_query
from database.data_handler import format_data

app = Flask(__name__)
app.secret_key = "secret_key_string"


@app.route('/')
def index():
    return render_template('index.html')


####################################################################################
#
# Login/Register pages
#
####################################################################################
@app.route('/login')
def user_login():
    return render_template('login.html')


@app.route('/register')
def user_register():
    return render_template('register.html')


@app.route('/logout')
def user_logout():
    session["username"] = ""
    session.permanent = False
    session['logged_in'] = False
    return render_template('index.html')


@app.route('/login_user', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Determine if the user exists
    query = f"SELECT username, password FROM users where username='{username}';"

    results = execute_query(query)
    response = results.fetchall()

    # Verify a password match to create session
    if "password" in response[0] and password == response[0]["password"]:
        session.permanent = True
        session['logged_in'] = True
        session["username"] = username

        return render_template('index.html')

    # Add in an error message that username or password was incorrect

    return render_template('index.html')


@app.route('/register_user', methods=['POST'])
def register():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    # Verify username isn't already in use
    query = f"SELECT username FROM users where username='{username}';"
    results = execute_query(query)
    response = results.fetchall()

    if len(response):
        return render_template('index.html')
    else:
        admin = False
        query = f"INSERT INTO users (first_name, last_name, username, password, email_address, admin) VALUES" \
                f"('{first_name}', '{last_name}', '{username}', '{password}', '{email}', {admin});"

        execute_query(query)

        session.permanent = True
        session['logged_in'] = True
        session["username"] = username

        return render_template('index.html')


####################################################################################
#
# Saved Payment Information page
#
####################################################################################


@app.route('/payment_information')
def payment_info():
    username = session["username"]
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
    username = session["username"]
    name = request.form.get("customer_name")
    card_number = request.form.get("card_number")
    security_number = request.form.get("security_number")
    expiration_date = request.form.get("expiration_date")

    query = f"INSERT INTO payment_information (user_id, name, card_number, security_number, expiration_date) " \
            f"VALUES ((SELECT id from users WHERE username='{username}'), '{name}', {int(card_number)}, {int(security_number)}, '{expiration_date}');"

    execute_query(query)

    return redirect(request.referrer)


####################################################################################
#
# Saved Address Information page
#
####################################################################################


@app.route('/address_information')
def address_info():
    username = session["username"]
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
    username = session["username"]
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
    username = session["username"]
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
    username = session["username"]
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
    username = session["username"]
    query = f"SELECT enrollments.id, enrollments.course_result, classes.class_name, classes.date, classes.instructor " \
            f"FROM enrollments INNER JOIN classes ON enrollments.class_id=classes.id " \
            f"WHERE enrollments.user_id=(SELECT id from users WHERE username='{username}');"
    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "date", "instructor", "course_result"])

    return render_template('enrolled_classes.html', data=data)


@app.route('/drop_class', methods=["POST"])
def drop_enrolled_class():
    class_id = request.form.get("drop_class")
    print(class_id)
    query = f"DELETE FROM enrollments WHERE id={int(class_id)}"

    execute_query(query)

    return redirect(request.referrer)


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
    user_id = request.form.get("remove_item")

    # In order to prevent null data from existing we need to delete all associated objects to the user
    query = f"DELETE FROM addresses where user_id={int(user_id)};"
    execute_query(query)

    query = f"DELETE FROM payment_information where user_id={int(user_id)};"
    execute_query(query)

    query = f"DELETE FROM enrollments where user_id={int(user_id)};"
    execute_query(query)

    query = f"SELECT id FROM orders where user_id={int(user_id)};"
    results = execute_query(query)
    response = results.fetchall()

    for order_id in response:
        query = f"DELETE FROM order_items where order_id={int(order_id['id'])};"
        execute_query(query)

        query = f"DELETE FROM orders where id={int(order_id['id'])};"
        execute_query(query)

    query = f"DELETE FROM users WHERE id={int(user_id)};"
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
    item_id = request.form.get("remove_item")

    # Need to safely delete all associated data - specifically any order_items that contain item
    query = f"DELETE FROM order_items where item_id={int(item_id)};"
    execute_query(query)

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


@app.route('/add_edit_classes', methods=["POST"])
def add_class():
    class_name = request.form.get("class_name")
    date = request.form.get("date")
    instructor = request.form.get("instructor")
    seats = request.form.get("available_seats")
    price = request.form.get("price")

    query = f"INSERT INTO classes (class_name, date, instructor, available_seats, price) " \
            f"VALUES ('{class_name}', '{date}', '{instructor}', {int(seats)}, {int(price)});"

    execute_query(query)

    return redirect(request.referrer)


# Delete for Edit Classes
@app.route('/delete_edit_classes', methods=["POST"])
def delete_class():
    class_id = request.form.get("remove_item")

    # Need to safely delete all associated data - specifically any enrollments that contain this class
    query = f"DELETE FROM enrollments where class_id={int(class_id)};"
    execute_query(query)

    query = f"DELETE FROM classes WHERE id={int(class_id)};"
    execute_query(query)

    return redirect(request.referrer)


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


# Delete for Edit Orders
@app.route('/delete_edit_orders', methods=["POST"])
def delete_order():
    order_id = request.form.get("remove_item")

    # Need to safely delete all associated data - specifically any order_items that contain this order
    query = f"DELETE FROM order_items where order_id={int(order_id)};"
    execute_query(query)

    query = f"DELETE FROM orders WHERE id={int(order_id)};"
    execute_query(query)

    return redirect(request.referrer)


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


# Delete for Edit Enrollments
@app.route('/delete_edit_enrollments', methods=["POST"])
def delete_enrollment():
    enroll_id = request.form.get("remove_item")

    query = f"DELETE FROM enrollments WHERE id={int(enroll_id)};"
    execute_query(query)

    return redirect(request.referrer)
