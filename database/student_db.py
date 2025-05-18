# FlaskSQLAlchemy-based implementation
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

db = SQLAlchemy()

# Models
class Group(db.Model):
    __tablename__ = 'groups_'
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    students = db.relationship('Student', backref='group', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Numeric(3,2))
    residence = db.Column(db.Enum('Hosteller', 'Dayscholar'), nullable=False)
    interest = db.Column(db.Enum('Web Dev', 'Cloud', 'Cybersecurity', 'AI', 'None'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups_.group_id'))
    previous_group_id = db.Column(db.Integer)

def init_app(app):
    db.init_app(app)

def save_student_data(student_records, student_groups):
    for student in student_records:
        existing = Student.query.filter_by(student_id=student['id']).first()
        if existing:
            existing.name = student['name']
            existing.email = student['email']
            existing.cgpa = student['cgpa']
            existing.residence = student['residence']
            existing.interest = student['interest']
        else:
            new_student = Student(
                student_id=student['id'],
                name=student['name'],
                email=student['email'],
                cgpa=student['cgpa'],
                residence=student['residence'],
                interest=student['interest']
            )
            db.session.add(new_student)
    db.session.commit()

    previous_groups = {}
    for student in Student.query.all():
        previous_groups[student.student_id] = student.group_id

    group_name_to_id = {}
    for group_name, member_ids in student_groups.items():
        group = Group.query.filter_by(group_name=group_name).first()
        if not group:
            group = Group(group_name=group_name)
            db.session.add(group)
            db.session.commit()
        group_name_to_id[group_name] = group.group_id
        for sid in member_ids:
            student = Student.query.filter_by(student_id=sid).first()
            if student:
                student.previous_group_id = student.group_id
                student.group_id = group.group_id
    db.session.commit()

    changed_students = {}
    for student in Student.query.all():
        old = previous_groups.get(student.student_id)
        new = student.group_id
        if old != new:
            changed_students[student.student_id] = (old, new)
    return changed_students

def get_existing_students():
    with current_app.app_context():
        students = Student.query.all()
        return [
            {
                'id': s.student_id,
                'name': s.name,
                'email': s.email,
                'cgpa': float(s.cgpa) if s.cgpa is not None else None,
                'residence': s.residence,
                'interest': s.interest,
                'group_id': s.group_id,
                'previous_group_id': s.previous_group_id
            }
            for s in students
        ]

def get_all_groups_with_members():
    with current_app.app_context():
        groups = Group.query.all()
        result = {}
        for group in groups:
            members = [s.student_id for s in group.students]
            result[group.group_name] = members
        return result
