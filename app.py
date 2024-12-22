from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    url = f'https://example.com/search?q={query}'  # Replace with the actual URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []
    for item in soup.select('.product-item'):  # Adjust the selector based on the website's structure
        title = item.select_one('.product-title').text
        price = item.select_one('.product-price').text
        link = item.select_one('a')['href']
        products.append({'title': title, 'price': price, 'link': link})

    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True) 