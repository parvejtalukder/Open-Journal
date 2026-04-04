import os
import uuid
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import error, login_required
from werkzeug.utils import secure_filename
from functools import wraps
from flask import jsonify

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

    posts = db.execute(
        """
            SELECT posts.*, users.name AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
            LIMIT ?
        """, (4,))
    
    news = db.execute(
        """
            SELECT posts.*, users.username AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = "news"
            ORDER BY posts.created_at DESC
            LIMIT ?
        """, (2,)
        )
    
    entertainment = db.execute(
        """
            SELECT posts.*, users.username AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = "entertainment"
            ORDER BY posts.created_at DESC
            LIMIT ?
        """, (4,)
        )
    
    tech = db.execute(
        """
            SELECT posts.*, users.username AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = "tech"
            ORDER BY posts.created_at DESC
            LIMIT ?
        """, (4,)
        )
    
    sports = db.execute(
        """
            SELECT posts.*, users.username AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = "sports"
            ORDER BY posts.created_at DESC
            LIMIT ?
        """, (2,)
        )
    
    opinions = db.execute(
        """
            SELECT posts.*, users.username AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = "opinion"
            ORDER BY posts.created_at DESC
            LIMIT ?
        """, (2,)
        )
    
    lasts = db.execute(
        """
            SELECT posts.*, users.username AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
            LIMIT ?
        """, (3,)
        )

    return render_template("index.html", posts=posts, newses=news, entertainments=entertainment, techs=tech, sports=sports, opinions=opinions, lasts=lasts)

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

@app.route("/dashboard/be-author", methods=["GET", "POST"])
@login_required
@role_required("reader")
def be_author():

    if request.method == "POST":

        user_id = session["user_id"]
        message = request.form.get("message")
        status = "pending"

        db.execute(
            """
            INSERT INTO applications (user_id, message, status)
            VALUES (?, ?, ?)
            """,
            user_id, message, status
        )

        flash("Application Sent!")
        return redirect("/dashboard")

    else:

        result = db.execute(
            "SELECT status FROM applications WHERE user_id = ?",
            (session["user_id"])
        )

        status = result[0]["status"] if result else None

        return render_template("dashboard/reader/applicationauthor.html", user=get_current_user(), status=status)
    
@app.route("/dashboard/applications", methods=["GET", "POST"])
@login_required
@role_required("admin")
def overview_application():

    applications = db.execute(
    """
        SELECT applications.*, users.username
        FROM applications
        JOIN users ON applications.user_id = users.id
        WHERE applications.status = 'pending'
    """
    )
    applications_count = db.execute("SELECT COUNT(*) AS total FROM applications WHERE status = 'pending'")[0]["total"]

    return render_template("dashboard/admin/applications.html", user=get_current_user(), applications=applications, applications_count=applications_count)


@app.route("/dashboard/applications/edit/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def update_application(id):

    status = request.form.get("status")

    db.execute(
        "UPDATE applications SET status = ? WHERE id = ?",
        status, id
    )

    if status == "approved":
        user = db.execute(
            "SELECT user_id FROM applications WHERE id = ?",
            id
        )[0]

        db.execute(
            "UPDATE users SET role = 'author' WHERE id = ?",
            user["user_id"]
        )

    flash("Application updated!")
    return redirect("/dashboard/applications")


@app.route("/dashboard/overview", methods=["GET", "POST"])
@login_required
@role_required("admin")
def overview_admin():
    curr_user = get_current_user();
    # url_path = request.base_url();

    user_list = db.execute(
        "SELECT * FROM users WHERE is_active = 1;")
    user_len = len(user_list)

    admin_list = db.execute(
        "SELECT * FROM users WHERE is_active = 1 AND users.role = ?", "admin")
    admin_len= len(admin_list)

    author_list = db.execute(
        "SELECT * FROM users WHERE is_active = 1 AND users.role = ?", "author")
    author_len= len(author_list)

    reader_list = db.execute(
        "SELECT * FROM users WHERE is_active = 1 AND users.role = ?", "reader")
    reader_len= len(reader_list)

    result = db.execute("SELECT COUNT(*) AS total FROM posts")
    posts_count = result[0]["total"]

    fb_page = request.args.get("fb_page", 1, type=int)
    fb_per_page = 3
    fb_offset = (fb_page - 1) * fb_per_page

    feedbacks = db.execute( 
        """
            SELECT feedback.*, users.username
            FROM feedback
            JOIN users ON feedback.user_id = users.id
            ORDER BY feedback.created_at DESC
            LIMIT ? OFFSET ?
        """, fb_per_page, fb_offset)
    
    fb_total = db.execute(
    "SELECT COUNT(*) as count FROM feedback"
    )[0]["count"]

    fb_next = fb_total > fb_page * fb_per_page
    fb_prev = fb_page > 1

    appli_count = db.execute("SELECT COUNT(*) AS total FROM applications")[0]["total"]
    appli_active = db.execute("SELECT COUNT(*) AS total FROM applications WHERE applications.status = 'pending'")[0]["total"]
    feedback_count = db.execute("SELECT COUNT (*) AS total FROM feedback")[0]["total"]

    return render_template("dashboard/admin/overview.html", user=curr_user, user_count=user_len, admin_count=admin_len, author_count=author_len, reader_count=reader_len, posts_count=posts_count, appli_count=appli_count, feedback_count=feedback_count,feedbacks=feedbacks, fb_next=fb_next, fb_prev=fb_prev, fb_page=fb_page,appli_active=appli_active,)

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

    user = get_current_user()
    if user["role"] == "author":

        posts = db.execute("""
                SELECT posts.*, users.name AS author_name
                FROM posts
                JOIN users ON posts.user_id = users.id
                WHERE posts.user_id = ?
                ORDER BY posts.created_at DESC
                LIMIT ? OFFSET ?
        """, session["user_id"], per_page, offset)
        post_count = len(posts);
    
        return render_template("dashboard/posts/posts.html", user=get_current_user(), next=next, prev=prev, posts=posts, page=page, posts_count=post_count)

    else:
        return render_template("dashboard/posts/posts.html", user=get_current_user(), next=next, prev=prev, posts=posts, page=page, posts_count=total)
    
@app.route("/dashboard/my-posts", methods=["GET", "POST"])
@login_required
@role_required("admin")
def overview_my_posts():

    page = request.args.get("page", 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    posts = db.execute("""
                SELECT posts.*, users.name AS author_name
                FROM posts
                JOIN users ON posts.user_id = users.id
                WHERE posts.user_id = ?
                ORDER BY posts.created_at DESC
                LIMIT ? OFFSET ?
        """, session["user_id"], per_page, offset)

    total = db.execute("SELECT COUNT(*) as count FROM posts WHERE posts.user_id = ? ", (session["user_id"]))[0]["count"]
    next = total > page * per_page
    prev = page > 1
    post_count = total

    return render_template("dashboard/posts/myposts.html", user=get_current_user(), next=next, prev=prev, posts=posts, page=page, posts_count=post_count)
    


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
        """, (post_id))

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

@app.route("/category/<string:name>")
def category(name):
    page = request.args.get("page", 1, type=int)
    per_page = 3

    offset = (page - 1) * per_page

    posts = db.execute(
        "SELECT * FROM posts WHERE category = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
        name, per_page, offset
    )

    total = db.execute(
        "SELECT COUNT(*) as count FROM posts WHERE category = ?",
        name
    )[0]["count"]

    next = offset + per_page < total

    return render_template("category.html", posts=posts, name=name, page=page, next=next)

@app.route("/posts")
def all_posts():
    page = request.args.get("page", 1, type=int)
    per_page = 6

    offset = (page - 1) * per_page

    posts = db.execute(
        "SELECT * FROM posts ORDER BY created_at DESC LIMIT ? OFFSET ?",
        per_page, offset
    )

    total = db.execute(
        "SELECT COUNT(*) as count FROM posts"
    )[0]["count"]

    next = offset + per_page < total

    return render_template( "/posts.html", posts=posts, page=page, next=next)


@app.route("/dashboard/reset-password", methods=["GET", "POST"])
@login_required
@role_required("admin", "author", "reader")
def reset_password():

    if request.method == "POST":
        
        password = request.form.get("password")
        if not password:
            flash("All fields are required")
            return redirect("/dashboard/reset-password")
        
        new_hash = generate_password_hash(password)

        db.execute("""
            UPDATE users
            SET hash = ?
            WHERE id = ?
        """, new_hash, session["user_id"])

        flash("Password updated successfully!")
        return redirect("/dashboard")

    return render_template("dashboard/resetpass.html", user=get_current_user())


@app.route("/dashboard/feedback", methods=["GET", "POST"])
@login_required
def feedback():

    if request.method == "POST":

        subject = request.form.get("subject")
        message = request.form.get("message")
        user_id = session["user_id"]

        if not message:
            flash("Message is required")
            return redirect("/dashboard/feedback")

        db.execute("""
            INSERT INTO feedback (user_id, subject, message)
            VALUES (?, ?, ?)
        """, user_id, subject, message)

        flash("Feedback sent successfully!")
        return redirect("/dashboard")

    return render_template("dashboard/sendfeedback.html", user=get_current_user())

@app.route("/dashboard/profile")
@login_required
def profile():
    return render_template("dashboard/profile.html", user=get_current_user())

@app.route("/dashboard/users")
@login_required
@role_required("admin")
def users_overview():

    page = request.args.get("page", 1, type=int)
    per_page = 3
    offset = (page - 1) * per_page

    users = db.execute("""
        SELECT * FROM users
        WHERE is_active = 1
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """, per_page, offset)

    total = db.execute("SELECT COUNT(*) AS count FROM users WHERE is_active = 1")[0]["count"]

    next = offset + per_page < total
    prev = page > 1

    return render_template( "dashboard/admin/users.html", user=get_current_user(), users=users, users_count=total, page=page, next=next, prev=prev)


@app.route("/author/<int:user_id>")
def public_author(user_id):

    page = request.args.get("page", 1, type=int)
    per_page = 3
    offset = (page - 1) * per_page

    author = db.execute(
        "SELECT * FROM users WHERE id = ?",
        user_id
    )

    if not author:
        return error("Author not found!")

    posts = db.execute("""
        SELECT * FROM posts
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, user_id, per_page, offset)

    total = db.execute(
        "SELECT COUNT(*) as count FROM posts WHERE user_id = ?",
        user_id
    )[0]["count"]

    next = total > page * per_page
    prev = page > 1

    return render_template( "profile.html", author=author[0], posts=posts, page=page, next=next, prev=prev)

@app.route("/dashboard/user/delete/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_user(user_id):

    role = db.execute("SELECT role FROM users WHERE users.id = ?", user_id)[0]["role"]

    if role in ["admin", "author"]:
        flash("You cannot delete admin or author accounts.")
        return redirect("/dashboard/users")
    
    else:
        db.execute("UPDATE users SET is_active = 0 WHERE id = ?", user_id)

    flash("User deleted successfully!")
    return redirect("/dashboard/users")

@app.route("/dashboard/posts/delete/<int:post_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_post(post_id):
    db.execute("DELETE FROM posts WHERE id = ?", post_id)
    flash("Post deleted successfully!")
    return redirect("/dashboard/posts")

@app.route("/dashboard/posts/edit/<int:post_id>", methods=["POST"])
@login_required
@role_required("admin", "author")
def edit_post(post_id):
    title = request.form.get("title")
    category = request.form.get("category")
    content = request.form.get("content")

    image = request.files.get("image")

    if image and image.filename != "":
        file_loc = os.path.join("static/uploads", image.filename)
        image.save(file_loc)

        db.execute("""
            UPDATE posts
            SET title = ?, category = ?, content = ?, image = ?
            WHERE id = ?
        """, title, category, content, file_loc, post_id)
    else:
        db.execute("""
            UPDATE posts
            SET title = ?, category = ?, content = ?
            WHERE id = ?
        """, title, category, content, post_id)
    
    flash("Post edited successfully!")
    return redirect("/dashboard/posts")


@app.route("/headlines")
def api_headlines():
    posts = db.execute("SELECT id, title FROM posts ORDER BY created_at DESC LIMIT 5")
    return jsonify(posts)

@app.route("/about")
def about_oj():
    return render_template("about.html")


@app.route("/contact")
def contact_oj():
    return render_template("contact.html")


@app.errorhandler(404)
def page_not_found(e):
    return error("Page not found!")

app.config["DEBUG"] = True