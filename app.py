from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Sample static products
static_products = [
    {'title': 'Product 1', 'price': '€10', 'link': 'https://example.com/product1'},
    {'title': 'Product 2', 'price': '€20', 'link': 'https://example.com/product2'},
    {'title': 'Product 3', 'price': '€30', 'link': 'https://example.com/product3'},
]

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(static_products)

def fetch_products_from_source(url, query):
    try:
        response = requests.get(url, params={'q': query})
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []
        for item in soup.select('.product-item'):  # Adjust the selector based on the website's structure
            title = item.select_one('.product-title').text.strip()
            price = item.select_one('.product-price').text.strip()
            link = item.select_one('a')['href']
            products.append({'title': title, 'price': price, 'link': link})

        return products
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    # Example URLs for different sources
    sources = [
        'https://example.com/search',  # Replace with actual URLs
        'https://another-example.com/search'
    ]

    all_products = []
    for source in sources:
        products = fetch_products_from_source(source, query)
        all_products.extend(products)

    if not all_products:
        return jsonify({'message': 'No products found'}), 404

    return jsonify(all_products)

if __name__ == '__main__':
    app.run(debug=True) 