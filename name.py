from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
db = SQLAlchemy(app)
db.app = app

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))
    date_uploaded = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    description = db.Column(db.String(1024))
    def __repr__(self):
        return 'Image ' + self.filename
with app.app_context():
    db.create_all()

@app.route("/")
def placeholder():
    return render_template('home.html', images=Image.query.all())

@app.route("/upload", methods=['GET','POST'])
def upload_screen():
    if request.method == 'POST':
        uploaded = request.files['file']
        if uploaded.filename == "":
            return redirect(url_for('placeholder'))
        new_filename = secure_filename(uploaded.filename)
        uploaded.save('static/uploaded/' + new_filename)
        db.session.add(Image(filename="uploaded/"+new_filename,description=request.form['desc']))
        db.session.commit()
        return redirect(url_for('placeholder'))
    return render_template('upload.html', images=Image.query.all())

@app.route("/search", methods=['GET'])
def show_results():
    word = request.args.get('word')
    if word == "":
         return redirect(url_for('placeholder'))
    return render_template('home.html', images=Image.query.filter(Image.description.like("%"+word+"%")).all())

if __name__ == "__main__":
    app.run(debug=True)
