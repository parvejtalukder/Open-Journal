import os
import uuid
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import error, login_required
from werkzeug.utils import secure_filename
from functools import wraps

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

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    return rows[0] if rows else None

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user["role"] not in roles:
                return redirect("/dashboard")  
            return f(*args, **kwargs)
        return wrapper
    return decorator

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
            return error("Must provide username!", 403)

        elif not request.form.get("password"):
            return error("Must provide password!", 403)

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return error("Invalid username or password!", 403)

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
            return error("Only PNG, JPG, JPEG, WEBP allowed!")
    
        extension = original_name.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4()}.{extension}"
        file_location = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(file_location)
        
        hash = generate_password_hash(password)

        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(existing_user) != 0:
            return error("Username already taken!")
        
        existing_email = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(existing_email) != 0:
            return error("Email already registered!")


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
            return error("Username already exists")

    else: 
        return render_template("register.html")
    

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    curr_user = get_current_user();
    if curr_user["role"] == "admin":
        return render_template("dashboard/admin.html", user=curr_user, show_cards=True)
    
    if curr_user["role"] == "author":
        return render_template("dashboard/author.html", user=curr_user, show_cards=True)
    
    if curr_user["role"] == "reader":
        return render_template("dashboard/reader.html", user=curr_user, show_cards=True)

    return render_template("dashboard.html", user=get_current_user())

@app.route("/dashboard/overview", methods=["GET", "POST"])
@login_required
@role_required("admin",)
def overview_admin():
    curr_user = get_current_user();
    # url_path = request.base_url();

    user_list = db.execute(
        "SELECT * FROM users;")
    user_len = len(user_list)

    admin_list = db.execute(
        "SELECT * FROM users WHERE role = ?", "admin")
    admin_len= len(admin_list)

    author_list = db.execute(
        "SELECT * FROM users WHERE role = ?", "author")
    author_len= len(author_list)

    reader_list = db.execute(
        "SELECT * FROM users WHERE role = ?", "reader")
    reader_len= len(reader_list)

    return render_template("dashboard/admin/overview.html", user=curr_user, user_count=user_len, admin_count=admin_len, author_cout=author_len, reader_count=reader_len)

@app.route("/dashboard/posts", methods=["GET", "POST"])
@login_required
@role_required("admin", "author")
def overview_posts():

    page = request.args.get("page", 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    posts = db.execute("""
        SELECT posts.*, users.name AS author_name
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
        LIMIT ? OFFSET ?
    """, per_page, offset)

    total = db.execute("SELECT COUNT(*) as count FROM posts")[0]["count"]
    next = total > page * per_page
    prev = page > 1
    post_count = len(posts);

    return render_template("dashboard/posts/posts.html", user=get_current_user(), next=next, prev=prev, posts=posts, page=page, posts_count=post_count)

@app.route("/dashboard/posts/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "author")
def overview_posts_create():

    if request.method == "POST":

        title = request.form.get("title")
        category = request.form.get("category")
        status = "draft"
        image = request.files.get("image")
        author = session["user_id"]
        content = request.form.get("content")

        if not title:
            return error("Must have a title!")
        
        if not category:
            return error("Must have a category!")
        
        if not content:
            return error("Must have content!")
        # if not status:
            # return error("Only PNG, JPG, JPEG, WEBP allowed!")

        original_name = secure_filename(image.filename)
        if not allowed_file(original_name):
            return error("Upload a file or valid file!")
    
        extension = original_name.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4()}.{extension}"
        file_location = os.path.join(UPLOAD_FOLDER, filename)
        image.save(file_location)

        db.execute(
            """
            INSERT INTO posts (user_id, title, content, image, category)
            VALUES (?, ?, ?, ?, ?)
            """,
        author, title, content, filename, category
        )
        flash("Post created successfully!")
        return redirect("/dashboard/posts")
    else:
        return render_template("dashboard/posts/create.html", user=get_current_user())


@app.route("/news", methods=["GET", "POST"])
def news():

    post_id = request.args.get("p")  

    post = db.execute(
        """
            SELECT posts.*, users.name AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.id = ?
        """, (post_id,))

    # post = {
    #     "id": post_id,
    #     "title": "AI Changing the Future of Bangladesh",
    #     "paragraph": "Artificial Intelligence is rapidly transforming industries in Bangladesh, from agriculture to fintech. Experts believe this shift will create new opportunities while also challenging traditional job sectors.",
    #     "image": "https://en.kavyakishor.com/wp-content/uploads/2024/12/Screenshot-2024-12-07-11.46.53-AM.png",
    #     "author": "Parvej H. Talukder",
    #     "date": "2 April 2026",
    #     "category": "Tech",
    #     "quote": "Technology will not replace humans, but humans who use technology will replace those who don’t."
    # }

    return render_template("/post.html", post = post[0] if post else None)

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

@app.errorhandler(404)
def page_not_found(e):
    return error("Page not found!")

app.config["DEBUG"] = True