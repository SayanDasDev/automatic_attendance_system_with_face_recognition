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

## Extending the Application

- To add new students: Add their photos to the dataset folder and restart the application
- To customize the UI: Modify the `main.py` file
- To change database settings: Update `app/config/config.py`

## Troubleshooting

- **Camera not working**: Check if your webcam is properly connected and not in use by another application
- **Face not recognized**: Ensure you have clear photos in the dataset directory and that lighting conditions are good
- **Database errors**: Delete the `attendance.db` file and restart to reset the database
