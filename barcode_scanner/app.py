from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def main():
    conn = get_db_connection()
    items = session.get('current_list', [])
    total_usd = sum(item['price_usd'] for item in items)
    conn.close()
    rate = session.get('rate', 1500)  # Default rate if not set
    return render_template('main.html', items=items, total_usd=total_usd, rate=rate)

@app.route('/scan', methods=['POST'])
def scan_item():
    barcode = request.form['barcode']
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE barcode = ?', (barcode,)).fetchone()
    conn.close()
    if item:
        item_dict = {'name': item['name'], 'price_usd': item['price_usd']}
        if 'current_list' not in session:
            session['current_list'] = []
        current_list = session['current_list']
        current_list.append(item_dict)
        session['current_list'] = current_list  # Update the session with the new list
    return redirect(url_for('main'))

@app.route('/delete_item/<int:item_index>', methods=['GET', 'POST'])
def delete_item(item_index):
    if 'current_list' in session:
        current_list = session['current_list']
        if 0 <= item_index < len(current_list):
            del current_list[item_index]
            session['current_list'] = current_list  # Update the session with the modified list
    return redirect(url_for('main'))


@app.route('/new_list')
def new_list():
    session.pop('current_list', None)
    return redirect(url_for('main'))

@app.route('/list', methods=('GET', 'POST'))
def list_items():
    conn = get_db_connection()
    if request.method == 'POST':
        barcode = request.form['barcode']
        name = request.form['name']
        price_usd = request.form['price_usd']
        conn.execute('INSERT INTO items (barcode, name, price_usd) VALUES (?, ?, ?)', (barcode, name, price_usd))
        conn.commit()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('list.html', items=items)

@app.route('/delete_database_item/<int:item_id>', methods=['POST'])
def delete_database_item(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_items'))


@app.route('/rate', methods=('GET', 'POST'))
def rate():
    conn = get_db_connection()
    if request.method == 'POST':
        new_rate = request.form['rate']
        session['rate'] = float(new_rate)
    rate = session.get('rate', 1500)
    return render_template('rate.html', rate=rate)

if __name__ == '__main__':
    app.run(debug=True)
