import logging
from datetime import datetime
from flask import Flask, render_template, redirect, request, session, url_for
from database.connector import execute_query
from database.data_handler import format_data

app = Flask(__name__)
app.secret_key = "secret_key_string"

logging.basicConfig(filename='bakery.log',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(process)d - %(message)s',
                    level=logging.INFO)

log = logging.getLogger(__name__)


@app.route('/')
def index():
    return render_template('index.html')


####################################################################################
#
# Login/Register/Logout pages
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
        session["cart"] = {}

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
        session["cart"] = {}

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


@app.route('/edit_payment_info', methods=['POST'])
def edit_payment_info():
    query = "SELECT id, user_id, name, card_number, security_number, expiration_date FROM payment_information;"
    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["name", "card_number", "security_number", "expiration_date"])

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


@app.route('/delete_payment_info', methods=["POST"])
def delete_payment_info():
    payment_id = request.form.get("remove_payment")

    query = f"DELETE FROM payment_information where id={int(payment_id)};"
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


@app.route('/delete_address_info', methods=["POST"])
def delete_address_info():
    address_id = request.form.get("remove_address")

    query = f"DELETE FROM addresses where id={int(address_id)};"
    execute_query(query)

    return redirect(request.referrer)

####################################################################################
#
# Previous Orders page and sub-page Order Items
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

    return render_template('order_history.html', data=data)


@app.route('/individual_order_items', methods=["POST"])
def ind_items():
    order_id = request.form.get("view_item")

    query = f"SELECT order_items.id, order_items.quantity, items.product_name, items.price FROM order_items " \
            f"LEFT OUTER JOIN items ON order_items.item_id=items.id " \
            f"WHERE order_items.order_id={int(order_id)};"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["product_name", "price", "quantity"])

    return render_template('view_order_items.html', data=data)


####################################################################################
#
# All Bakery Products page
#
####################################################################################


@app.route('/all_products', methods=["GET", "POST"])
def load_products():
    # grabbing the value from whatever the button name is for filter

    # Perform an if statement similar to the one in admin_edit_products where it checks if value is None. If it is none
    # then the page wasn't called by filter button and we return the select query that isn't filtering anything

    # If the button value is not None then we know that a call was made to filter so we need to grab the filter value
    # from the form and perform a query using the LIKE mysql verb

    # Then in either case we can format data and render products.html

    query = "SELECT items.id, items.product_name, items.price, items.stock_quantity, vendors.vendor_name " \
            "FROM items LEFT OUTER JOIN vendors ON items.vendor_id=vendors.id;"
    results = execute_query(query)
    response = results.fetchall()

    # TODO: Set vendor name to "Homemade" if NULL
    data = format_data(response, ["product_name", "vendor_name", "price", "stock_quantity"])

    return render_template('products.html', data=data)


@app.route('/add_cart', methods=["POST"])
def add_to_cart():
    item_id = request.form.get("add_to_cart")
    quantity = request.form.get(f"input_quantity {item_id}")

    # Check to see if item was previously added to cart
    if item_id in session["cart"]:
        session["cart"][item_id] += int(quantity)

    else:
        session["cart"].update({item_id: int(quantity)})

    print(session["cart"])
    return redirect(request.referrer)

####################################################################################
#
# Shopping Cart page
#
####################################################################################


@app.route('/shopping_cart')
def shop_cart():

    cart = {}

    for key, value in session["cart"].items():
        query = f"SELECT items.id, items.product_name, items.price, vendors.vendor_name " \
                f"FROM items LEFT OUTER JOIN vendors ON items.vendor_id=vendors.id WHERE items.id={int(key)};"
        results = execute_query(query)
        response = results.fetchall()

        data = format_data(response, ["product_name", "vendor_name", "price"])

        data[key].update({"quantity": str(value)})
        print(data)
        cart.update(data)

    print(cart)

    return render_template('shopping_cart.html', data=cart)


@app.route('/checkout', methods=["POST"])
def check_out():

    print(request.form)

    item_id = request.form.get("remove_item")

    if item_id is None:
        parameters = request.form.to_dict()
        del parameters["checkout"]

        if len(parameters):

            total_price = 0

            for key, value in parameters.items():
                print(key)
                print(value)

                # Get the item price to add to total price
                query = f"SELECT price FROM items WHERE id={int(key)};"
                results = execute_query(query)
                response = results.fetchall()

                total_price += (response[0]["price"] * int(value))

            # Create order
            username = session["username"]
            fulfilled = False
            date = datetime.today().strftime('%Y-%m-%d')
            query = f"INSERT INTO orders (user_id, date, fulfilled, total_cost) VALUES " \
                    f"((SELECT id from users WHERE username='{username}'), DATE '{date}', {fulfilled}, {total_price});"

            execute_query(query)

            # Get most recent order_id for use in creating the individual order_items entries
            query = f"SELECT MAX(id) FROM orders WHERE user_id=(SELECT id from users WHERE username='{username}');"
            results = execute_query(query)
            response = results.fetchall()
            order_id = response[0]["MAX(id)"]
            print(response)

            for key, value in parameters.items():
                query = f"INSERT INTO order_items (order_id, item_id, quantity) VALUES " \
                        f"({order_id}, {int(key)}, {int(value)});"

                execute_query(query)

            # Empty the session shopping cart
            session["cart"] = {}

            return redirect(url_for("orders"))

        else:
            return redirect(url_for("shop_cart"))

    else:
        remove_item(item_id)
        return redirect(url_for("shop_cart"))


@app.route('/remove_item', methods=["POST"])
def remove_item(item_id):

    if item_id is None:
        check_out(request.form)

    del session["cart"][item_id]

    return redirect(url_for("shop_cart"))

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


# Edit for Edit Accounts
@app.route('/edit_edit_accounts', methods=["POST"])
def edit_account_page():
    user_id = request.form.get("edit_item")

    query = f"SELECT id, first_name, last_name, username, password, email_address, admin FROM users WHERE id={int(user_id)};"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["first_name", "last_name", "username", "password", "email_address", "admin"])
    headers = ["First Name", "Last Name", "Username", "Password", "Email", "Admin", "Action(s)"]
    page = "edit_accounts"
    field_order = {"text", "text", "text", "text", "text", "checkbox"}

    return render_template('edit_row.html', data=data, headers=headers, page=page, field_order=field_order)


# Update for Edit Accounts
@app.route('/post_edit_accounts', methods=["POST"])
def post_edit_account_page():
    user_id = request.form.get("save_item")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email_address")
    checkbox = request.form.get("admin")

    if checkbox is not None:
        admin = True
    else:
        admin = False

    if user_id is None:
        return redirect(url_for("admin_edit_accounts"))

    query = f"UPDATE users " \
            f"SET first_name='{first_name}', last_name='{last_name}', username='{username}', " \
            f"password='{password}', email_address='{email}', admin={admin}" \
            f" WHERE id={int(user_id)};"
    execute_query(query)

    return redirect(url_for("admin_edit_accounts"))


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


# Edit for Edit Products
@app.route('/edit_edit_products', methods=["POST"])
def edit_products_page():
    product_id = request.form.get("edit_item")

    query = f"SELECT items.id, items.product_name, items.price, items.stock_quantity, vendors.vendor_name " \
            f"FROM items LEFT OUTER JOIN vendors ON items.vendor_id=vendors.id WHERE items.id={int(product_id)};"
    results = execute_query(query)
    response = results.fetchall()
    print(response)

    data = format_data(response, ["product_name", "vendor_name", "price", "stock_quantity"])
    headers = ["Product Name", "Vendor Name", "Price", "Quantity", "Action(s)"]
    page = "edit_products"
    field_order = {"text", "text", "number", "number"}

    return render_template('edit_row.html', data=data, headers=headers, page=page, field_order=field_order)


# Update for Edit Products
@app.route('/post_edit_products', methods=["POST"])
def post_edit_product_page():
    product_id = request.form.get("save_item")
    product_name = request.form.get("product_name")
    vendor_name = request.form.get("vendor_name")
    price = request.form.get("price")
    quantity = request.form.get("stock_quantity")

    if product_id is None:
        return redirect(url_for("admin_edit_products"))

    if vendor_name == "":
        vendor_id = None or "NULL"
        print("HERE")
        query = f"UPDATE items SET " \
                f"product_name='{product_name}', vendor_id={str(vendor_id)}, price={int(price)}, stock_quantity={int(quantity)} " \
                f"WHERE id={int(product_id)};"

    else:
        query = f"SELECT id from vendors where vendor_name='{vendor_name}';"
        results = execute_query(query)
        vendor_id = results.fetchall()

        if not vendor_id:
            query = f"INSERT INTO vendors (vendor_name) VALUES ('{vendor_name}');"
            execute_query(query)
            query = f"SELECT id from vendors where vendor_name='{vendor_name}';"
            results = execute_query(query)
            vendor_id = results.fetchall()

        vendor_id = vendor_id[0]["id"]
        query = f"UPDATE items SET " \
                f"product_name='{product_name}', vendor_id={int(vendor_id)}, price={int(price)}, stock_quantity={int(quantity)} " \
                f"WHERE id={int(product_id)};"

    execute_query(query)

    return redirect(url_for("admin_edit_products"))


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


# Edit for Edit Classes
@app.route('/edit_edit_classes', methods=["POST"])
def edit_class_page():
    class_id = request.form.get("edit_item")

    query = f"SELECT id, class_name, date, instructor, available_seats, price FROM classes WHERE id={int(class_id)};"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["class_name", "date", "instructor", "available_seats", "price"])
    headers = ["Class Name", "Class Date", "Instructor", "Available Seats", "Price", "Action(s)"]
    page = "edit_classes"
    field_order = {"text", "date", "text", "number", "number"}

    return render_template('edit_row.html', data=data, headers=headers, page=page, field_order=field_order)


# Update for Edit Classes
@app.route('/post_edit_classes', methods=["POST"])
def post_edit_class_page():
    class_id = request.form.get("save_item")
    class_name = request.form.get("class_name")
    date = request.form.get("date")
    instructor = request.form.get("instructor")
    seats = request.form.get("available_seats")
    price = request.form.get("price")

    if class_id is None:
        return redirect(url_for("admin_edit_classes"))

    query = f"UPDATE classes " \
            f"SET class_name='{class_name}', date='{date}', instructor='{instructor}', " \
            f"available_seats={int(seats)}, price={int(price)}" \
            f" WHERE id={int(class_id)};"
    execute_query(query)

    return redirect(url_for("admin_edit_classes"))


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


# Edit for Edit Orders
@app.route('/edit_edit_orders', methods=["POST"])
def edit_orders_page():
    order_id = request.form.get("edit_item")

    query = f"SELECT id, date, fulfilled, total_cost FROM orders WHERE id={int(order_id)};"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["date", "total_cost", "fulfilled"])
    headers = ["Date", "Total Cost", "Fulfilled", "Action(s)"]
    page = "edit_orders"
    field_order = {"date", "number", "checkbox"}

    return render_template('edit_row.html', data=data, headers=headers, page=page, field_order=field_order)


# Edit Post for Edit Orders
@app.route('/post_edit_orders', methods=["POST"])
def post_edit_orders_page():
    order_id = request.form.get("save_item")
    date = request.form.get("date")
    total_cost = request.form.get("total_cost")
    fulfilled_status = request.form.get("fulfilled")

    if order_id is None:
        return redirect(url_for("admin_edit_orders"))

    if fulfilled_status == "1":
        fulfilled = True
    else:
        fulfilled = False

    query = f"UPDATE orders SET date='{date}', total_cost={int(total_cost)}, fulfilled={fulfilled} WHERE id={int(order_id)};"
    execute_query(query)

    return redirect(url_for("admin_edit_orders"))


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
# Edit Order Items page
#
####################################################################################


@app.route('/view_edit_orders', methods=["GET", "POST"])
def view_order_item():
    order_id = request.form.get("view_item")

    query = f"SELECT order_items.id, order_items.quantity, items.product_name, items.price FROM order_items " \
            f"LEFT OUTER JOIN items ON order_items.item_id=items.id " \
            f"WHERE order_items.order_id={int(order_id)};"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["product_name", "price", "quantity"])

    headers = ["Product Name", "Price", "Quantity", "Action(s)"]
    button = ["edit", "delete"]
    title = f"Admin Tools - Order Items - Order Number {order_id}"
    page = "edit_order_items"

    return render_template('tables.html', data=data, headers=headers, button=button, title=title, page=page)


# Edit for Edit Order Items
@app.route('/edit_edit_order_items', methods=["POST"])
def edit_order_items_page():
    order_id = request.form.get("edit_item")

    query = f"SELECT id, quantity FROM order_items WHERE id={int(order_id)};"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["quantity"])
    headers = ["Quantity", "Action(s)"]
    page = "edit_order_items"
    field_order = {"number"}

    return render_template('edit_row.html', data=data, headers=headers, page=page, field_order=field_order)


# Edit Post for Edit Order Items
@app.route('/post_edit_order_items', methods=["POST"])
def post_edit_order_items_page():
    order_id = request.form.get("save_item")
    quantity = request.form.get("quantity")

    if order_id is None:
        return redirect(url_for("admin_edit_orders"))

    query = f"UPDATE order_items SET quantity={int(quantity)} WHERE id={int(order_id)};"
    execute_query(query)

    return redirect(url_for("admin_edit_orders"))


# Delete for Edit Order Items
@app.route('/delete_edit_order_items', methods=["POST"])
def delete_order_item():
    order_items_id = request.form.get("remove_item")

    query = f"DELETE FROM order_items where id={int(order_items_id)};"
    execute_query(query)

    return redirect(url_for("admin_edit_orders"))

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


# Edit for Edit Enrollments
@app.route('/edit_edit_enrollments', methods=["POST"])
def edit_enrollment_page():
    enroll_id = request.form.get("edit_item")

    query = f"SELECT id, course_result FROM enrollments WHERE id={int(enroll_id)};"

    results = execute_query(query)
    response = results.fetchall()

    data = format_data(response, ["course_result"])
    headers = ["Course Result", "Action(s)"]
    page = "edit_enrollments"
    field_order = {"text"}

    return render_template('edit_row.html', data=data, headers=headers, page=page, field_order=field_order)


# Edit Post for Edit Enrollments
@app.route('/post_edit_enrollments', methods=["POST"])
def post_edit_enrollment_page():
    enroll_id = request.form.get("save_item")
    course_result = request.form.get("course_result")

    if enroll_id is None:
        return redirect(url_for("admin_edit_enrollments"))

    query = f"UPDATE enrollments SET course_result='{course_result}' WHERE id={int(enroll_id)};"
    execute_query(query)

    return redirect(url_for("admin_edit_enrollments"))


# Delete for Edit Enrollments
@app.route('/delete_edit_enrollments', methods=["POST"])
def delete_enrollment():
    enroll_id = request.form.get("remove_item")

    query = f"DELETE FROM enrollments WHERE id={int(enroll_id)};"
    execute_query(query)

    return redirect(request.referrer)
