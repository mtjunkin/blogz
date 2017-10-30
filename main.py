from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(150))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect('/blog')

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
                new_entry = Blog(title, body)
                db.session.add(new_entry)
                db.session.commit()
                return redirect('/blog?id='+str(new_entry.id))
    else:
        return render_template('newpost.html')

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template('single-post.html', blog=blog)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs, title="Build A Blog")

def require_input(string):
    if string == '':
        return False
    else:
        return True

if __name__ == '__main__':
    app.run()