from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from config import Config
from models import init_db

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database initialization
init_db(app)

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    if user:
        return UserMixin(id=user[0])
    return None

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

# Recipe Form
class RecipeForm(FlaskForm):
    title = StringField('Recipe Title', validators=[DataRequired()])
    content = TextAreaField('Recipe Content', validators=[DataRequired()])
    submit = SubmitField('Submit Recipe')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (form.username.data, form.email.data, hashed_password))
        mysql.connection.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Add login logic here
    return render_template('login.html')

@app.route("/recipe/new", methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO recipes (title, content, user_id) VALUES (%s, %s, %s)",
                    (form.title.data, form.content.data, current_user.id))
        mysql.connection.commit()
        flash('Your recipe has been posted!', 'success')
        return redirect(url_for('home'))
    return render_template('create_recipe.html', form=form)

@app.route("/home")
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM recipes")
    recipes = cur.fetchall()
    return render_template('home.html', recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
