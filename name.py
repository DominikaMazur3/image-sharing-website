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
    def __repr__(self):
        return 'Image ' + self.filename
with app.app_context():
    db.create_all()

@app.route("/", methods=['GET','POST'])
def placeholder():
    if request.method == 'POST':
        uploaded = request.files['file']
        new_filename = secure_filename(uploaded.filename)
        uploaded.save('static/uploaded/' + new_filename)
        db.session.add(Image(filename='static/uploaded/' + new_filename))
        db.session.commit()
        return redirect(url_for('placeholder'))
    return render_template('home.html', images=Image.query.all(),messages=Message.query.all())

if __name__ == "__main__":
    app.run(debug=True)
