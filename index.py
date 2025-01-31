from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Database setup
db_file = 'data_entries.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    description TEXT,
                    price REAL,
                    timestamp TEXT
                  )''')
conn.commit()
conn.close()

# Dropdown categories and corresponding emojis
categories = {
    "Fruits": "🍎",
    "Vegetables": "🥒",
    "Eating out": "🍽️",
    "Logistics": "📦",
    "Groceries": "🛒",
    "Milk/Dairy": "🥛",
    "Misc.": "❓"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        category = request.form.get('category')
        description = request.form.get('description')
        price = request.form.get('price')

        # Validate input
        if category and description and price:
            try:
                price = float(price)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Save entry to the database
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO entries (category, description, price, timestamp) VALUES (?, ?, ?, ?)", (category, description, price, timestamp))
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
            except ValueError:
                pass

    return render_template('index.html', categories=categories)

@app.route('/analysis')
def analysis():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(price) FROM entries GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    categories = [row[0] for row in data]
    expenditures = [row[1] for row in data]

    # Plotting the graph
    plt.figure(figsize=(10, 6))
    plt.bar(categories, expenditures, color='skyblue')
    plt.title('Expenditure by Category')
    plt.xlabel('Category')
    plt.ylabel('Total Expenditure')

    # Save the plot to a string buffer
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('analysis.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
