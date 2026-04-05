# OPEN JOURNAL  
#### Video Demo:  <https://www.youtube.com/watch?v=50x3WIcrHFo>  

## Description  
Open Journal is a modern full-stack content management system (CMS) built using Flask, Jinja2, SQLite, and Tailwind CSS. The application is designed to provide a structured and user-friendly platform where users can explore, create, and manage articles across multiple categories such as News, Tech, Sports, Entertainment, and Opinion.

The platform follows a role-based architecture, ensuring that different types of users interact with the system in a controlled and meaningful way. Readers can browse content and discover articles, Authors can create and manage posts, and Admins have full control over the platform, including user management and system monitoring.

The goal of this project was to build a clean, scalable CMS with a focus on simplicity, usability, and clear separation between backend logic and frontend presentation.

---

## Features  

### Public Features  
Open Journal provides a smooth and responsive browsing experience for all users, even without authentication. The homepage dynamically displays the latest posts along with category-based sections, allowing users to quickly discover trending or recent content.

- Browse latest news and featured posts  
- Filter content by categories (News, Tech, Sports, etc.)  
- View individual post pages with full content and images  
- Visit author profile pages to explore their published articles  
- Fully responsive interface built with Tailwind CSS  
- Flash message notifications for user feedback  

---

### Authentication  
The application includes a secure authentication system that allows users to register, log in, and manage their sessions.

During registration, users must provide:
- Name  
- Username  
- Email  
- Password (with confirmation)  
- Profile photo upload  

Passwords are securely hashed using Flask’s Werkzeug utilities before being stored in the database. Session management is handled using Flask-Session, ensuring secure and persistent login states.

---

### Roles & Permissions  
A central part of Open Journal is its role-based access system:

- **Reader**: Default role. Can browse content and apply to become an author  
- **Author**: Can create, edit, and manage their own posts  
- **Admin**: Full control over users, posts, applications, and system data  

Custom decorators such as `login_required` and `role_required` are used to protect routes and enforce access control, ensuring users only access features appropriate to their role.

---

### Dashboard  
Each authenticated user has access to a personalized dashboard that adapts based on their role.

- Role-based dashboard UI (Reader, Author, Admin)  
- Sidebar navigation with dynamic options  
- Profile overview and account management  
- Admin controls for managing users and content  

---

### Content Management  
Open Journal includes a complete system for managing posts.

- Create new posts with title, category, content, and image  
- Upload images with validation (PNG, JPG, JPEG, WEBP)  
- Edit or delete posts through the dashboard  
- Pagination for posts and categories  

Images are stored using unique filenames generated with UUID to prevent conflicts. Pagination ensures efficient loading and navigation across large datasets.

---

## How It Works  

The application is built around Flask routes that handle different parts of the system. Each route connects user actions (such as logging in, creating posts, or viewing categories) with database operations using SQLite.

Jinja templates are used to render dynamic content on the frontend. Data from the backend is passed into templates and displayed using reusable components. This separation makes the code easier to manage and scale.

Role-based access is enforced using custom decorators. These decorators check whether a user is logged in and whether they have the correct role before allowing access to certain routes. This ensures both security and proper system behavior.

---

## Project Structure  

The project follows a simple and organized structure:

- `app.py` – Main application file containing routes and logic  
- `templates/` – HTML templates rendered with Jinja2  
- `static/` – CSS, JavaScript, and uploaded images  
- `helpers.py` – Custom helper functions (authentication, error handling)  
- `openjournal.db` – SQLite database  
- `tailwind.config.js` – TailwindCSS Configuration 

This structure keeps backend logic, frontend design, and data handling clearly separated.

---

## Tech Stack  

### Backend  
- Python (Flask)  
- Jinja Templates  
- SQLite3  
- CS50 SQL Library  

### Frontend  
- HTML5  
- Tailwind CSS  
- JavaScript (Vanilla)  
- Flowbite Components  

---

## Future Improvements  

There are several features that could be added in the future to enhance the platform:

- Comment system for posts  
- Like and bookmark functionality  
- Search feature for posts and authors  
- Rich text editor for better content creation  
- Email verification and password recovery system  

These improvements would make the platform more interactive and closer to a production-level CMS.


---

## Conclusion  

Open Journal is a complete full-stack web application that combines backend logic, database management, and frontend design into a cohesive system. It demonstrates practical implementation of authentication, role-based authorization, file uploads, pagination, and dynamic content rendering.

This project was developed as part of **Harvard’s CS50x: Introduction to Computer Science**, reflecting both foundational knowledge and independent learning applied to real-world web development.
