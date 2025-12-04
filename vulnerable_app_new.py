from flask import Flask, request, render_template_string, session, redirect, url_for
import sqlite3
import os
import bleach

from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_dev_key")

csrf = CSRFProtect(app)

class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])

class CommentForm(FlaskForm):
    comment = TextAreaField("comment", validators=[DataRequired()])

def get_db_connection():
    conn = sqlite3.connect('example_new.db')
    conn.row_factory = sqlite3.Row
    return conn






@app.route('/')
def index():
    return render_template_string("""
        <div class='container'>
            <h1>Welcome</h1>
            <a href='/login'>Login</a>
        </div>
    """)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))

        error = "Invalid credentials!"
    else:
        error = None

    return render_template_string("""
        <div class='container'>
            <h1>Login</h1>

            {% if error %}
                <div class='alert alert-danger'>{{ error }}</div>
            {% endif %}

            <form method='post'>
                {{ form.hidden_tag() }}

                <div class='form-group'>
                    <label>Username</label>
                    {{ form.username(class="form-control") }}
                </div>

                <div class='form-group'>
                    <label>Password</label>
                    {{ form.password(class="form-control") }}
                </div>

                <button class='btn btn-primary'>Login</button>
            </form>
        </div>
    """, form=form, error=error)


@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    comments = conn.execute(
        "SELECT comment FROM comments WHERE user_id = ?", (session["user_id"],)
    ).fetchall()
    conn.close()

    form = CommentForm()

    return render_template_string("""
        <div class='container'>
            <h1>Dashboard (User {{ user_id }})</h1>

            <form method='post' action='/submit_comment'>
                {{ form.hidden_tag() }}

                <div class='form-group'>
                    <label>Comment</label>
                    {{ form.comment(class="form-control") }}
                </div>

                <button class='btn btn-primary'>Submit Comment</button>
            </form>

            <h2>Your Comments</h2>
            <ul class='list-group'>
                {% for c in comments %}
                    <li class='list-group-item'>{{ c['comment'] }}</li>
                {% endfor %}
            </ul>
        </div>
    """, comments=comments, form=form, user_id=session["user_id"])


@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    if "user_id" not in session:
        return redirect(url_for("login"))

    form = CommentForm()

    if form.validate_on_submit():
        comment = bleach.clean(form.comment.data)

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO comments (user_id, comment) VALUES (?, ?)",
            (session["user_id"], comment)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("dashboard"))


@app.route('/admin')
def admin():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    return render_template_string("""
        <div class='container'>
            <h1>Admin Panel</h1>
        </div>
    """)


if __name__ == '__main__':
    app.run(debug=False)
