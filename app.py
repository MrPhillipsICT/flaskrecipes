from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ross'
app.config['MYSQL_PASSWORD'] = 'K@y1eigh1908'  # Use your MySQL password
app.config['MYSQL_DB'] = 'flaskapp'

mysql = MySQL(app)

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form fields
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Basic validation for email format
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return "Invalid email address!"

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
        mysql.connection.commit()
        return redirect('/')
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        
        if user:
            session['loggedin'] = True
            session['username'] = user['username']
            return redirect('/submit_recipe')
        else:
            return "Invalid credentials!"
    return render_template('login.html')

# Submit Recipe Route
@app.route('/submit_recipe', methods=['GET', 'POST'])
def submit_recipe():
    if 'loggedin' in session:
        if request.method == 'POST':
            recipe_name = request.form['recipe_name']
            ingredients = request.form['ingredients']
            instructions = request.form['instructions']
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO recipes (username, recipe_name, ingredients, instructions) VALUES (%s, %s, %s, %s)', 
                           (session['username'], recipe_name, ingredients, instructions))
            mysql.connection.commit()
            return "Recipe submitted successfully!"
        return render_template('submit_recipe.html')
    return redirect('/login')
 
@app.route('/members', methods=['GET'])
def members():
    # Check if the user is logged in
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch all recipes submitted by the logged-in user
        cursor.execute('SELECT * FROM recipes WHERE username = %s', [session['username']])
        recipes = cursor.fetchall()
        return render_template('members.html', recipes=recipes)
    return redirect('/login')

@app.route('/edit_recipe/<int:id>', methods=['GET', 'POST'])
def edit_recipe(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch the specific recipe to edit
        cursor.execute('SELECT * FROM recipes WHERE id = %s AND username = %s', (id, session['username']))
        recipe = cursor.fetchone()
        
        if request.method == 'POST':
            # Update the recipe with the new data
            new_name = request.form['recipe_name']
            new_ingredients = request.form['ingredients']
            new_instructions = request.form['instructions']
            cursor.execute('UPDATE recipes SET recipe_name = %s, ingredients = %s, instructions = %s WHERE id = %s',
                           (new_name, new_ingredients, new_instructions, id))
            mysql.connection.commit()
            return redirect('/members')
        
        return render_template('edit_recipe.html', recipe=recipe)
    return redirect('/login')


@app.route('/delete_recipe/<int:id>', methods=['GET'])
def delete_recipe(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Delete the recipe
        cursor.execute('DELETE FROM recipes WHERE id = %s AND username = %s', (id, session['username']))
        mysql.connection.commit()
        
        return redirect('/members')
    return redirect('/login')


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
