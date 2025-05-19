"""
Service for managing attendance records
"""

import pandas as pd
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.models import get_db, User, Session, Attendance
from app.utils.constants import DEFAULT_STUDENTS

class AttendanceService:
    def __init__(self):
        """Initialize the attendance service and ensure default students exist"""
        self._ensure_default_students()
    
    def _ensure_default_students(self):
        """Ensure that the default student records exist in the database"""
        db = get_db()
        try:
            # Check if each default student exists, create if not
            for student_name in DEFAULT_STUDENTS:
                student = db.query(User).filter(User.name == student_name).first()
                if not student:
                    new_student = User(name=student_name)
                    db.add(new_student)
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error ensuring default students: {str(e)}")
        finally:
            db.close()
    
    def create_session(self, session_name):
        """
        Create a new attendance session
        
        Args:
            session_name: Name of the session (e.g., "May 19, 2025 - Class 6")
            
        Returns:
            int: ID of the created session
        """
        db = get_db()
        try:
            # Check if session already exists
            existing_session = db.query(Session).filter(Session.name == session_name).first()
            if existing_session:
                return existing_session.id
            
            # Create new session
            new_session = Session(name=session_name)
            db.add(new_session)
            db.commit()
            
            return new_session.id
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create session: {str(e)}")
        finally:
            db.close()
    
    def mark_attendance(self, session_id, student_name):
        """
        Mark a student as present for a session
        
        Args:
            session_id: ID of the session
            student_name: Name of the student
            
        Returns:
            bool: True if attendance was marked successfully
        """
        db = get_db()
        try:
            # Get user by name
            user = db.query(User).filter(User.name == student_name).first()
            if not user:
                # Create user if not exists
                user = User(name=student_name)
                db.add(user)
                db.commit()
            
            # Check if attendance already exists
            existing_attendance = db.query(Attendance).filter(
                Attendance.user_id == user.id,
                Attendance.session_id == session_id
            ).first()
            
            if not existing_attendance:
                # Create attendance record
                attendance = Attendance(user_id=user.id, session_id=session_id)
                db.add(attendance)
                db.commit()
            
            return True
        except IntegrityError:
            # Skip if already marked (unique constraint violation)
            db.rollback()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error marking attendance: {str(e)}")
            return False
        finally:
            db.close()
    
    def get_attendance_dataframe(self):
        """
        Get attendance data as a pandas DataFrame
        
        Returns:
            DataFrame: Attendance data with students as rows and sessions as columns
        """
        db = get_db()
        try:
            # Get all users and sessions
            users = db.query(User).order_by(User.name).all()
            sessions = db.query(Session).order_by(Session.created_at).all()
            
            if not users or not sessions:
                return None
            
            # Create empty dataframe
            columns = ["Student"] + [session.name for session in sessions]
            data = []
            
            # Fill data for each user
            for user in users:
                row = [user.name]
                
                # Query attendance for each session
                for session in sessions:
                    attendance = db.query(Attendance).filter(
                        Attendance.user_id == user.id,
                        Attendance.session_id == session.id
                    ).first()
                    
                    # Mark 1 for present, 0 for absent
                    row.append(1 if attendance else 0)
                
                data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            return df
        except Exception as e:
            print(f"Error getting attendance dataframe: {str(e)}")
            return None
        finally:
            db.close()
