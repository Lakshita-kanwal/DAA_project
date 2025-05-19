# Dynamic Student Grouping System (DAA Project)

This repository implements an automated student grouping system using Python and Flask, designed as a practical project for the Design and Analysis of Algorithms (DAA). The system streamlines the process of uploading student data, forming balanced groups based on various criteria, managing assignments, and sending notifications.

---

## 🚀 Features

- **CSV Upload**: Easily upload student data in CSV format via a web interface.
- **Automated Grouping**: Efficiently organizes students into balanced groups using CGPA, specialization, and residence.
- **Database Integration**: Stores and retrieves student and group data using MySQL (via SQLAlchemy).
- **Email Notifications**: Notifies students of their group assignments and any changes.
- **Admin Dashboard**: Displays results and summaries for administrators.

---

## 🗂️ Project Structure

```
DAA_project/
│
├── app.py                   # Main Flask application (routes, group processing)
├── config.py                # Central configuration (app, database, email, grouping params)
├── database/
│   ├── __init__.py
│   └── student_db.py        # Database models and helper functions
├── utils/
│   ├── group_organiser.py   # Grouping algorithm (not shown above)
│   └── email_manager.py     # Email notification logic (not shown above)
├── student_uploads/         # Uploaded CSV files (runtime)
├── templates/
│   ├── upload.html          # Upload interface (frontend)
│   └── results.html         # Group results display
├── .env                     # Environment variables for secrets (not in repo)
└── README.md
```

---

## ⚙️ Configuration

All settings are managed in `config.py` and/or the `.env` file:
- **App Settings**: Debug mode, upload folder, file size/type restrictions.
- **Database**: Connection details (host, user, password, db, port).
- **Grouping Algorithm**: Min/max group size, performance levels.
- **Email**: SMTP server, sender/receiver emails, template texts.

Sensitive values should be set in `.env` for security.

---

## 💡 How It Works

1. **Upload** a CSV with student records (id, name, email, CGPA, residence, specialization).
2. **Validate** the file and extract student data.
3. **Group** students using algorithms to balance group performance and interests.
4. **Save** group assignments in the database.
5. **Notify** students of their assignments (or changes).
6. **Display** results on the admin dashboard.

---

## 🏁 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lakshita-kanwal/DAA_project.git
   cd DAA_project
   ```

2. **Install dependencies** (Flask, SQLAlchemy, python-dotenv, pymysql):
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your environment:**
   - Copy `.env.example` to `.env` and fill in your secrets.

4. **Run the app:**
   ```bash
   python app.py
   ```

5. **Access the web interface** at [http://localhost:5000](http://localhost:5000).

---

## 📑 Example CSV Format

```csv
student_id,name,email,cgpa,residence,interest
101,John Doe,john@example.com,8.1,Hostel,AI
102,Jane Smith,jane@example.com,7.5,Day Scholar,ML
```

---

## 🤝 Contributing

Contributions and suggestions are welcome!  
- Fork this repo
- Create a new branch
- Submit a pull request


## 🙏 Acknowledgements

Built as part of a DAA Project Based Learning project.  
Special thanks to all contributors and reviewers.
