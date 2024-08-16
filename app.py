import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
from PIL import Image
from rembg import remove
import urllib.parse

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('clothing.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS clothing_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        type TEXT,
                        category TEXT,
                        market_price TEXT,
                        color TEXT,
                        style TEXT,
                        name TEXT,
                        favorited INTEGER)''')
    conn.commit()
    conn.close()

def add_clothing_item(filename, clothing_type, category):
    conn = sqlite3.connect('clothing.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO clothing_items (filename, type, category, market_price, color, style, name, favorited)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (filename, clothing_type, category, '', '', '', '', 0))
    conn.commit()
    conn.close()

def get_clothing_items():
    conn = sqlite3.connect('clothing.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clothing_items')
    items = cursor.fetchall()
    conn.close()
    return items

def update_clothing_item(index, clothing_type, category):
    conn = sqlite3.connect('clothing.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE clothing_items SET type = ?, category = ? WHERE id = ?''', (clothing_type, category, index))
    conn.commit()
    conn.close()

def update_item_info(index, category, market_price, color, style, name):
    conn = sqlite3.connect('clothing.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE clothing_items SET category = ?, market_price = ?, color = ?, style = ?, name = ? WHERE id = ?''',
                   (category, market_price, color, style, name, index))
    conn.commit()
    conn.close()

def toggle_favorite(index):
    conn = sqlite3.connect('clothing.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT favorited FROM clothing_items WHERE id = ?''', (index,))
    favorited = cursor.fetchone()[0]
    new_favorited = 1 if favorited == 0 else 0
    cursor.execute('''UPDATE clothing_items SET favorited = ? WHERE id = ?''', (new_favorited, index))
    conn.commit()
    conn.close()

def delete_clothing_item(index):
    conn = sqlite3.connect('clothing.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clothing_items WHERE id = ?', (index,))
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Mock data for clothing items
CLOTHING_TYPES = ['Shirt', 'Pants', 'Jacket', 'Dress', 'Shoes', 'Watches', 'Hats', 'Necklaces', 'Socks', 'Sweater']
CATEGORIES = {
    'Shirt': 'Tops',
    'Pants': 'Bottoms',
    'Jacket': 'Outerwear',
    'Dress': 'Dresses',
    'Shoes': 'Footwear',
    'Watches': 'Accessories',
    'Hats': 'Accessories',
    'Necklaces': 'Accessories',
    'Socks': 'Footwear',
    'Sweater': 'Tops'
}

# Function to remove background from image
def remove_background(image_data):
    output_data = remove(image_data)
    return output_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        image_url = request.form.get('url')
        clothing_type = request.form['type']

        if file:
            input_path = os.path.join('static/uploads', file.filename)
            file.save(input_path)
        elif image_url:
            parsed_url = urllib.parse.urlparse(image_url)
            basename = os.path.basename(parsed_url.path)
            input_path = os.path.join('static/uploads', basename)
            response = requests.get(image_url)
            with open(input_path, 'wb') as f:
                f.write(response.content)
        else:
            return redirect(url_for('index'))

        output_path = os.path.join('static/uploads', 'bg_' + os.path.basename(input_path))
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()
            output_data = remove_background(input_data)
            with open(output_path, 'wb') as output_file:
                output_file.write(output_data)

        add_clothing_item('bg_' + os.path.basename(input_path), clothing_type, CATEGORIES[clothing_type])

        return redirect(url_for('index'))

    clothing_items = get_clothing_items()
    favorites = [item for item in clothing_items if item[8] == 1]  # Favorited items have a value of 1 in favorited field
    return render_template('index.html', items=clothing_items, types=CLOTHING_TYPES, favorites=favorites)

@app.route('/edit/<int:index>', methods=['POST'])
def edit_item_type(index):
    data = request.json
    update_clothing_item(index, data['type'], CATEGORIES[data['type']])
    return jsonify(success=True)

@app.route('/edit_item/<int:index>', methods=['POST'])
def edit_item_info(index):
    data = request.json
    update_item_info(index, data['category'], data['marketPrice'], data['color'], data['style'], data['name'])
    return jsonify(success=True)

@app.route('/favorite/<int:index>', methods=['POST'])
def favorite_item(index):
    toggle_favorite(index)
    return jsonify(success=True)

@app.route('/delete/<int:index>', methods=['POST'])
def delete_item(index):
    delete_clothing_item(index)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
