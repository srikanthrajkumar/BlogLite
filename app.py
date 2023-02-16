import os
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_bcrypt import Bcrypt
from flask_restful import Resource, Api, reqparse
import datetime

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(current_dir, 'static/images')
db = SQLAlchemy()
bcrypt = Bcrypt(app)
db.init_app(app)
api = Api(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##################################################  API  ############################################################

c_use_parse = reqparse.RequestParser()
c_use_parse.add_argument('firstname')
c_use_parse.add_argument('lastname')
c_use_parse.add_argument('username')
c_use_parse.add_argument('password')
c_use_parse.add_argument('image_file')

u_use_parse = reqparse.RequestParser()
u_use_parse.add_argument('firstname')
u_use_parse.add_argument('lastname')
u_use_parse.add_argument('username')

c_art_parse = reqparse.RequestParser()
c_art_parse.add_argument('title')
c_art_parse.add_argument('content')
c_art_parse.add_argument('image_file')


u_art_parse = reqparse.RequestParser()
u_art_parse.add_argument('title')
u_art_parse.add_argument('content')
u_art_parse.add_argument('image_file')

class UserApi(Resource):
    def get(self, username):
        user = User.query.filter_by(username = username).first()
        if user:
            return {"firstname": user.firstname, "lastname": user.lastname, "image_file": user.image_file, "username": username}
        else:
            {"Error": "Something went wrong"}, 400

    def put(self, username):
        user = User.query.filter_by(username = username).first()
        if not user:
            {"Error": "Something went wrong"}, 400

        val = c_use_parse.parse_args()
        firstname = val.get("firstname", None)
        lastname = val.get("lastname", None)
        username = val.get("username", None)

        user.firstname = firstname
        user.lastname = lastname
        user.username = username

        db.session.add(user)
        db.session.commit()

        return {"firstname": user.firstname, "lastname": user.lastname, "password": user.password, "username": username}

    def delete(self, username):
        user = User.query.filter_by(username = username).first()
        if not user:
            return {"Error": "Something went wrong"}, 400

        db.session.delete(user)
        db.session.commit()

        return "The user has been deleted"
        
    def post(self):
        val = c_use_parse.parse_args()
        firstname = val.get("firstname", None)
        lastname = val.get("lastname", None)
        username = val.get("username", None)
        password = val.get("password", None)
        image_file = val.get("image_file", None)

        user = db.session.query(User).filter_by(username = username).first()
        if user:
            return {"Error": "Something went wrong"}, 400

        new = User(firstname = firstname, lastname = lastname, username = username, password = password, image_file = image_file)
        db.session.add(new)
        db.session.commit()
        return {"firstname": new.firstname, "lastname": new.lastname, "password": new.password, "username": username}

api.add_resource(UserApi, '/users/<string:username>', '/users')
    
class ArticleApi(Resource):
    def get(self, id):
        article = Article.query.filter_by(id = id).first()
        if article:
            return {"id" : id, "title": article.title, "content": article.content, "image_file": article.image_file, "date_posted" : article.date_posted}
        else:
            {"Error": "Something went wrong"}, 400

    def put(self, id):
        article = Article.query.filter_by(id = id).first()
        if not article:
            {"Error": "Something went wrong"}, 400

        val = u_art_parse.parse_args()
        title = val.get("title", None)
        content = val.get("content", None)
        image_file = val.get("image_file", None)

        article.title = title
        article.content = content
        article.image_file = image_file

        db.session.add(article)
        db.session.commit()

        return {"id" : id, "title": article.title, "content": article.content, "image_file": article.image_file, "date_posted" : article.date_posted}

    def delete(self, id):
        user = Article.query.filter_by(id = id).first()
        if not user:
            return {"Error": "Something went wrong"}, 400

        db.session.delete(user)
        db.session.commit()

        return "The blog has been deleted"
        
    def post(self):
        val = c_art_parse.parse_args()
        title = val.get("title", None)
        content = val.get("content", None)
        image_file = val.get("image_file", None)

        user = db.session.query(Article).filter_by(id = id).first()
        if user:
            return {"Error": "Something went wrong"}, 400

        new = Article(title = title, content = content, image_file = image_file, user_id = 0)
        db.session.add(new)
        db.session.commit()
        return {"id" : id, "title": new.title, "content": new.content, "image_file": new.image_file, "date_posted" : new.date_posted}

api.add_resource(ArticleApi, '/blog/<int:id>', '/blog')
    

#########################################################################################################################

# User Database Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.Text, unique=True, nullable=False)

class Article(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_file = db.Column(db.Text, unique=True, nullable=False)
    like_count = db.Column(db.Integer, nullable=False, default=0)
    authors = db.relationship("User", secondary = "article_authors")

class ArticleAuthors(db.Model, UserMixin):
    __tablename__ = 'article_authors'
    user_id = db.Column(db.Integer,   db.ForeignKey("user.id"), primary_key=True, nullable=False)
    article_id = db.Column(db.Integer,  db.ForeignKey("article.id"), primary_key=True, nullable=False) 

class Follow(db.Model, UserMixin):
    __tablename__ = 'follow'
    followed_by_id = db.Column(db.Integer,   db.ForeignKey("user.id"), primary_key=True, nullable=False)
    followed_id = db.Column(db.Integer,  db.ForeignKey("user.id"), primary_key=True, nullable=False)

class Like(db.Model, UserMixin):
    __tablename__ = 'like'
    user_id = db.Column(db.Integer,   db.ForeignKey("user.id"), primary_key=True, nullable=False)
    article_id = db.Column(db.Integer,  db.ForeignKey("article.id"), primary_key=True, nullable=False)

#########################################################################################################################

class RegisterForm(FlaskForm):
    firstname = StringField(validators=[
                           InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "First Name"})    

    lastname = StringField(validators=[
                           InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Last Name"})  
    
    photo = FileField(validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])

    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

class AddBlog(FlaskForm):
    title = StringField(validators=[
                           InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Title"})
    content = StringField(validators=[
                            InputRequired()], render_kw={"placeholder": "Content"})
    photo = FileField(validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
                           
    submit = SubmitField('Upload')

class SearchUser(FlaskForm):
    search_content = StringField(validators=[
                        InputRequired()], render_kw={"placeholder": "Search for User"})
    submit = SubmitField('Search')

class EditProfileForm(FlaskForm):
    firstname = StringField(validators=[
                           InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "First Name"})
    lastname = StringField(validators=[
                           InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Last Name"})
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    submit = SubmitField('Update')                      


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', form=form, info = "Password incorrect!")
        else:
            return render_template('login.html', form=form, info = "Username doesn't exist!")

        
    return render_template('login.html', form=form, info = "")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    existing_username = User.query.filter_by(username = form.username.data).first()

    if existing_username:
        return render_template('register.html', form=form, info = "This username already exists")

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        new_url = file_url.rsplit('/', 1)[-1]
        new_user = User(username=form.username.data, password=hashed_password, firstname = form.firstname.data , lastname = form.lastname.data, image_file = new_url)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
        
    return render_template('register.html', form=form, info = "")

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    articles = Article.query.join(Follow, Follow.followed_id == Article.user_id ).filter(Follow.followed_by_id == current_user.id).order_by(Article.date_posted.desc())

    liked = Like.query.filter_by(user_id = current_user.id)
    flag_list = [r.article_id for r in liked]

    return render_template('dashboard.html', your_name = current_user.firstname, articles = articles, flag_list = flag_list)

@app.route('/like/<article_id>', methods=['GET', 'POST'])
@login_required
def like(article_id):
    article = Article.query.filter_by(id = article_id).first()

    try:
        new_like = Like(user_id=current_user.id,article_id = article_id)
        db.session.add(new_like)
        db.session.commit()

        article.like_count += 1

        db.session.add(article)
        db.session.commit()

        flash("Article liked!")

        return redirect(url_for('dashboard'))

    except:
        flash("Something went wrong. Try again!")

        return redirect(url_for('dashboard'))

@app.route('/unlike/<article_id>', methods=['GET', 'POST'])
@login_required
def unlike(article_id):
    article = Article.query.filter_by(id = article_id).first()
    existing_like = Like.query.filter_by(user_id=current_user.id,article_id = article_id).first()
    
    try:
        db.session.delete(existing_like)
        db.session.commit()

        article.like_count -= 1

        db.session.add(article)
        db.session.commit()

        flash("Article unliked!")

        return redirect(url_for('dashboard'))

    except:
        flash("Something went wrong. Try again!")

        return redirect(url_for('dashboard'))

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_viewer(username):
    user = User.query.filter_by(username = username).first()
    articles = Article.query.filter(Article.authors.any(username = username))
    post_count = Article.query.filter(Article.authors.any(username=user.username)).count()
    following_count = Follow.query.filter_by(followed_by_id = user.id).count()
    follower_count = Follow.query.filter_by(followed_id = user.id).count()

    flag = False
    existing_follow = Follow.query.filter_by(followed_by_id=current_user.id,followed_id = user.id).first()
    if existing_follow:
        flag = True
    
    return render_template('user.html', articles = articles, user = user, post_count = post_count, flag = flag, username = username, follower_count = follower_count, following_count = following_count)

@app.route('/user/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow_user(username):
    user = User.query.filter_by(username = username).first()
    
    try:
        new_follow = Follow(followed_by_id=current_user.id,followed_id = user.id)
        db.session.add(new_follow)
        db.session.commit()

        flash("User followed!")

        return redirect(url_for('user_viewer', username = username))

    except:
        flash("Something went wrong. Try again!")

        return redirect(url_for('user_viewer', username = username))

@app.route('/user/unfollow/<username>', methods=['GET', 'POST'])
@login_required
def unfollow_user(username):
    user = User.query.filter_by(username = username).first()
    existing_follow = Follow.query.filter_by(followed_by_id=current_user.id,followed_id = user.id).first()

    try:
        db.session.delete(existing_follow)
        db.session.commit()

        flash("User unfollowed!")
      
        return redirect(url_for('user_viewer', username = username))

    except:

        flash("Something went wrong. Try again!")

        return redirect(url_for('user_viewer', username = username))
    

@app.route('/blog/delete/<int:article_id>', methods=['GET', 'POST'])
@login_required
def delete_blog(article_id):
    to_delete = Article.query.filter_by(id = article_id).first()
    
    try:
        os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], to_delete.image_file))
        db.session.delete(to_delete)
        db.session.commit()

        flash("Post has been deleted")
      
        return redirect(url_for('my_profile'))

    except:

        flash("Something went wrong. Try again!")

        return redirect(url_for('my_profile'))


@app.route('/blog/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(article_id):
    to_edit = Article.query.filter_by(id = article_id).first()
    form = AddBlog()
    if form.validate_on_submit():
        os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], to_edit.image_file))
        to_edit.title = form.title.data
        to_edit.content = form.content.data
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        new_url = file_url.rsplit('/', 1)[-1]
        to_edit.image_file = new_url
 
        db.session.add(to_edit)
        db.session.commit()

        return redirect(url_for('my_profile'))
    
    form.title.data= to_edit.title
    form.content.data = to_edit.content

    return render_template('edit_blog.html', form=form)
    

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    query  = request.args.get('query')
    
    if query:
        users = User.query.filter(User.username.contains(query) | User.firstname.contains(query) | User.lastname.contains(query))
    else:
        users  = User.query.all()
            
    return render_template('search.html', your_name = current_user.firstname, users = users)

@app.route('/my_profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    if request.method == "GET":        
        articles = Article.query.filter(Article.authors.any(username=current_user.username))
        post_count = Article.query.filter(Article.authors.any(username=current_user.username)).count()
        following_count = Follow.query.filter_by(followed_by_id = current_user.id).count()
        follower_count = Follow.query.filter_by(followed_id = current_user.id).count()
        return render_template('my_profile.html', articles=articles, user = current_user,  post_count = post_count, following_count = following_count, follower_count = follower_count)

@app.route('/my_profile/my_followers', methods=['GET', 'POST'])
@login_required
def my_followers():     
    followers = User.query.join(Follow, Follow.followed_by_id == User.id).filter(Follow.followed_id == current_user.id).filter(Follow.followed_by_id != current_user.id)
        
    return render_template('my_followers.html', followers = followers)

@app.route('/my_profile/my_following', methods=['GET', 'POST'])
@login_required
def my_following():     
    following = User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.followed_by_id == current_user.id)
        
    return render_template('my_following.html', following = following)


@app.route('/my_profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    my_old = User.query.filter_by(id = current_user.id).first()  
    form = EditProfileForm()
    existing_username = User.query.filter_by(username = form.username.data).first()

    if existing_username and form.username.data != current_user.username:
        return render_template('edit_profile.html', form=form, info = "This username already exists")

    if form.validate_on_submit():
        my_old.firstname = form.firstname.data
        my_old.lastname = form.lastname.data
        my_old.username = form.username.data

        db.session.add(my_old)
        db.session.commit()

        return redirect(url_for('my_profile'))

    if request.method == 'GET':
        form.firstname.data = my_old.firstname
        form.lastname.data = my_old.lastname
        form.username.data =  my_old.username
        
    return render_template('edit_profile.html', form=form)


@app.route('/my_profile/delete', methods=['GET', 'POST'])
@login_required
def delete_profile():
    user_to_delete = User.query.filter_by(id = current_user.id).first()
    articles_to_delete = Article.query.filter_by(user_id=current_user.id).all()
    article_images = [r.image_file for r in articles_to_delete]
    following_to_delete = db.session.query(Follow).filter_by(followed_by_id=current_user.id).all()
    following_ids = [r.followed_by_id for r in following_to_delete]
    follower_to_delete = db.session.query(Follow).filter_by(followed_id=current_user.id).all()
    follower_ids = [r.followed_id for r in follower_to_delete]
    
    try:
        if articles_to_delete:
            for image in article_images:
                os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], image))
                article = Article.query.filter_by(image_file = image).first()
                db.session.delete(article)
                db.session.commit()
        
        if following_to_delete:
            for follow in following_ids:
                thing = Follow.query.filter_by(followed_by_id=follow).first()
                db.session.delete(thing)
                db.session.commit()
        
        if follower_to_delete:
            for follow in follower_ids:
                thing = Follow.query.filter_by(followed_id=follow).first()
                db.session.delete(thing)
                db.session.commit()

        os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], user_to_delete.image_file))
        db.session.delete(user_to_delete)
        db.session.commit()

        flash("Post has been deleted")
      
        return redirect(url_for('home'))

    except:

        print("Something went wrong. Try again!")

        return redirect(url_for('my_profile'))

    


@app.route('/add_blog', methods=['GET', 'POST'])
@login_required
def add_blog():
    form = AddBlog()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        new_url = file_url.rsplit('/', 1)[-1]
        post = Article(title=form.title.data, content=form.content.data , image_file = new_url , user_id=current_user.id)  
        db.session.add(post)
        db.session.commit()

        to_find_id = Article.query.filter_by(image_file = new_url).first()
        article_author = ArticleAuthors(user_id = current_user.id, article_id = to_find_id.id)
        db.session.add(article_author)
        db.session.commit()
        
        return redirect(url_for('dashboard'))
    else:
        file_url = None
    
    user = current_user
    the_name = user.firstname
    return render_template('add_blog.html', form=form, file_url=file_url)

if __name__ == "__main__":
    app.run(debug=True)