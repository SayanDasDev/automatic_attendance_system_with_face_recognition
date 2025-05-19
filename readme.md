# Automatic Attendance System

A Streamlit application that uses face recognition to automatically track attendance for classes.

## Features

- 🎥 Live webcam feed with face recognition

- ✅ Automatic attendance recording for detected faces

- 📊 Historical attendance records displayed in a table format

- 🏫 Supports multiple classes/sessions

- ➕ Add new students in real time

- 🗃️ SQLite database for persistent storage

## Prerequisites

- Python 3.10.13
- Webcam/Camera connected to your computer
- Download `buffalo-l` model [here](https://drive.google.com/file/d/1qXsQJ8ZT42_xSmWIYy85IcidpiZudOCB/view)
- Save model files in the `models/` directory:

## Installation

1. Clone this repository or download the code
2. Create a virtual environment (recommended)

```bash
conda create -n attendance-app python=3.10.13
conda activate attendance-app
```

If you don't have conda(NOT RECOMMANDED):

```bash
python -m venv .venv --python=python3.10.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the required packages

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:

```bash
streamlit run main.py
```

2. The application will:

   - Initialize the database
   - Extract face embeddings from the dataset (if not already done)
   - Start the webcam feed with face recognition

3. View attendance records in the table on the right side of the screen

4. To take attendance:

   - Enter a class name in the sidebar
   - Click "Start Attendance Capture"
   - The system will internally mark students as present when their faces are detected
   - Click "Stop Attendance Capture" when done and the attendance will be reflected in the table.

5. You can add new student in the form below the attendance records.

## Project Structure

```
attendance_app/
│
├── app/
│   ├── config/                # Configuration settings
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── session.py
│   │   └── attendance.py
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── attendance_service.py
│   │   └── face_service.py
│   ├── utils/                 # Helper functions
│   │   ├── __init__.py
│   │   ├── video_utils.py
│   │   └── constants.py
│   └── db/                    # Database connections
│       └── base.py
├── models/                    # Face recognition models
│   └── buffalo_l/
│       ├── det_10g.onnx       # Detection model
│       └── w600k_r50.onnx     # Recognition model
├── uploads/                   # Face embeddings storage
├── dataset/                   # Face images for recognition
├── main.py                    # Streamlit application
└── requirements.txt           # Dependencies

```

# Database Schema Overview

This database schema is for an **Automatic Attendance System** using SQLAlchemy ORM.

## Tables and Fields

### `users` Table

- `id` (Integer, Primary Key, Indexed)
- `name` (String, Unique, Indexed, Not Null)

### `sessions` Table

- `id` (Integer, Primary Key, Indexed)
- `name` (String, Unique, Not Null)
- `created_at` (DateTime, defaults to current time)

### `attendance` Table

- `id` (Integer, Primary Key, Indexed)
- `user_id` (Integer, Foreign Key → users.id, Not Null)
- `session_id` (Integer, Foreign Key → sessions.id, Not Null)
- **Unique Constraint**: `(user_id, session_id)`

## Relationships

- A `User` can attend many `Sessions`
- A `Session` can have many `Users`
- `Attendance` is the join table mapping many-to-many relationship between `User` and `Session`

---

## ER Diagram (ASCII)

```diff
+---------+        +---------------+        +-----------+
|  users  |        |  attendance   |        | sessions  |
+---------+        +---------------+        +-----------+
| id      |◄──┐    | id            |    ───>| id        |
| name    |   └──+ | user_id (FK)  |   |    | name      |
+---------+        | session_id(FK)|+──     | created_at|
                   +---------------+        +-----------+

```

# Troubleshooting

```bash
conda install -c conda-forge libstdcxx-ng
```

```bash
sudo dnf install gtk3-devel pkgconf-pkg-config
```
