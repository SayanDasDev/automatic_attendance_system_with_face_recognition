import os
import streamlit as st
import cv2
import pandas as pd
import numpy as np
from datetime import datetime
import time

# Import modules from the application
from app.config.config import Config
from app.models import init_db, User, Session, Attendance
from app.services.attendance_service import AttendanceService
from app.services.face_service import FaceService
from app.utils.constants import ABSENT_MARK, PRESENT_MARK
from app.utils.video_utils import get_video_capture

# Initialize the database
init_db()

# Initialize services
attendance_service = AttendanceService()
face_service = FaceService()

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Automatic Attendance System",
        page_icon="📋",
        layout="wide"
    )

    # Title and description
    st.title("Automatic Attendance System")
    st.markdown("Track attendance automatically using face recognition")

    # Initialize session state variables
    if 'is_capturing' not in st.session_state:
        st.session_state.is_capturing = False
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'recognized_students' not in st.session_state:
        st.session_state.recognized_students = set()

    # Sidebar for session control
    with st.sidebar:
        st.header("Attendance Control")

        if not st.session_state.is_capturing:
            # Class name input
            class_name = st.text_input("Class Name", "")

            # Start capture button
            if st.button("Start Attendance Capture"):
                if class_name:
                    today = datetime.now().strftime("%b %d, %Y")
                    session_name = f"{today} - {class_name}"

                    # Create a new session
                    session_id = attendance_service.create_session(session_name)
                    st.session_state.current_session_id = session_id
                    st.session_state.is_capturing = True
                    st.session_state.recognized_students = set()
                    st.success(f"Started attendance for: {session_name}")
                    st.experimental_rerun()
                else:
                    st.error("Please enter a class name")
        else:
            st.info(f"Currently capturing attendance for session #{st.session_state.current_session_id}")

            # Stop capture button
            if st.button("Stop Attendance Capture"):
                # Finalize the session
                st.session_state.is_capturing = False
                st.session_state.current_session_id = None
                st.session_state.recognized_students = set()
                st.success("Attendance capture stopped")
                st.experimental_rerun()

    # Main content area - split into two columns
    col1, col2 = st.columns([3, 2])

    # Column 1: Video feed
    with col1:
        st.header("Attendance Records")

        # Get all attendance data
        attendance_df = attendance_service.get_attendance_dataframe()

        if attendance_df is not None and not attendance_df.empty:
            # Style the dataframe to show checkmarks and X marks
            styled_df = attendance_df.copy()

            # Replace 1s with ✅ and 0s with ❌
            for col in styled_df.columns:
                if col != 'Student':
                    styled_df[col] = styled_df[col].map({1: PRESENT_MARK, 0: ABSENT_MARK})

            # Display the styled dataframe
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No attendance records found yet. Start capturing attendance to see records.")

        # Currently recognized students during this session
        if st.session_state.is_capturing and st.session_state.recognized_students:
            st.subheader("Currently Recognized")
            st.write(", ".join(sorted(st.session_state.recognized_students)))

        with st.expander("➕ Add New Person"):
            person_name = st.text_input("Enter person's name")

            uploaded_images = st.file_uploader(
                "Upload face images",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )

            if st.button("Save Person"):
                if not person_name.strip():
                    st.warning("Please enter a valid name.")
                elif not uploaded_images:
                    st.warning("Please upload at least one image.")
                else:
                    # Process and save each image
                    for img_file in uploaded_images:
                        image_bytes = img_file.read()

                        # Save image using face service
                        face_service.save_face_image(person_name.strip(), image_bytes)

                    st.success(f"Person '{person_name}' with {len(uploaded_images)} image(s) added successfully!")
                    st.rerun()



    # Column 2: Attendance Records
    with col2:
        st.header("Live Camera Feed")

        # Placeholder for the video feed
        video_placeholder = st.empty()

        # Load face recognition models and data
        face_service.load_models()
        known_embeddings, known_names = face_service.load_embeddings()

        if known_embeddings is None or known_names is None:
            st.error("No face embeddings found. Please ensure the dataset is properly prepared.")
            return

        # Start video capture
        cap = get_video_capture()
        if not cap.isOpened():
            st.error("Unable to open camera. Please check your camera connection.")
            return

        try:
            # Process frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to grab frame from camera.")
                    break

                # Process the frame with face recognition
                processed_frame, detected_names = face_service.process_frame(
                    frame, known_embeddings, known_names
                )

                # Record attendance if capturing is active
                if st.session_state.is_capturing:
                    for name in detected_names:
                        if name != 'Unknown' and name not in st.session_state.recognized_students:
                            attendance_service.mark_attendance(
                                st.session_state.current_session_id,
                                name
                            )
                            st.session_state.recognized_students.add(name)

                # Display the processed frame
                video_placeholder.image(
                    cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB),
                    channels="RGB",
                    use_column_width=True
                )

                # Small delay to prevent high CPU usage
                time.sleep(0.01)

                # Check if app state has changed
                if not st.session_state.is_capturing and len(st.session_state.recognized_students) > 0:
                    st.session_state.recognized_students = set()

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            # Release camera when app is closed
            cap.release()

if __name__ == "__main__":
    main()
