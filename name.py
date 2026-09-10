from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from flask_argon2 import Argon2
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KLUCZ!KLUCZ!KLUCZ!KLUCZ'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
db = SQLAlchemy(app)
db.app = app
login_manager = LoginManager()
login_manager.init_app(app)
argon2 = Argon2(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password = db.Column(db.String(512), nullable=False)
    uploaded_images = db.relationship('Image', backref='user')

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))
    date_uploaded = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String(1024))
    def __repr__(self):
        return 'Image ' + self.filename

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=['POST'])
def register():
    username = request.form["username"]
    password = request.form["password"]
    if username == '' or password == '':
        return redirect(url_for('main_gallery'))
    hashed = argon2.generate_password_hash(password)
    new_user = User(username=username,password=hashed)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('main_gallery'))

@app.route("/login", methods=['POST'])
def login():
    login_username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=login_username).scalar()
    if user is None:
        return "no user"
    if argon2.check_password_hash(user.password,password):
        login_user(user)
    return redirect(url_for('main_gallery'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_gallery'))    

@app.route("/")
def main_gallery():
    select_command = db.select(Image.filename, Image.date_uploaded, User.username).select_from(Image).join(User)
    images = db.session.execute(select_command).all()
    return render_template('home.html', images=images)

@app.route("/upload_error")
def upload_error():
    return render_template('home.html', images=Image.query.all())

@app.route("/login_register")
def login_register_screen():
    return render_template('login.html')

@app.route("/upload", methods=['GET','POST'])
def upload_screen():
    if request.method == 'POST':
        uploaded = request.files['file']
        if uploaded.filename == "":
            return redirect(url_for('upload_error'))
        new_filename = secure_filename(uploaded.filename)
        uploaded.save('static/uploaded/' + new_filename)
        db.session.add(Image(filename="uploaded/"+new_filename, description=request.form['desc'], uploaded_by=current_user.id))
        db.session.commit()
        return redirect(url_for('main_gallery'))
    return render_template('upload.html', images=Image.query.all())

@app.route("/search", methods=['GET'])
def show_results():
    word = request.args.get('word')
    if word == "":
         return redirect(url_for('main_gallery'))
    select_command = db.select(Image.filename, Image.date_uploaded, User.username, Image.description).select_from(Image).join(User).filter(Image.description.like("%"+word+"%"))
    result = db.session.execute(select_command).all()
    return render_template('home.html', images=result)

@app.route("/<name>")
def user_gallery(name):
    user = User.query.filter_by(username=name).scalar()
    if user is None:
        return "User doesn't exist"
    return render_template('profile.html', images=Image.query.filter_by(uploaded_by=user.id).all(),username=user.username)

if __name__ == "__main__":
    app.run(debug=True)
