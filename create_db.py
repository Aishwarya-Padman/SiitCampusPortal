import sqlite3
from app import db, Image, app

def create_sqlite_table():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create the contact_form table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS contact_form (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("SQLite database and table created successfully.")

def create_mysql_tables():
    with app.app_context():
        db.create_all()  # Ensure MySQL tables are created
        print("MySQL tables created successfully.")

        # Insert image records if they don't exist
        if not Image.query.first():  # Check if images already exist
            img1 = Image(name="Library", path="images/library.jpg")
            img2 = Image(name="Playground", path="images/playground.jpg")
            img3 = Image(name="Mess", path="images/mess.jpg")

            db.session.add_all([img1, img2, img3])
            db.session.commit()
            print("Image records inserted successfully.")
        else:
            print("Image records already exist.")

if __name__ == "__main__":
    create_sqlite_table()   # Create SQLite table
    create_mysql_tables()   # Create MySQL tables and insert image records
