from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

# Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
dt = date.today()

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = BlogPost.query.get(index)
    if requested_post:
        return render_template("post.html", post=requested_post)
    else:
        return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/add", methods=["GET", "POST"])
def creat_post():
    form = CreatePostForm()
    if request.method == "POST" and form.validate_on_submit():
        new_blog = BlogPost(title=form.title.data, subtitle=form.subtitle.data, img_url=form.img_url.data,
                            body=form.body.data, author=form.author.data, date=dt.strftime("%d %B %Y"))
        db.session.add(new_blog)
        db.session.commit()
        del new_blog
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post_data = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(title=post_data.title, subtitle=post_data.subtitle,
                               author=post_data.author, img_url=post_data.img_url, body=post_data.body)
    if edit_form.validate_on_submit():
        post_data.title = edit_form.title.data
        post_data.subtitle = edit_form.subtitle.data
        post_data.img_url = edit_form.img_url.data
        post_data.body = edit_form.body.data
        post_data.author = edit_form.author.data
        post_data.date = dt.strftime("%d %B %Y")
        db.session.commit()
        return redirect(url_for('show_post', index=post_data.id))
    return render_template('make-post.html', form=edit_form)


@app.route("/delete-post/<int:del_id>")
def delete_post(del_id):
    blog_to_delete = BlogPost.query.get(del_id)
    if blog_to_delete:
        db.session.delete(blog_to_delete)
        db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
