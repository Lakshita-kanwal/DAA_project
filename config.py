#System Configuration Settings

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class AppConfig:
    #Main application configuration
    
    # Application settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-testing-only')
    UPLOAD_DIRECTORY = 'student_uploads'
    ALLOWED_FILE_TYPES = {'csv'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
    
    # Grouping algorithm parameters
    MIN_GROUP_SIZE = 3
    MAX_GROUP_SIZE = 5
    PERFORMANCE_LEVELS = {
        'high': 8.5,    # High: 8.5 and above
        'medium': 7.5,  # Medium: 6.0 to 8.49
        'low': 0.0      # Low: below 6.0
    }

class DatabaseConfig:
    #Database connection settings
    
    HOST = os.getenv('DB_HOST', 'localhost')
    USERNAME = os.getenv('DB_USER', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', 'jyoti')
    DATABASE = os.getenv('DB_NAME', 'student_db')
    PORT = int(os.getenv('DB_PORT', 3306))
    
    @classmethod
    def connection_string(cls):
        """Generate database connection string"""
        return {
            'host': cls.HOST,
            'user': cls.USERNAME,
            'password': cls.PASSWORD,
            'database': cls.DATABASE,
            'port': cls.PORT
        }

class EmailConfig:
    #Email notification settings
    
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'groups@university.edu')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@university.edu')
    
    # Email templates
    NEW_GROUP_TEMPLATE = """
    Hello {student_name},
    
    You've been assigned to {group_name} for your project work.
    
    Your team members:
    {team_members}
    
    Best regards,
    Student Grouping System
    """
    
    GROUP_CHANGE_TEMPLATE = """
    Hello {student_name},
    
    Your project group has changed. You are now in {group_name}.
    
    Your new team members:
    {team_members}
    
    Best regards,
    Student Grouping System
    """
