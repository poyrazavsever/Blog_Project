from functools import wraps
from logging import PlaceHolder, raiseExceptions
import re
from unicodedata import name
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
# Login Form
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

# Kullanıcı Kayıt Formu
class RegisterForm(Form):

    name = StringField("İsim Soyisim",validators = [validators.length(min = 4,max= 16)])
    username = StringField("Kullanıcı Adı",validators = [validators.length(min = 5,max= 25)])
    email = StringField("Email Adresi",validators = [validators.Email(message="Lütfen Geçerli Bir Email Adresi Giriniz")])
    password = PasswordField("Parola",validators=[

        validators.DataRequired(message="Lütfen bir parola giriniz"),
        validators.EqualTo(fieldname = "confirm",message = "Parolanız Uyuşmuyor...")
    
    ])
    confirm = PasswordField("Parola Doğrula")

# Contact Form
class ContactForm(Form):

    name = StringField("İsminiz",validators = [validators.length(min = 4,max= 16)])
    email = StringField("Email Adresi",validators = [validators.Email(message="Lütfen Geçerli Bir Email Adresi Giriniz")])
    message = TextAreaField("Mesajınız")

def login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if  not "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Siz zaten giriş yaptınız!","danger")
            return redirect(url_for("index"))
    return decorated_function

def register_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Siz zaten kayıtlısınız!","danger")
            return redirect(url_for("index"))
    return decorated_function

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
#Kayıt olma
@app.route("/register",methods = ["GET","POST"])
@register_req
def register():
    
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():

        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()
        
        sorgu = "Insert into users(name,email,username,password) Values(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()

        flash("Başarıyla Kayıt Oldunuz!" , "success")

        return redirect(url_for("login"))
    else:
        
        return render_template("register.html",form = form)
#Login işlemi
@app.route("/login",methods = ["GET","POST"])
@login_req
def login():
    form = LoginForm(request.form)
    
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        
        sorgu = "SELECT * FROM users WHERE username = %s"
        result = cursor.execute(sorgu,(username,))

        if result > 0 :
            data = cursor.fetchone()
            real_password = data["password"]

            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla giriş yapıldı...","success")

                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("index"))
            else:
                flash("Parolanızı yanlış girdiniz...","danger")
                return redirect(url_for("login"))

        else:
            flash("Böyle bir kullanıcı bulunmuyor...", "danger")
            return redirect(url_for("login"))

        
            


    return render_template("login.html",form = form)
#Çıkış yapma işlemi
@app.route("/logout")
def logout():
    session.clear()
    flash("Çıkış yaptınız.", "success")
    return redirect(url_for("index"))

#Acount Page
@app.route("/acount")
def acount():
    return render_template("acount.html")
    

        
        

if __name__ == "__main__":
    app.run(debug=True)
