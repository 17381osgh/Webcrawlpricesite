from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}!'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Sample static products
static_products = [
    {'title': 'Product 1', 'price': '€10', 'link': 'https://example.com/product1'},
    {'title': 'Product 2', 'price': '€20', 'link': 'https://example.com/product2'},
    {'title': 'Product 3', 'price': '€30', 'link': 'https://example.com/product3'},
]

# Sample recommended products
recommended_products = [
    {'title': 'Recommended Product 1', 'price': '€15', 'link': 'https://example.com/recommended1'},
    {'title': 'Recommended Product 2', 'price': '€25', 'link': 'https://example.com/recommended2'},
    {'title': 'Recommended Product 3', 'price': '€35', 'link': 'https://example.com/recommended3'},
]

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(static_products)

@app.route('/recommended', methods=['GET'])
def get_recommended_products():
    return jsonify(recommended_products)

def fetch_products(query):
    search_url = f"https://www.example-search-engine.com/search?q={query}"  # Replace with a real search engine URL
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []
        for item in soup.select('.product-item'):  # Adjust the selector based on the website's structure
            title = item.select_one('.product-title').text.strip()
            price = item.select_one('.product-price').text.strip()
            link = item.select_one('a')['href']
            products.append({'title': title, 'price': price, 'link': link})

        return products
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    all_products = fetch_products(query)

    if not all_products:
        return jsonify({'message': 'No products found'}), 404

    # Choose recommended and static products based on search results
    chosen_recommended = []
    chosen_static = []

    for product in all_products:
        if 'Recommended' in product['title'] or float(product['price'].replace('€', '').replace(',', '.')) < 20:
            chosen_recommended.append(product)
        else:
            chosen_static.append(product)

    return jsonify({
        'recommended': chosen_recommended,
        'static': chosen_static
    })

if __name__ == '__main__':
    db.create_all()  # Create database tables
    app.run(debug=True) 