import os
import uuid
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import error, login_required
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)        
      
db = SQL("sqlite:///openjournal.db")

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def after_request(response):

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    posts = [
        {"title": "AI Model Released", "image": "https://en.kavyakishor.com/wp-content/uploads/2024/12/Screenshot-2024-12-07-11.46.53-AM.png"},
        {"title": "Global Event", "image": "https://en.kavyakishor.com/wp-content/uploads/2024/12/Screenshot-2024-12-07-11.46.53-AM.png"},
        {"title": "Sports Win", "image": "https://en.kavyakishor.com/wp-content/uploads/2024/12/Screenshot-2024-12-07-11.46.53-AM.png"},
    ]
    return render_template("index.html", posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return error("must provide username", 403)

        elif not request.form.get("password"):
            return error("must provide password", 403)

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return error("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]

        flash("Logged in successfully!")
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        photo = request.files.get("photo")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not email:
            return error("Must provide an email!")
        
        if not photo:
            return error("Must provide a photo!")
        
        if not username:
            return error("Must provide an username!")
        
        if not name:
            return error("Must provide your name!")

        if not password or not confirmation:
            return error("Must provide a password!")

        if password != confirmation:
            return error("Must two passwords are same!")
        
        original_name = secure_filename(photo.filename)
        if not allowed_file(original_name):
            return error("Only PNG, JPG, JPEG, WEBP allowed")
    
        extension = original_name.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4()}.{extension}"
        file_location = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(file_location)
        
        hash = generate_password_hash(password)

        try:
            db.execute("""
                       INSERT INTO users (name, username, email, hash, photo) 
                       VALUES (?, ?, ?, ?, ?)""", name, username, email, hash, filename)
            user_id = db.execute(
                    "SELECT id FROM users WHERE username = ?",
                    username
                    )[0]["id"]
            session["user_id"] = user_id

            flash("Registered successfully!")
            return redirect("/")

        except: 
            return error("username already exists")

    else: 
        return render_template("register.html")

@app.route("/news", methods=["GET", "POST"])
def news():

    post_id = request.args.get("p")  

    post = {
        "id": post_id,
        "title": "AI Changing the Future of Bangladesh",
        "paragraph": "Artificial Intelligence is rapidly transforming industries in Bangladesh, from agriculture to fintech. Experts believe this shift will create new opportunities while also challenging traditional job sectors.",
        "image": "https://en.kavyakishor.com/wp-content/uploads/2024/12/Screenshot-2024-12-07-11.46.53-AM.png",
        "author": "Parvej H. Talukder",
        "date": "2 April 2026",
        "category": "Tech",
        "quote": "Technology will not replace humans, but humans who use technology will replace those who don’t."
    }

    return render_template("/post.html", post=post)

@app.route("/page", methods=["GET", "POST"])
def page():

    page_id = request.args.get("id")  

    page = {
        "id": page_id,
        "title": "AI Changing the Future of Bangladesh",
        "paragraph": "Artificial Intelligence is rapidly transforming industries in Bangladesh, from agriculture to fintech. Experts believe this shift will create new opportunities while also challenging traditional job sectors.",
        "image": "https://en.kavyakishor.com/wp-content/uploads/2024/12/Screenshot-2024-12-07-11.46.53-AM.png",
        "author": "Parvej H. Talukder",
        "date": "2 April 2026",
        "category": "Tech",
        "quote": "Technology will not replace humans, but humans who use technology will replace those who don’t."
    }

    return render_template("/page.html", page=page)

app.config["DEBUG"] = True