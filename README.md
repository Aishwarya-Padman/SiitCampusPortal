Overview:
SIITCampusPortal is a fully dynamic and database-driven college website built using Flask (Python) and MySQL. It is designed for ease of use by non-technical users such as college administrators. All major sections of the site can be updated directly through the database, including images, staff information, and academic details.

🔹 Key Features:
✅ Dynamic Image Management:

All website images (including banners, events, facilities, testimonials, and principal profile) are stored in the database (via image paths).

College admin can easily update or replace images based on new events or academic changes without coding knowledge.

✅ Student Feedback System:

Students can submit feedback with their photo, name, and description.

All feedback entries are stored in the database and displayed dynamically on the feedback/testimonials page.

✅ Admission Form with Conditional Logic:

Students fill out an online admission form.

All form data is stored in the MySQL database.

✅ Dynamic Merit List System:

Admin selects the number of students (e.g., top 20) from total submitted applications (e.g., 30).

Only selected students appear in the merit list page.

Until selection is made, the website shows "Merit List Unavailable".

Only shortlisted students can access the Final Admission Form, which upon submission is saved in the database.

✅ Principal and Staff Details:

Separate page for the Principal’s profile and staff information, all dynamically managed from the database.

✅ Contact Page:

Contains college contact details and an embedded location map.

✅ Admin Panel and images:

Image Handling: Dynamic image paths stored in database

Admin Panel: For managing merit list, images, and staff info



💻 Technologies Used

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **ORM**: SQLAlchemy (for models)
- **File Handling**: Flask-Uploads
- **Authentication**: Flask-Login 
