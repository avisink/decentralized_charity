from app import app
import sqlite3

def populate_initial_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO charities (name, address) VALUES ('Charity 1', 'GABCD1234...')")
    c.execute("INSERT INTO charities (name, address) VALUES ('Charity 2', 'GBXYZ5678...')")
    conn.commit()
    conn.close()

populate_initial_data()

if __name__ == '__main__':
    app.run(debug=True)
