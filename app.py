"""
Main Flask Application for Student Grouping System
Handles file uploads, processes student data, and manages group formation
"""

import csv
import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from utils.group_organiser import organise_students_into_groups
from utils.email_manager import notify_students
from database.student_db import save_student_data, get_existing_students, init_app, db, get_all_groups_with_members
from config import AppConfig


# Initialize our Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = AppConfig.UPLOAD_DIRECTORY
app.config['MAX_CONTENT_LENGTH'] = AppConfig.MAX_FILE_SIZE

# Database config for SQLAlchemy
from config import DatabaseConfig
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{DatabaseConfig.USERNAME}:{DatabaseConfig.PASSWORD}"
    f"@{DatabaseConfig.HOST}:{DatabaseConfig.PORT}/{DatabaseConfig.DATABASE}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_app(app)

def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in AppConfig.ALLOWED_FILE_TYPES

@app.route('/')
def show_homepage():
    """Display the main upload interface to users"""
    return render_template('upload.html')

@app.route('/process-groups', methods=['POST'])
def handle_student_upload():
    """
    Process uploaded student CSV file and create balanced groups
    1. Validate the uploaded file
    2. Read student data from CSV
    3. Organize students into balanced groups
    4. Save results and notify students
    """
    
    # Check if file was properly uploaded
    if 'student_data_file' not in request.files:
        return "No file uploaded", 400
    
    uploaded_file = request.files['student_data_file']
    
    # Validate file presence and type
    if uploaded_file.filename == '':
        return "No selected file", 400
        
    if not allowed_file(uploaded_file.filename):
        return "Invalid file type. Please upload a CSV file.", 400
    
    try:
        # Securely save the uploaded file
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)
        
        # Extract student data from CSV
        student_records = read_student_data(file_path)
        
        if not student_records:
            return "No valid student data found in the file", 400
        
        # Create a mapping of student IDs to names
        id_to_name = {student['id']: student['name'] for student in student_records}
        
        for student in student_records:
            student['id_to_name'] = id_to_name
        
        # Check if this is the first run of the system
        is_initial_setup = len(get_existing_students()) == 0
        
        # Use cgpa for performance in grouping
        for student in student_records:
            student['performance'] = student['cgpa']
            student['accommodation'] = student['residence']
            student['specialisation'] = student['interest']
        
        # Create balanced student groups using our algorithm
        student_groups = organise_students_into_groups(student_records, is_initial_setup)
        
        # Store results in database and get changed students
        changed_students_dict = save_student_data(student_records, student_groups)
        
        # Retrieve all groups with members from the database
        all_groups = get_all_groups_with_members()
        
        # Prepare list of students whose group changed
        changed_students = [s for s in student_records if s['id'] in changed_students_dict] if not is_initial_setup else student_records
        
        # Send appropriate email notifications
        notify_students(changed_students, student_groups, is_initial_setup)
        
        # Show results to the administrator
        return render_template(
            'results.html',
            groups=all_groups,
            total_students=len(student_records),
            total_groups=len(all_groups),
            id_to_name=id_to_name
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()  # This will print the full error to your console
        return f"An error occurred: {str(e)}", 500

def read_student_data(filepath):
    """Extract student records from uploaded CSV file"""
    students = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as csv_file:
            # Using DictReader to access columns by name
            reader = csv.DictReader(csv_file)
            
            for row in reader:
                try:
                    student = {
                        'id': row['student_id'].strip(),
                        'name': row['name'].strip(),
                        'email': row['email'].strip().lower(),
                        'cgpa': float(row['cgpa']),
                        'residence': row['residence'].strip().capitalize(),
                        'interest': row['interest'].strip()
                    }
                    students.append(student)
                except (ValueError, KeyError) as e:
                    # Skip rows with invalid data but continue processing
                    print(f"Skipping invalid row: {row}. Error: {e}")
                    continue
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise
    
    return students

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Create tables if they do not exist
    with app.app_context():
        db.create_all()
    app.run(debug=AppConfig.DEBUG_MODE)