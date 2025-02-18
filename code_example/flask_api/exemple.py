import sqlite3
import time
from flask import Flask, request, jsonify
#import monitor

app = Flask(__name__)
DATABASE = 'example.db'

def heavy_computation():
    """Simulate a long-running business logic operation."""
    time.sleep(1)  # Simulate a time-consuming task
    return 2000


def init_db():
    """Initialize the SQLite database with a sample table."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL
            )
        ''')
        conn.commit()

@app.route('/items', methods=['GET'])
def get_items():
    """Fetch all items from the database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, value FROM items")
        rows = cursor.fetchall()
        items = []
        for row in rows:
            items.append({'id': row[0], 'name': row[1], 'value': row[2]})
    return jsonify(items), 200

@app.route('/items', methods=['POST'])
def create_item():
    """Insert a new item into the database."""
    data = request.get_json()
    name = data.get('name')
    value = data.get('value')

    if not all([name, value]):
        return jsonify({'error': 'Name and value are required fields.'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, value) VALUES (?, ?)",
            (name, value)
        )
        conn.commit()
        new_id = cursor.lastrowid

    return jsonify({'id': new_id, 'name': name, 'value': value}), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update an existing item by ID."""
    data = request.get_json()
    name = data.get('name')
    value = data.get('value')


    if not all([name, value]):
        return jsonify({'error': 'Name and value are required fields.'}), 400

    value += heavy_computation()

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE items SET name = ?, value = ? WHERE id = ?",
            (name, value, item_id)
        )
        conn.commit()
    
    return jsonify({'id': item_id, 'name': name, 'value': value}), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item from the database by ID."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()

    return jsonify({'message': f'Item with id {item_id} has been deleted.'}), 200


if __name__ == '__main__':
    init_db()
    app.run(debug=False)
