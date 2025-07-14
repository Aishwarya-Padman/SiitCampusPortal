import os
import os
from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
import pymysql
from flask_mysqldb import MySQL  # ✅ Use Flask-MySQL
import mysql.connector  # ✅ Correct import
import pymysql  # already imported above

# Then use pymysql for the connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="Siit",
    cursorclass=pymysql.cursors.DictCursor
)

# ✅ Initialize Flask app FIRST
app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS

# ✅ Set Secret Key for Session
app.secret_key = 'secret_key'

# ✅ MySQL Configuration for Flask-MySQLdb
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'Siit'

# ✅ Initialize MySQL AFTER Flask App
mysql = MySQL(app)

# ✅ SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/Siit'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# ✅ Initialize SQLAlchemy
db = SQLAlchemy(app)

# ✅ Create Database Tables
with app.app_context():
    db.create_all()

# ✅ Correct Database Connection Function
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='Siit',
        cursorclass=pymysql.cursors.DictCursor  # Ensures dictionary output
    )
    return connection




# ✅ User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    



# Admission Model
class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    course = db.Column(db.String(50), nullable=False)
    marks_12th = db.Column(db.Integer, nullable=True)  # BCA/BCS के लिए
    graduation_marks = db.Column(db.Integer, nullable=True)  # MCS के लिए
    cet_marks = db.Column(db.Integer, nullable=True)  # सिर्फ BCA के लिए
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/admissionform', methods=['GET', 'POST'])
def admissionform():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        address = request.form.get('address')
        course = request.form.get('course')
        category = request.form.get('category')

        # Course के अनुसार Marks को सही तरीके से हैंडल करें
        if course == 'MCS':
            graduation_marks = request.form.get('graduation_marks')
            marks_12th = None
        else:
            marks_12th = request.form.get('marks_12th')
            graduation_marks = None

        cet_marks = request.form.get('cet_marks') if course == 'BCA' else None

        if not student_name or not email or not phone or not dob or not address or not course:
            flash("All fields are required!", "danger")
            return redirect(url_for('admissionform'))

        try:
            if marks_12th:
                marks_12th = int(marks_12th)
            if graduation_marks:
                graduation_marks = int(graduation_marks)
            if cet_marks:
                cet_marks = int(cet_marks)
        except ValueError:
            flash("Invalid marks input! Please enter a valid number.", "danger")
            return redirect(url_for('admissionform'))

        new_admission = Admission(
            student_name=student_name,
            email=email,
            phone=phone,
            dob=datetime.strptime(dob, "%Y-%m-%d"),
            address=address,
            course=course,
            marks_12th=marks_12th,
            graduation_marks=graduation_marks,
            cet_marks=cet_marks,
            category=category
        )

        db.session.add(new_admission)
        db.session.commit()
        flash("Admission form submitted successfully!", "success")
        return redirect(url_for('pay'))

    return render_template('admissionform.html')




# ✅ Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/get_full_table/<course>')
def get_full_table(course):
    students = admission.query.filter_by(course=course).all() # type: ignore
    student_data = [{"student_name": s.student_name, "marks": s.cet_marks or s.marks_12th or s.graduation_marks} for s in students]
    return jsonify(student_data)

@app.route("/get_meritlist/<course>")
def get_meritlist(course):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        sort_column = {
            "BCA": "cet_marks",
            "BCS": "marks_12th",
            "MCS": "graduation_marks"
        }.get(course)

        if not sort_column:
            return jsonify({"error": "Invalid course selected"})

        query = f"""
            SELECT student_name, COALESCE({sort_column}, 0) as marks 
            FROM admission 
            WHERE course = %s 
            ORDER BY {sort_column} DESC
        """
        cursor.execute(query, (course,))
        result = cursor.fetchall()
        db.close()

        return jsonify({"data": result}) if result else jsonify({"data": []})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/save_meritlist', methods=['POST'])
def save_meritlist():
    try:
        data = request.json
        course = data.get('course')
        number = int(data.get('number', 0))

        conn = get_db_connection()
        cursor = conn.cursor()

        sort_column = {
            "BCA": "cet_marks",
            "BCS": "marks_12th",
            "MCS": "graduation_marks"
        }.get(course)

        if not sort_column:
            return jsonify({"error": "Invalid course selected"})

        query = f"""
            SELECT student_name, COALESCE({sort_column}, 0) as marks
            FROM admission
            WHERE course = %s
            ORDER BY {sort_column} DESC
            LIMIT %s
        """
        cursor.execute(query, (course, number))
        students_data = cursor.fetchall()

        session[f'merit_list_{course.lower()}'] = students_data  # ✅ Course-specific merit list

        cursor.close()
        conn.close()

        return jsonify({"message": f"{course} Merit list saved successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/meritlist')
def meritlist():
    merit_bca = session.get('merit_list_bca', [])
    merit_bcs = session.get('merit_list_bcs', [])
    merit_mcs = session.get('merit_list_mcs', [])

    return render_template('meritlistall.html', merit_bca=merit_bca, merit_bcs=merit_bcs, merit_mcs=merit_mcs)

@app.route('/delete_all_meritlists', methods=['POST'])
def delete_all_meritlists():
    try:
        cursor.execute("DELETE FROM merit_list")  # type: ignore # Table ka naam check karo
        conn.commit()
        return jsonify({"message": "All merit lists deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"details": str(e)}), 500






@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['username'] = user.username
            session['email'] = user.email
            flash('Login successful!', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('Logged out successfully!', 'info')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        flash('Please login first!', 'warning')
        return redirect('/login')
    return render_template('index.html')

@app.route('/college')
def college():
    return render_template('college.html')

@app.route('/viceprincipal')
def viceprincipal():
    return render_template('viceprincipal.html')


@app.route('/bca')
def bca():
    return render_template('bca.html')


@app.route('/bcs')
def bcs():
    return render_template('bcs.html')


@app.route('/mcs')
def mcs():
    return render_template('mcs.html')


@app.route('/admissioncommittee')
def admissioncommittee():
    return render_template('admissioncommittee.html')

@app.route('/gallery1')
def gallery1():
    return render_template('gallery1.html')

@app.route('/hostel')
def hostel():
    return render_template('hostel.html')


@app.route('/bus')
def bus():
    return render_template('bus.html')

@app.route('/placement')
def Placement():
    return render_template('placement.html')



@app.route('/delete_meritlist', methods=['POST'])
def delete_meritlist():
    session.pop('merit_list', None)  # Remove merit list from session
    return redirect(url_for('meritlist_bca'))




@app.route('/meritlistall')
def meritlistall():
    return render_template('meritlistall.html')  # Ensure this file exists

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/pay')
def pay():
    return render_template('pay.html')

@app.route('/admin_meritlist')
def admin_meritlist():
    return render_template('login1.html')


ADMIN_USERNAME = "Siit"
ADMIN_PASSWORD = "Siit123"

# 📌 Route: Show Login Page
@app.route('/login1')
def login1():
    return render_template('login1.html')

# 📌 Route: Handle Login Request
@app.route('/login1', methods=['POST'])
def login1_post():
    username = request.form['username']  # Get username from form
    password = request.form['password']  # Get password from form

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True  # Set session
        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
    else:
        return render_template('login1.html', error="Invalid Credentials!")  # Show error

# 📌 Route: Admin Dashboard (Protected)
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login1'))  # Redirect to login if not logged in
    return render_template('admin_meritlist.html')

# 📌 Route: Logout
@app.route('/logout1')
def logout1():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login1'))  # Redirect to login page


@app.route("/submit_testimonial", methods=["POST"])
def submit_testimonial():
    name = request.form["name"]
    message = request.form["message"]
    rating = int(request.form["rating"])
    image = request.files["image"]
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO testimonials (name, message, image_filename, rating) VALUES (%s, %s, %s, %s)"
    values = (name, message, filename, rating)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/testimonials")



@app.route("/testimonials")
def testimonials():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, message, image_filename, rating FROM testimonials")
    all_reviews = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("testimonials.html", reviews=all_reviews)

class MeritList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    course = db.Column(db.String(50))
    marks = db.Column(db.Integer)

@app.route('/finalform', methods=['GET', 'POST'])
def finalform():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        course = request.form.get('course')

        # Check if student is in merit list
        student_in_merit = MeritList.query.filter_by(student_name=student_name, course=course).first()

        if not student_in_merit:
            flash("You are not in the merit list for selected course.", "danger")
            return redirect(url_for('finalform'))

        # If student is in merit, proceed to save admission
        email = request.form.get('email')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        address = request.form.get('address')
        category = request.form.get('category')

        marks_12th = request.form.get('marks_12th') if course in ['BCA', 'BCS'] else None
        graduation_marks = request.form.get('graduation_marks') if course == 'MCS' else None
        cet_marks = request.form.get('cet_marks') if course == 'BCA' else None

        new_admission = Admission(
            student_name=student_name,
            email=email,
            phone=phone,
            dob=datetime.strptime(dob, "%Y-%m-%d"),
            address=address,
            course=course,
            marks_12th=int(marks_12th) if marks_12th else None,
            graduation_marks=int(graduation_marks) if graduation_marks else None,
            cet_marks=int(cet_marks) if cet_marks else None,
            category=category
        )

        db.session.add(new_admission)
        db.session.commit()

        flash("Admission submitted successfully!", "success")
        return redirect(url_for('pay'))

    return render_template('finalform.html')



if __name__ == '__main__':
    app.run(debug=True)
