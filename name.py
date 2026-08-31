from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
db = SQLAlchemy(app)
db.app = app

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    content = db.Column(db.String(1000))
    def __repr__(self):
        return 'Message ' + self.content
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))
    def __repr__(self):
        return 'Image ' + self.filename
with app.app_context():
    db.create_all()

@app.route("/", methods=['GET','POST'])
def placeholder():
    if request.method == 'POST':
        uploaded = request.files['file']
        uploaded.save('static/uploaded/' + uploaded.filename)
        db.session.add(Image(filename='static/uploaded/' + uploaded.filename))
        db.session.commit()
        return redirect(url_for('placeholder'))
    return render_template('home.html', images=Image.query.all(),messages=Message.query.all())

if __name__ == "__main__":
    app.run(debug=True)
