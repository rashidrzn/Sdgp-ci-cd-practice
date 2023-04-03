from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_wtf import form

from forms import RegistrationForm, LoginForm
from flask_mysqldb import MySQL, MySQLdb
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd5f9cd14dac908b79558cb5d'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'd5f9cd14dac908b79558cb5d'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_app_db'
app.config['MYSQL_DB'] = 'crowd'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    users = []
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user_about")
    for row in cursor.fetchall():
        users.append(row)
    cursor.close()
    return render_template('about.html', users = users)



@app.route("/result")
def result():
    return render_template('result.html', title='Result')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template("register.html", form=form)
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        c_password = request.form['c-password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        if all(not param.strip() for param in [name, email, password, c_password]):
            flash("Please fill all the field before submitting")
            return redirect(url_for('register'))
        # elif not name:
        #     flash("Please check before registering as you missed a required information(name)")
        #     return redirect(url_for('register'))
        # elif not email:
        #     flash("Please check before registering as you missed a required information(email)")
        #     return redirect(url_for('register'))
        # elif not password:
        #     flash("Please check before registering as you missed a required information(password)")
        #     return redirect(url_for('register'))
        else:

            if password != c_password:
                flash(name + "! your password are not matching, please enter the same password.")
                return redirect(url_for('register'))
            else:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
                            (name, email, hash_password,))
                mysql.connection.commit()

                flash(f'Account created for {name}!', 'success')
                return redirect(url_for('login'))


# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         if form.email.data == 'admin@blog.com' and form.password.data == 'password':
#             flash('You have been logged in!', 'success')
#             return redirect(url_for('home'))
#         else:
#             flash('Login Unsuccessful. Please check username and password', 'danger')
#     return render_template('login.html', title='Login', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return render_template("home.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html", form=form)
    
    
@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True)
