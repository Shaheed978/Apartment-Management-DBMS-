# Importing necessary libraries
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

# Creating the Flask app instance
app = Flask(__name__, template_folder="templates")

# Function to establish a connection to the database
def get_database_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'apartment_management.db')
    return sqlite3.connect(db_path)

# Function to execute SQL queries
def execute_query(query, parameters=None):
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        conn.commit()
        result = cursor.fetchall()
        return result
    except sqlite3.OperationalError as e:
        print("OperationalError:", e)
        conn.rollback()
    finally:
        conn.close()

# Function to create database tables if they don't exist
def create_tables():
    create_apartments_table = '''
        CREATE TABLE IF NOT EXISTS Apartments (
            apartment_number INTEGER PRIMARY KEY,
            apartment_type TEXT NOT NULL,
            rent REAL NOT NULL,
            occupancy INTEGER DEFAULT 0,
            check_in_date DATE,
            check_out_date DATE
        )
    '''

    create_tenants_table = '''
        CREATE TABLE IF NOT EXISTS Tenants (
            tenant_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE
        )
    '''

    create_leases_table = '''
        CREATE TABLE IF NOT EXISTS Leases (
            lease_id INTEGER PRIMARY KEY,
            tenant_id INTEGER NOT NULL,
            apartment_number INTEGER NOT NULL,
            check_in_date DATE NOT NULL,
            check_out_date DATE NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES Tenants(tenant_id),
            FOREIGN KEY (apartment_number) REFERENCES Apartments(apartment_number)
        )
    '''

    execute_query(create_apartments_table)
    execute_query(create_tenants_table)
    execute_query(create_leases_table)

# Flask route to display leased apartments
@app.route('/show_leased_apartments')
def show_leased_apartments():
    # Query the database for leased apartments with check-in and check-out dates
    leased_apartments = execute_query('SELECT apartment_number, tenant_id, check_in_date, check_out_date FROM Leases WHERE check_in_date IS NOT NULL AND check_out_date IS NOT NULL')
    return render_template('show_leased_apartments.html', leased_apartments=leased_apartments)

# Flask route to remove a tenant
@app.route('/remove_tenant/<int:tenant_id>')
def remove_tenant(tenant_id):
    execute_query('DELETE FROM Tenants WHERE tenant_id = ?', (tenant_id,))
    return redirect(url_for('show_tenants'))

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for adding a new tenant
@app.route('/add_tenant', methods=['GET', 'POST'])
def add_tenant():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        execute_query('INSERT INTO Tenants (name, email, phone) VALUES (?, ?, ?)', (name, email, phone))
        return redirect(url_for('index'))
    return render_template('add_tenant.html')

# Route for leasing an apartment
@app.route('/add_lease_apartment', methods=['GET', 'POST'])
def add_lease_apartment():
    if request.method == 'POST':
        apartment_number = request.form['apartment_number']
        tenant_id = request.form['tenant_id']
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        # Handle the leasing logic here
        execute_query('INSERT INTO Leases (tenant_id, apartment_number, check_in_date, check_out_date) VALUES (?, ?, ?, ?)', (tenant_id, apartment_number, check_in_date, check_out_date))
        return redirect(url_for('index'))
    else:
        # Handle the case where the request method is not POST
        return render_template('add_lease_apartment.html')

# Route to display the list of tenants
@app.route('/show_tenants')
def show_tenants():
    tenants = execute_query('SELECT * FROM Tenants')
    return render_template('show_tenants.html', tenants=tenants)

# Main block to run the app
if __name__ == "__main__":
    create_tables()
    app.run(debug=True, port=5009)
