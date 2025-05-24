"""
Email Notification System
Handles all communication with students about their group assignments
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EmailConfig

def notify_students(student_data, groups_assigned, is_initial_setup):
    """
    Manages all email notifications to students:
    - First run: Notify everyone about their new groups
    - Subsequent runs: Only notify students whose groups changed
    """
    student_group_map = create_student_group_mapping(groups_assigned)
    
    # On initial setup, notify all students
    if is_initial_setup:
        students_to_notify = student_data
    else:
        # Only notify students whose group has changed
        students_to_notify = []
        for student in student_data:
            prev_group = student.get('previous_group_id')
            new_group = None
            # Find new group id from mapping
            group_info = student_group_map.get(student['id'])
            if group_info:
                new_group = group_info['group_name']
            # Compare previous and new group
            if prev_group != new_group:
                students_to_notify.append(student)
    
    # Send emails
    mail_server = setup_email_connection()
    try:
        for student in students_to_notify:
            try:
                prepare_and_send_email(
                    student,
                    student_group_map,
                    is_initial_setup,
                    mail_server
                )
            except Exception as e:
                print(f"Failed to send email to {student['email']}: {e}")
    finally:
        mail_server.quit()

def create_student_group_mapping(groups):
    """Creates a dictionary mapping student IDs to their group names"""
    mapping = {}
    
    for group_name, members in groups.items():
        for student_id in members:
            mapping[student_id] = {
                'group_name': group_name,
                'members': [m for m in members if m != student_id]
            }
    
    return mapping

def setup_email_connection():
    """Establishes connection with SMTP server"""
    server = smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT)
    server.set_debuglevel(1)
    server.starttls()
    server.login(EmailConfig.SENDER_EMAIL, EmailConfig.SENDER_PASSWORD)
    return server

def prepare_and_send_email(student, group_map, is_initial, server):
    """Prepares and sends individual email to each student"""
    
    student_id = student['id']
    student_info = group_map.get(student_id)
    
    # Skip if student isn't in any group (shouldn't happen)
    if not student_info:
        return

    # Get names of group members (excluding the student)
    member_ids = student_info['members']
    # You need a mapping from student_id to name
    # Let's assume you pass it as student['id_to_name'] (update call accordingly)
    id_to_name = student.get('id_to_name', {})
    member_names = [id_to_name.get(mid, mid) for mid in member_ids]
    members_display = "\n".join(f"{mid} - {name}" for mid, name in zip(member_ids, member_names))

    # Prepare email content based on situation
    if is_initial:
        email_content = EmailConfig.NEW_GROUP_TEMPLATE.format(
            student_name=student['name'],
            group_name=student_info['group_name'],
            team_members=members_display
        )
    else:
        email_content = EmailConfig.GROUP_CHANGE_TEMPLATE.format(
            student_name=student['name'],
            group_name=student_info['group_name'],
            team_members=members_display
        )
    
    # Create email message
    message = MIMEMultipart()
    message['From'] = EmailConfig.SENDER_EMAIL
    message['To'] = student['email']
    message['Subject'] = "Your Project Group Assignment"
    
    # Attach our formatted message
    message.attach(MIMEText(email_content, 'plain'))
    
    # Send the email
    server.send_message(message)