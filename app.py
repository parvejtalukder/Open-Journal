import os
import uuid
from functools import wraps

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import error, login_required

app = Flask(__name__)

# Secret key configuration for security
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "openjournal-secret-key-prod-default")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///openjournal.db")

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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
            if not user or user["role"] not in roles:
                flash("Unauthorized access.")
                return redirect("/dashboard")
            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/")
def index():
    posts = db.execute(
        """
            SELECT posts.*, COALESCE(users.name, users.username) AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
            LIMIT 4
        """
    )

    news = db.execute(
        """
            SELECT posts.*, COALESCE(users.name, users.username) AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = 'news'
            ORDER BY posts.created_at DESC
            LIMIT 2
        """
    )

    entertainment = db.execute(
        """
            SELECT posts.*, COALESCE(users.name, users.username) AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = 'entertainment'
            ORDER BY posts.created_at DESC
            LIMIT 4
        """
    )

    tech = db.execute(
        """
            SELECT posts.*, COALESCE(users.name, users.username) AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = 'tech'
            ORDER BY posts.created_at DESC
            LIMIT 4
        """
    )

    sports = db.execute(
        """
            SELECT posts.*, COALESCE(users.name, users.username) AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = 'sports'
            ORDER BY posts.created_at DESC
            LIMIT 2
        """
    )

    opinions = db.execute(
        """
            SELECT posts.*, COALESCE(users.name, users.username) AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.category = 'opinion'
            ORDER BY posts.created_at DESC
            LIMIT 2
        """
    )

    lasts = db.execute(
        """
            SELECT posts.*, COALESCE(users.name, users.username) AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
            LIMIT 3
        """
    )

    return render_template(
        "index.html",
        posts=posts,
        newses=news,
        entertainments=entertainment,
        techs=tech,
        sports=sports,
        opinions=opinions,
        lasts=lasts
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return error("Must provide username!", 403)

        if not password:
            return error("Must provide password!", 403)

        rows = db.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            username
        )

        if not rows or not check_password_hash(rows[0]["hash"], password):
            return error("Invalid username or password!", 403)

        session["user_id"] = rows[0]["id"]
        flash("Logged in successfully!")
        return redirect("/dashboard")
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

        if not name:
            return error("Must provide your name!")
        if not username:
            return error("Must provide a username!")
        if not email:
            return error("Must provide an email!")
        if not password or not confirmation:
            return error("Must provide a password!")
        if password != confirmation:
            return error("Passwords must match!")
        if not photo or photo.filename == "":
            return error("Must provide a profile photo!")

        original_name = secure_filename(photo.filename)
        if not allowed_file(original_name):
            return error("Only PNG, JPG, JPEG, WEBP images allowed!")

        extension = original_name.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4()}.{extension}"
        file_location = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(file_location)

        if db.execute("SELECT 1 FROM users WHERE username = ?", username):
            return error("Username already taken!")

        if db.execute("SELECT 1 FROM users WHERE email = ?", email):
            return error("Email already registered!")

        pwd_hash = generate_password_hash(password)

        try:
            db.execute(
                """
                INSERT INTO users (name, username, email, hash, photo) 
                VALUES (?, ?, ?, ?, ?)
                """,
                name, username, email, pwd_hash, filename
            )
            user_rows = db.execute("SELECT id FROM users WHERE username = ?", username)
            session["user_id"] = user_rows[0]["id"]

            flash("Registered successfully!")
            return redirect("/")
        except Exception:
            return error("Failed to complete registration.")
    else:
        return render_template("register.html")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    curr_user = get_current_user()
    if not curr_user:
        session.clear()
        return redirect("/login")

    if curr_user["role"] == "admin":
        return render_template("dashboard/admin.html", user=curr_user, show_cards=True)

    if curr_user["role"] == "author":
        return render_template("dashboard/author.html", user=curr_user, show_cards=True)

    if curr_user["role"] == "reader":
        return render_template("dashboard/reader.html", user=curr_user, show_cards=True)

    return render_template("dashboard.html", user=curr_user)


@app.route("/dashboard/be-author", methods=["GET", "POST"])
@login_required
@role_required("reader")
def be_author():
    if request.method == "POST":
        user_id = session["user_id"]
        message = request.form.get("message")

        existing = db.execute("SELECT status FROM applications WHERE user_id = ? AND status = 'pending'", user_id)
        if existing:
            flash("You already have a pending application under review.")
            return redirect("/dashboard/be-author")

        db.execute(
            """
            INSERT INTO applications (user_id, message, status)
            VALUES (?, ?, 'pending')
            """,
            user_id, message
        )

        flash("Application sent successfully!")
        return redirect("/dashboard")
    else:
        result = db.execute(
            "SELECT status FROM applications WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            session["user_id"]
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
            ORDER BY applications.created_at DESC
        """
    )
    applications_count = len(applications)

    return render_template(
        "dashboard/admin/applications.html",
        user=get_current_user(),
        applications=applications,
        applications_count=applications_count
    )


@app.route("/dashboard/applications/edit/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def update_application(id):
    status = request.form.get("status")

    if status not in ["approved", "rejected"]:
        flash("Invalid status specified.")
        return redirect("/dashboard/applications")

    db.execute("UPDATE applications SET status = ? WHERE id = ?", status, id)

    if status == "approved":
        user = db.execute("SELECT user_id FROM applications WHERE id = ?", id)
        if user:
            db.execute("UPDATE users SET role = 'author' WHERE id = ?", user[0]["user_id"])

    flash("Application updated successfully!")
    return redirect("/dashboard/applications")


@app.route("/dashboard/overview", methods=["GET", "POST"])
@login_required
@role_required("admin")
def overview_admin():
    curr_user = get_current_user()

    user_list = db.execute("SELECT * FROM users WHERE is_active = 1;")
    user_len = len(user_list)

    admin_list = db.execute("SELECT * FROM users WHERE is_active = 1 AND role = 'admin'")
    admin_len = len(admin_list)

    author_list = db.execute("SELECT * FROM users WHERE is_active = 1 AND role = 'author'")
    author_len = len(author_list)

    reader_list = db.execute("SELECT * FROM users WHERE is_active = 1 AND role = 'reader'")
    reader_len = len(reader_list)

    result = db.execute("SELECT COUNT(*) AS total FROM posts")
    posts_count = result[0]["total"]

    fb_page = max(1, request.args.get("fb_page", 1, type=int) or 1)
    fb_per_page = 3
    fb_offset = (fb_page - 1) * fb_per_page

    feedbacks = db.execute(
        """
            SELECT feedback.*, users.username
            FROM feedback
            JOIN users ON feedback.user_id = users.id
            ORDER BY feedback.created_at DESC
            LIMIT ? OFFSET ?
        """,
        fb_per_page, fb_offset
    )

    fb_total = db.execute("SELECT COUNT(*) as count FROM feedback")[0]["count"]

    fb_next = fb_total > fb_page * fb_per_page
    fb_prev = fb_page > 1

    appli_count = db.execute("SELECT COUNT(*) AS total FROM applications")[0]["total"]
    appli_active = db.execute("SELECT COUNT(*) AS total FROM applications WHERE status = 'pending'")[0]["total"]
    feedback_count = fb_total

    return render_template(
        "dashboard/admin/overview.html",
        user=curr_user,
        user_count=user_len,
        admin_count=admin_len,
        author_count=author_len,
        reader_count=reader_len,
        posts_count=posts_count,
        appli_count=appli_count,
        feedback_count=feedback_count,
        feedbacks=feedbacks,
        fb_next=fb_next,
        fb_prev=fb_prev,
        fb_page=fb_page,
        appli_active=appli_active
    )


@app.route("/dashboard/posts", methods=["GET", "POST"])
@login_required
@role_required("admin", "author")
def overview_posts():
    user = get_current_user()
    page = max(1, request.args.get("page", 1, type=int) or 1)
    per_page = 5
    offset = (page - 1) * per_page

    if user["role"] == "author":
        posts = db.execute(
            """
                SELECT posts.*, users.name AS author_name
                FROM posts
                JOIN users ON posts.user_id = users.id
                WHERE posts.user_id = ?
                ORDER BY posts.created_at DESC
                LIMIT ? OFFSET ?
            """,
            session["user_id"], per_page, offset
        )
        total = db.execute("SELECT COUNT(*) as count FROM posts WHERE user_id = ?", session["user_id"])[0]["count"]
    else:
        posts = db.execute(
            """
                SELECT posts.*, users.name AS author_name
                FROM posts
                JOIN users ON posts.user_id = users.id
                ORDER BY posts.created_at DESC
                LIMIT ? OFFSET ?
            """,
            per_page, offset
        )
        total = db.execute("SELECT COUNT(*) as count FROM posts")[0]["count"]

    next_page = total > page * per_page
    prev_page = page > 1

    return render_template(
        "dashboard/posts/posts.html",
        user=user,
        next=next_page,
        prev=prev_page,
        posts=posts,
        page=page,
        posts_count=total
    )


@app.route("/dashboard/my-posts", methods=["GET", "POST"])
@login_required
@role_required("admin")
def overview_my_posts():
    page = max(1, request.args.get("page", 1, type=int) or 1)
    per_page = 5
    offset = (page - 1) * per_page

    posts = db.execute(
        """
            SELECT posts.*, users.name AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.user_id = ?
            ORDER BY posts.created_at DESC
            LIMIT ? OFFSET ?
        """,
        session["user_id"], per_page, offset
    )

    total = db.execute("SELECT COUNT(*) as count FROM posts WHERE posts.user_id = ?", session["user_id"])[0]["count"]
    next_page = total > page * per_page
    prev_page = page > 1

    return render_template(
        "dashboard/posts/myposts.html",
        user=get_current_user(),
        next=next_page,
        prev=prev_page,
        posts=posts,
        page=page,
        posts_count=total
    )


@app.route("/dashboard/posts/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "author")
def overview_posts_create():
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        image = request.files.get("image")
        author = session["user_id"]
        content = request.form.get("content")

        if not title:
            return error("Must have a title!")
        if not category:
            return error("Must select a category!")
        if not content:
            return error("Must provide post content!")
        if not image or image.filename == "":
            return error("Must upload a valid image!")

        original_name = secure_filename(image.filename)
        if not allowed_file(original_name):
            return error("Only PNG, JPG, JPEG, WEBP images allowed!")

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
    if not post_id:
        return render_template("post.html", post=None)

    posts = db.execute(
        """
            SELECT posts.*, users.name AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.id = ?
        """,
        post_id
    )

    if not posts:
        return render_template("post.html", post=None)

    current_post = posts[0]

    prev_post = db.execute("SELECT id FROM posts WHERE id < ? ORDER BY id DESC LIMIT 1", current_post["id"])
    next_post = db.execute("SELECT id FROM posts WHERE id > ? ORDER BY id ASC LIMIT 1", current_post["id"])

    prev_id = prev_post[0]["id"] if prev_post else None
    next_id = next_post[0]["id"] if next_post else None

    return render_template("post.html", post=current_post, prev_id=prev_id, next_id=next_id)


@app.route("/page", methods=["GET", "POST"])
def page():
    page_id = request.args.get("id")
    page_data = {
        "id": page_id,
        "title": "AI Changing the Future of Bangladesh",
        "paragraph": "Artificial Intelligence is rapidly transforming industries in Bangladesh, from agriculture to fintech. Experts believe this shift will create new opportunities while also challenging traditional job sectors.",
        "image": "https://en.kavyakishor.com/wp-content/uploads/2024/12/Screenshot-2024-12-07-11.46.53-AM.png",
        "author": "Parvej H. Talukder",
        "date": "2 April 2026",
        "category": "Tech",
        "quote": "Technology will not replace humans, but humans who use technology will replace those who don’t."
    }

    return render_template("page.html", page=page_data)


@app.route("/category/<string:name>")
def category(name):
    page = max(1, request.args.get("page", 1, type=int) or 1)
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

    next_page = offset + per_page < total

    return render_template("category.html", posts=posts, name=name, page=page, next=next_page)


@app.route("/posts")
def all_posts():
    page = max(1, request.args.get("page", 1, type=int) or 1)
    per_page = 6
    offset = (page - 1) * per_page

    posts = db.execute(
        "SELECT * FROM posts ORDER BY created_at DESC LIMIT ? OFFSET ?",
        per_page, offset
    )

    total = db.execute("SELECT COUNT(*) as count FROM posts")[0]["count"]
    next_page = offset + per_page < total

    return render_template("posts.html", posts=posts, page=page, next=next_page)


@app.route("/dashboard/reset-password", methods=["GET", "POST"])
@login_required
@role_required("admin", "author", "reader")
def reset_password():
    if request.method == "POST":
        password = request.form.get("password")
        if not password:
            flash("All fields are required.")
            return redirect("/dashboard/reset-password")

        new_hash = generate_password_hash(password)

        db.execute(
            """
            UPDATE users
            SET hash = ?
            WHERE id = ?
        """,
            new_hash, session["user_id"]
        )

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
            flash("Message is required.")
            return redirect("/dashboard/feedback")

        db.execute(
            """
            INSERT INTO feedback (user_id, subject, message)
            VALUES (?, ?, ?)
        """,
            user_id, subject, message
        )

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
    page = max(1, request.args.get("page", 1, type=int) or 1)
    per_page = 3
    offset = (page - 1) * per_page

    users = db.execute(
        """
        SELECT * FROM users
        WHERE is_active = 1
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """,
        per_page, offset
    )

    total = db.execute("SELECT COUNT(*) AS count FROM users WHERE is_active = 1")[0]["count"]

    next_page = offset + per_page < total
    prev_page = page > 1

    return render_template(
        "dashboard/admin/users.html",
        user=get_current_user(),
        users=users,
        users_count=total,
        page=page,
        next=next_page,
        prev=prev_page
    )


@app.route("/author/<int:user_id>")
def public_author(user_id):
    page = max(1, request.args.get("page", 1, type=int) or 1)
    per_page = 3
    offset = (page - 1) * per_page

    author = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    if not author:
        return error("Author not found!")

    posts = db.execute(
        """
        SELECT * FROM posts
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """,
        user_id, per_page, offset
    )

    total = db.execute("SELECT COUNT(*) as count FROM posts WHERE user_id = ?", user_id)[0]["count"]

    next_page = total > page * per_page
    prev_page = page > 1

    return render_template(
        "profile.html",
        author=author[0],
        posts=posts,
        page=page,
        next=next_page,
        prev=prev_page
    )


@app.route("/dashboard/user/delete/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_user(user_id):
    target_user = db.execute("SELECT role FROM users WHERE users.id = ?", user_id)
    if not target_user:
        flash("User not found.")
        return redirect("/dashboard/users")

    if target_user[0]["role"] in ["admin", "author"]:
        flash("You cannot delete admin or author accounts.")
        return redirect("/dashboard/users")

    db.execute("UPDATE users SET is_active = 0 WHERE id = ?", user_id)

    flash("User deleted successfully!")
    return redirect("/dashboard/users")


@app.route("/dashboard/posts/delete/<int:post_id>", methods=["POST"])
@login_required
@role_required("admin", "author")
def delete_post(post_id):
    post = db.execute("SELECT user_id FROM posts WHERE id = ?", post_id)
    if not post:
        flash("Post not found.")
        return redirect("/dashboard/posts")

    curr_user = get_current_user()
    if curr_user["role"] != "admin" and post[0]["user_id"] != session["user_id"]:
        flash("Unauthorized to delete this post.")
        return redirect("/dashboard/posts")

    db.execute("DELETE FROM posts WHERE id = ?", post_id)
    flash("Post deleted successfully!")
    return redirect("/dashboard/posts")


@app.route("/dashboard/posts/edit/<int:post_id>", methods=["POST"])
@login_required
@role_required("admin", "author")
def edit_post(post_id):
    post = db.execute("SELECT * FROM posts WHERE id = ?", post_id)
    if not post:
        return error("Post not found", 404)

    curr_user = get_current_user()
    if curr_user["role"] != "admin" and post[0]["user_id"] != session["user_id"]:
        return error("Unauthorized to edit this post!", 403)

    title = request.form.get("title")
    category = request.form.get("category")
    content = request.form.get("content")

    if not title or not category or not content:
        return error("All fields are required!")

    image = request.files.get("image")

    if image and image.filename != "":
        original_name = secure_filename(image.filename)
        if not allowed_file(original_name):
            return error("Only PNG, JPG, JPEG, WEBP images allowed!")

        extension = original_name.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4()}.{extension}"
        file_location = os.path.join(UPLOAD_FOLDER, filename)
        image.save(file_location)

        db.execute(
            """
            UPDATE posts
            SET title = ?, category = ?, content = ?, image = ?
            WHERE id = ?
        """,
            title, category, content, filename, post_id
        )
    else:
        db.execute(
            """
            UPDATE posts
            SET title = ?, category = ?, content = ?
            WHERE id = ?
        """,
            title, category, content, post_id
        )

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
    return error("Page not found!", 404)


if __name__ == "__main__":
    app.run(debug=True)