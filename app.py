from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# 🔥 Initialize Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Using SQLite
app.config['SECRET_KEY'] = 'your_secret_key'  # Secret Key for Session Management

# 📌 Initialize Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# 🚀 User Model (Authentication)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        """Hash and store the user's password."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the entered password matches the stored hash."""
        return bcrypt.check_password_hash(self.password, password)

# 🍕 Menu Model
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)

# 🔑 Flask-Login: Load User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 🎯 Home Route (Menu Page)
@app.route('/')
@login_required
def menu():
    menu_items = MenuItem.query.all()
    return render_template('menu.html', menu_items=menu_items)

# 📝 Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Try another one.', 'warning')
            return redirect(url_for('register'))

        # Create New User & Hash Password
        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# 🔑 Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):  
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('menu'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# 🚪 Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# 🛒 Cart Route
@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

# ➕ Add to Cart Route
@app.route('/add_to_cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item = MenuItem.query.get_or_404(item_id)
    cart = session.get('cart', {})

    if str(item_id) in cart:
        cart[str(item_id)]['quantity'] += 1
    else:
        cart[str(item_id)] = {'name': item.name, 'price': item.price, 'quantity': 1}
    
    session['cart'] = cart
    flash(f'{item.name} added to cart!', 'success')
    return redirect(url_for('menu'))

# ✅ Place Order Route
@app.route('/order')
@login_required
def order():
    session.pop('cart', None)  # Clear cart after order
    flash('Order placed successfully!', 'success')
    return render_template('order.html')

# 🎯 Database Setup (Run Once)
with app.app_context():
    db.create_all()

    # ✅ Insert Default Menu Items (Run Only If DB is Empty)
    if MenuItem.query.count() == 0:
        menu_items = [
            MenuItem(name="Burger", price=99.00, image="burger.jpg"),
            MenuItem(name="Pizza", price=199.00, image="pizza.jpg"),
            MenuItem(name="Pasta", price=149.00, image="pasta.jpg"),
            MenuItem(name="Salad", price=89.00, image="salad.jpg"),
            MenuItem(name="Sushi", price=189.00, image="sushi.jpg"),
            MenuItem(name="Fries", price=49.00, image="fries.jpg"),
            MenuItem(name="Taco", price=129.00, image="taco.jpg"),
            MenuItem(name="Sandwich", price=89.00, image="sandwich.jpg"),
            MenuItem(name="Ice Cream", price=59.00, image="icecream.jpg"),
        ]
        db.session.add_all(menu_items)
        db.session.commit()

# 🚀 Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
