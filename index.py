from flask import Flask, render_template, request, redirect, url_for, session
import oracledb
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'wiNdBreAKeR2015'

# -------------------------------
# Oracle DB connection setup
# -------------------------------
try:
    connection = oracledb.connect(
        user="system",
        password="Chilaka1900",
        dsn="localhost/XE"
    )
    cursor = connection.cursor()
    print("Connected to Oracle DB")
except Exception as e:
    print("DB ERROR:", e)

# -------------------------------
# Homepage
# -------------------------------
@app.route('/')
def homepage():
    return render_template('homepage.html')

# -------------------------------
# Login
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username = :1 AND password = :2", (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            print("Logged in as", username)
            return redirect(url_for('catalog'))
        else:
            print("Wrong credentials")
            return "Wrong username or password. Try again."

    return render_template('loginpage.html')

# -------------------------------
# Register
# -------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            cursor.execute(
                "INSERT INTO users (user_id, username, email, password) VALUES (users_seq.NEXTVAL, :1, :2, :3)",
                (username, email, password)
            )
            connection.commit()
            print("Registered new user:", username)
            return redirect(url_for('login'))

        except Exception as e:
            print("Registration error:", e)
            return f"Error: {e}"

    return render_template('register.html')

# -------------------------------
# Catalog Page
# -------------------------------
@app.route('/catalog')
def catalog():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('catalog.html', products=products)

# -------------------------------
# Add to Cart
# -------------------------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    try:
        cursor.execute("SELECT quantity FROM cart WHERE user_id = :1 AND product_id = :2", (user_id, product_id))
        result = cursor.fetchone()

        if result:
            cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id = :1 AND product_id = :2", (user_id, product_id))
        else:
            cursor.execute("INSERT INTO cart (cart_id, user_id, product_id, quantity) VALUES (cart_seq.NEXTVAL, :1, :2, 1)", (user_id, product_id))

        connection.commit()
        return redirect(url_for('catalog'))

    except Exception as e:
        print("Cart Error:", e)
        return f"Error: {e}"

@app.route('/increase_quantity', methods=['POST'])
def increase_quantity():
    product_id = request.form['product_id']
    user_id = session.get('user_id')

    try:
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id = :1 AND product_id = :2", (user_id, product_id))
        connection.commit()
        return redirect('/cart')
    except Exception as e:
        print("Increase Error:", e)
        return f"Error: {e}"

@app.route('/decrease_quantity', methods=['POST'])
def decrease_quantity():
    product_id = request.form['product_id']
    user_id = session.get('user_id')

    try:
        cursor.execute("UPDATE cart SET quantity = quantity - 1 WHERE user_id = :1 AND product_id = :2 AND quantity > 1", (user_id, product_id))
        connection.commit()
        return redirect('/cart')
    except Exception as e:
        print("Decrease Error:", e)
        return f"Error: {e}"

# -------------------------------
# Remove from Cart
# -------------------------------
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form['product_id']
    user_id = session.get('user_id')

    try:
        cursor.execute("DELETE FROM cart WHERE user_id = :1 AND product_id = :2", (user_id, product_id))
        connection.commit()
        return redirect('/cart')
    except Exception as e:
        print("Remove Error:", e)
        return f"Error: {e}"

# -------------------------------
# View Cart
# -------------------------------
@app.route('/cart')
def view_cart():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    cursor.execute("""
        SELECT p.title, p.price, p.image_path, c.quantity, p.product_id
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = :1
    """, (user_id,))
    cart_items = cursor.fetchall()
    total_price = sum(item[1] * item[3] for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

# -------------------------------
# Launch App
# -------------------------------
if __name__ == '__main__':
    print("Flask app running...")
    app.run(debug=True)
