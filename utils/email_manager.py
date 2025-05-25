"""
Email Notification System

"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EmailConfig

def notify_students(student_data, groups_assigned, is_initial_setup):
    print("[INFO] notify_students() called")
    
    student_group_map = create_student_group_mapping(groups_assigned)
    
    # Determine students to notify
    if is_initial_setup:
        students_to_notify = student_data
        print(f"[INFO] Initial setup: notifying all {len(students_to_notify)} students")
    else:
        students_to_notify = []
        for student in student_data:
            prev_group = student.get('previous_group_id')
            new_group = None
            group_info = student_group_map.get(student['id'])
            if group_info:
                new_group = group_info['group_name']
            if prev_group != new_group:
                students_to_notify.append(student)
        print(f"[INFO] Group change mode: notifying {len(students_to_notify)} students")

    # If no students need to be notified
    if not students_to_notify:
        print("[WARNING] No students to notify. Exiting email step.")
        return

    # Setup Gmail API
    gmail_service = setup_gmail_service()

    # Send emails
    for student in students_to_notify:
        try:
            prepare_and_send_email(
                student,
                student_group_map,
                is_initial_setup,
                gmail_service
            )
            print(f"[✅] Email sent to {student['email']}")
        except Exception as e:
            print(f"[❌] Failed to send email to {student['email']}: {e}")


def create_student_group_mapping(groups):

    mapping = {}
    
    for group_name, members in groups.items():
        for student_id in members:
            mapping[student_id] = {
                'group_name': group_name,
                'members': [m for m in members if m != student_id]
            }
    
    return mapping

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def setup_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

import base64
from email.message import EmailMessage

def prepare_and_send_email(student, group_map, is_initial, gmail_service):
    student_id = student['id']
    student_info = group_map.get(student_id)

    if not student_info:
        return

    member_ids = student_info['members']
    id_to_name = student.get('id_to_name', {})
    member_names = [id_to_name.get(mid, mid) for mid in member_ids]
    members_display = "\n".join(f"{mid} - {name}" for mid, name in zip(member_ids, member_names))

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

    message = EmailMessage()
    message.set_content(email_content)
    message['To'] = student['email']
    message['From'] = EmailConfig.SENDER_EMAIL
    message['Subject'] = "Your Project Group Assignment"

    encoded_msg = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_msg = {'raw': encoded_msg}

    gmail_service.users().messages().send(userId="me", body=send_msg).execute()
