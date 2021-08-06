# Class 2 Masimthembe Ndabeni
# Flask-End-of-Module Project
# Soccer Boots Point-of-Sale-API
import email
import hmac
import sqlite3
import datetime

from flask import Flask
from flask_mail import Mail, Message

from flask import Flask, request, jsonify, redirect, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, username, password, user_email, phone_number, address):
        self.id = id
        self.username = username
        self.password = password
        self.user_email = user_email
        self.phone_number = phone_number
        self.address = address


# Creating User_table
def init_user_table():
    conn = sqlite3.connect('Point_of_Sale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL, address TEXT NOT NULL, phone_number INT NOT NULL, user_email TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# Creating Post_table
def init_user_login_table():
    with sqlite3.connect('Point_of_Sale.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS login (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "user_email TEXT NOT NULL,"
                     "password TEXT NOT NULL,"
                     "login_date TEXT NOT NULL)")
    print("Login table created successfully.")


# Creating product_table
def init_product_table():
    with sqlite3.connect('Point_of_Sale.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS user_products (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_name TEXT NOT NULL,"
                     "price INTEGER NOT NULL,"
                     "description TEXT NOT NULL)")
    print("Product table created successfully.")


# Tables
init_product_table()
init_user_table()
init_user_login_table()


def fetch_users():
    with sqlite3.connect('Point_of_Sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")

        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4], data[5], data[6], data[7]))
    return new_data




users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sithandathuzipho@gmail.com'
app.config['MAIL_PASSWORD'] = 'Crf6ZS@#'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
Mail = Mail(app)

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/login/', methods=['GET', 'POST'])
def login():
    return render_template('/login.html')


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        phone_number = request.form['phone_number']
        user_email = request.form['user_email']

        with sqlite3.connect("Point_of_Sale.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password,address,phone_number,user_email) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (first_name, last_name, username, password, address, phone_number, user_email))
            conn.commit()
            response["message"] = "successfully registered"
            response["status_code"] = 201


            msg = Message('Congratulations', sender='sithandathuzipho@gmail.com', recipients=['sithandathuzipho@gmail.com'])
            msg.body = "You have successfully registered"
            Mail.send(msg)

        return response


# route to create products

@app.route('/create-products/', methods=["POST"])
@jwt_required()
def create_products():
    response = {}

    if request.method == "POST":
        product_name = request.form['product_name']
        price = request.form['price']
        description = request.form['description']
        with sqlite3.connect('Point_of_Sale.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_products("
                           "product_name,"
                           "price,"
                           "description) VALUES(?, ?, ?)", (product_name, price, description))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "products created successfully"
        return response


# Creating products

@app.route('/products/')
def show_products():
    products = [{'id': 0, 'Product_name': 'Yocco speed point', 'Price': 300, 'Description': 'The best speed point'},
                {'id': 1, 'Product_name': 'samsung', 'Description': 'smartphone'}]
    return jsonify(products)


@app.route('/get_products/', methods=["GET"])
def get_Point_of_Sales():
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM user_products")
        posts = cursor.fetchall()
        accumulator = []

        for i in posts:
           accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)



# route to delete products
@app.route("/delete-products/<int:post_id>")
@jwt_required()
def delete_post(post_id):
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_products WHERE id=" + str(post_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "products deleted successfully."
    return response

# route to update products

@app.route('/update_products/<int:post_id>/', methods=["PUT"])
@jwt_required()
def update_product(post_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('Point_of_Sale.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

        # updating product_name
            if incoming_data.get("product_name") is not None:
                put_data["product_name"] = incoming_data.get("product_name")
                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user_products SET product_name =? WHERE id=?", (put_data["product_name"], post_id))
                    conn.commit()
                    response['message'] = "product_name Updated successfully"
                    response['status_code'] = 200

        # updating price
            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user_products SET price =? WHERE id=?", (put_data["price"], post_id))
                    conn.commit()

                    response["price"] = "price updated successfully"
                    response["status_code"] = 200

        # updating description
            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user_products SET description =? WHERE id=?", (put_data["description"], post_id))
                    conn.commit()

                    response["price"] = "description updated successfully"
                    response["status_code"] = 200
    return response


if __name__ == '__main__':
    app.run(debug=True)
