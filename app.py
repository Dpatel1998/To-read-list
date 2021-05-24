from flask import Flask, url_for, redirect, render_template, request 
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf import FlaskForm
from sqlalchemy.orm import backref 
from wtforms import StringField, SubmitField , DateField
from wtforms.fields.core import IntegerField, SelectField

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = ###
app.config["SECRET_KEY"] = ###
db = SQLAlchemy(app)

class authors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.DateTime, default="1970-01-01")
    gender = db.Column(db.String(10))
    toreads = db.relationship('Toreads',backref='authors')

class AuthorsForm(FlaskForm):
    author = StringField("Author")
    dob = DateField("YYYY-MM-DD") 
    gender = SelectField('Gender',choices=[('Male','Male'),('Female','Female'),('Other','Other')])
    submit = SubmitField("Add Author")

class Toreads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String(50), nullable=False)
    reading = db.Column(db.Boolean, default=False) 
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'),nullable=False)

class ToreadForm(FlaskForm):
    book = StringField("Book")
    Published_date= DateField("Published date")
    submit = SubmitField("Add Toread")
    authors_id = SelectField('Authors',choices=[('unknown','Unknown')])

@app.route("/")
def index():
    all_toreads = Toreads.query.all()
    toreads_string = ""
    all_authors = authors.query.all()
    authors_string = ""
    return render_template("index.html",all_toreads=all_toreads,authors=all_authors)

@app.route("/add", methods=["GET","POST"])
def add():
    form = ToreadForm()
    all_authors = authors.query.all()
    authors_array = [("unknown", "Unknown")]
    for a in all_authors:
        authors_array.append(tuple((a.id, a.author)))
    form.authors_id.choices=authors_array
    if form.validate_on_submit():
        new_toread = Toreads(book=form.book.data,author_id=form.authors_id.data)
        db.session.add(new_toread)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add.html", form=form)

@app.route('/addnewauthor', methods=["GET","POST"])
def add_author():
    form = AuthorsForm()
    if form.validate_on_submit():
        table_1=authors(author=form.author.data,gender=form.gender.data,dob=form.dob.data)
        db.session.add(table_1)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("author.html", form=form)

@app.route("/reading/<int:toread_id>") 
def reading(toread_id):
    toread = Toreads.query.get(toread_id) 
    print (toread)
    tempbook = Toreads.query.filter_by(id=toread_id).first()
    tempbook.reading = True
    

    db.session.commit()
    return redirect(url_for("index"))


@app.route("/not_reading/<int:toread_id>") 
def not_reading(toread_id):
    toread = Toreads.query.get(toread_id) 
    toread.reading = False
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:toread_id>")
def delete(toread_id):
    toread = Toreads.query.get(toread_id)
    db.session.delete(toread)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/update/<int:toread_id>", methods=["GET", "POST"])
def update(toread_id):
    form = ToreadForm()
    all_authors = authors.query.all()
    authors_array = [("unknown", "Unknown")]
    for a in all_authors:
        authors_array.append(tuple((a.id, a.author)))
    form.authors_id.choices=authors_array
    toread_to_be_updated = Toreads.query.get(toread_id)
    if form.validate_on_submit():
        toread_to_be_updated.book = form.book.data
        db.session.commit()
        return redirect(url_for("index"))
    elif request.method == "GET":
        form.book.data = toread_to_be_updated.book 
    return render_template("update.html", form=form)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
