from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'washington'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(150))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('You logged in Successfully ' + username, 'success')
            print(session)
            return redirect('/newpost')

        else:
            flash('User password does not match, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        username_error = ''
        password_error = ''
        verify_error = ''

        if username == '':
            username_error = 'Username must be entered'
        elif username.find(' ') >= 1:
            username_error = 'Username cannot have spaces'
        elif len(username) < 3 or len(username) >20:
            username_error = 'Username must be between 3 and 20 characters'
        elif username == existing_user:
            username_error = 'Username already exists'

        if password == '':
            password_error = 'Password must be entered'
            verify_error = 'Password must be entered'
        elif password.find(' ') >= 1:
            password_error = 'Password cannot have spaces'
        elif len(password) < 3 or len(password) > 20:
            password_error = 'Password must be between 3 and 20 characters'
        elif password != verify:
            password_error = 'Passwords do not match'
            verify_error = 'Passwords do not match'

        if username_error or password_error or verify_error:
            return render_template('signup.html', username=username, username_error=username_error, password='', password_error=password_error, verify='', verify_error=verify_error)

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('Signup Successful', 'success')
            return redirect('/newpost')
        else:
            flash('Username already exists', 'error')
            return render_template('signup.html')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('You have successfully logged out', 'success')
    return redirect('/blog')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['post_title']
        body = request.form['new_post']
        body_error=''
        title_error=''
        if title=="":
                title_error = "Add a title"
        if body=="":
                body_error = "Add a body"
        if title=="" or body=="":
            return render_template('newpost.html', title_error=title_error, body_error=body_error, title=title, body=body)
        else:
            owner = User.query.filter_by(username=session['username']).first()
            new_entry = Blog(title, body, owner)
            db.session.add(new_entry)
            db.session.commit()
            flash('Post Successful', 'success')
            return redirect('/blog?id='+str(new_entry.id))
    else:
        return render_template('newpost.html')

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    owner_id = request.args.get('user')
    if (owner_id):
        blogs = Blog.query.filter_by(owner_id=owner_id)
        return render_template('blog.html', title="User Posts", blogs=blogs)

    blog_id = request.args.get('id')
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('single-post.html', page_title="Blog Entry", blog=blog)

    sort_type = request.args.get('sort')
    if sort_type == "newest":
        blogs = Blog.query.order_by(Blog.created.desc()).all()
    else:
        blogs = Blog.query.all()

    return render_template('blog.html', blogs=blogs)

if __name__ == '__main__':
    app.run()