# OPEN JOURNAL
#### Video Demo:  <https://www.youtube.com/watch?v=50x3WIcrHFo>
#### Description: 
Open Journal is a modern full-stack CMS built with Flask, Jinja2, SQLite, and Tailwind CSS. It provides a simple, role-based system where users can read, create, and manage articles across categories such as News, Tech, Sports, Entertainment, and Opinion, with structured access and an easy-to-use dashboard.

## Features
### Public Features
* Browse latest news and featured posts
* Category-based filtering (News, Tech, Sports, etc.)
* Individual post pages with full content
* Author profile pages
* Responsive UI with Tailwind CSS
* Flash message notifications

### Authentication
* User registration with profile photo
* Secure login/logout system
* Password hashing (Flask backend)

### Roles & Permissions
* **Reader**: Can browse content and apply to become an author
* **Author**: Can create and manage posts
* **Admin**: Full access (users, posts, applications)

### Dashboard
* Role-based dashboard UI
* Sidebar navigation with dynamic options
* Profile overview
* Admin controls 

### Content Management
* Create, view, and manage posts
* Upload images for posts
* Pagination for posts and categories

## Tech Stack
**Backend**
* Python (Flask)
* Jinja Templates
* SQLite3

**Frontend**
* HTML5
* Tailwind CSS
* JavaScript (Vanilla)
* Flowbite components

## Note 
Tailwind CSS was used for styling due to familiarity with utility-first design, and Flowbite components were used in parts of the dashboard and homepage to speed up development and maintain UI consistency.

Some features, particularly pagination, were implemented after learning concepts with the help of AI (ChatGPT by OpenAI). It was used as a learning resource to understand LIMIT/OFFSET queries and page navigation, while the final implementation was written, adapted, and tested independently.

I also applied prior full-stack (MERN) experience to structure the project. Tools like Werkzeug and UUID were explored, and logic from Project 9 was adapted after fully understanding it. Additionally, SQLite tutorials from various online sources were used to strengthen database handling. The role-based access system was implemented using my own logic, and the project was built as a CMS with a dashboard and portal.
