from functools import wraps
from logging import raiseExceptions
import re
from django.shortcuts import render
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask.templating import render_template_string
from flask.wrappers import Request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField, form, meta,validators
from passlib.hash import sha256_crypt
import os
from flask import Flask, render_template, request, redirect, abort, flash, url_for
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Kullanıcı Kayıt Formu
class ContactForm(Form):

    name = StringField("İsminiz",validators = [validators.length(min = 4,max= 16)])
    email = StringField("Email Adresi",validators = [validators.Email(message="Lütfen Geçerli Bir Email Adresi Giriniz")])
    message = TextAreaField("Mesajınız")

app = Flask(__name__)
app.secret_key = "myblogsite"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "myblogsite"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/")

def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/myworks")
def works():
    return render_template("myworks.html")
    
@app.route("/contact", methods = ["GET" , "POST"])
def contact():
    form = ContactForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        cursor = mysql.connection.cursor()
        
        sorgu = "Insert into messages(name,email,message) Values(%s,%s,%s)"
        cursor.execute(sorgu,(name,email,message))
        mysql.connection.commit()
        cursor.close()

        flash("Mesajınız iletildi. En kısa zamanda size dönüş yapılacaktır." , "success")

        return redirect(url_for("index"))
    else:
        return render_template("contact.html", form=form)


@app.route("/articles")
def articles():
    return render_template("articles.html")

if __name__ == "__main__":
    app.run(debug=True)
