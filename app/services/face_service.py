"""
Service for face detection and recognition
"""

import os
import cv2
import pickle
import numpy as np
from glob import glob
from app.models import get_db, User
from insightface.app.common import Face
from insightface.model_zoo import model_zoo
from datetime import datetime
from app.config.config import Config

class FaceService:
    def __init__(self):
        """Initialize the face service"""
        self.det_model = None
        self.rec_model = None

    def load_models(self):
        """Load the detection and recognition models"""
        # Check if models are already loaded
        if self.det_model is not None and self.rec_model is not None:
            return

        try:
            # Load detection model
            self.det_model = model_zoo.get_model(Config.DET_MODEL_PATH)
            self.det_model.prepare(ctx_id=0, input_size=(640, 640), det_thres=Config.DETECTION_THRESHOLD)

            # Load recognition model
            self.rec_model = model_zoo.get_model(Config.REC_MODEL_PATH)
            self.rec_model.prepare(ctx_id=0, input_size=(640, 640), det_thres=Config.DETECTION_THRESHOLD)
        except Exception as e:
            raise Exception(f"Failed to load face models: {str(e)}")

    def save_face_image(self, person_name: str, image_bytes: bytes):
        """
        Save an uploaded face image to the dataset directory under the person's name.

        Args:
            person_name (str): Name of the person.
            image_bytes (bytes): Image content in bytes.
        """
        db = get_db()
        try:
            existing_user = db.query(User).filter_by(name=person_name).first()
            if existing_user:
                # User exists - do NOT save image or extract embeddings
                return False

            # User does not exist - save user to DB
            new_user = User(name=person_name)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        finally:
            db.close()

        # Create a safe folder name
        safe_name = person_name.strip().replace(" ", "_")

        # Determine person-specific path
        person_folder = os.path.join(Config.DATASET_PATH, safe_name)
        os.makedirs(person_folder, exist_ok=True)

        # Unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}.jpg"
        file_path = os.path.join(person_folder, filename)

        # Save image to disk
        with open(file_path, "wb") as f:
            f.write(image_bytes)


        # immediately extract updated embeddings after adding image
        self.extract_face_embeddings()

    def extract_face_embeddings(self):
        """
        Extract face embeddings from images in the dataset directory

        Returns:
            tuple: (known_embeddings, known_names) - the extracted embeddings and corresponding names
        """
        embeddings_path = Config.EMBEDDINGS_PATH
        names_path = Config.NAMES_PATH

        # Initialize empty arrays for embeddings and names
        known_embeddings = np.array([]).reshape(0, 512)
        known_names = []

        # Check if dataset directory exists
        if not os.path.exists(Config.DATASET_PATH):
            os.makedirs(Config.DATASET_PATH)
            return known_embeddings, known_names

        # List all directories in the dataset folder
        person_dirs = [d for d in os.listdir(Config.DATASET_PATH)
                      if os.path.isdir(os.path.join(Config.DATASET_PATH, d))]

        # Load face detection and recognition models if not already loaded
        if self.det_model is None or self.rec_model is None:
            self.load_models()

        # Process each person's directory
        for person_name in person_dirs:
            directory = os.path.join(Config.DATASET_PATH, person_name)
            img_paths = glob(f"{directory}/*.jpg")
            new_embeddings = []

            for img_path in img_paths:
                img = cv2.imread(img_path)
                if img is None:
                    continue

                # Detect faces in the image
                bboxes, kpss = self.det_model.detect(img, max_num=0, metric='default')
                if len(bboxes) == 0:
                    continue

                # Process the first face (assuming one face per image)
                bbox = bboxes[0, :4]
                det_score = bboxes[0, 4]
                kps = kpss[0]
                face = Face(bbox=bbox, kps=kps, det_score=det_score)

                # Extract embedding for the face
                self.rec_model.get(img, face)

                if hasattr(face, 'normed_embedding'):
                    new_embeddings.append(face.normed_embedding)

            # Add embeddings to the collection if any were found
            if new_embeddings:
                new_embeddings = np.vstack(new_embeddings)
                known_embeddings = np.vstack([known_embeddings, new_embeddings])
                known_names.extend([person_name] * new_embeddings.shape[0])

        # Save embeddings and names
        os.makedirs(os.path.dirname(embeddings_path), exist_ok=True)
        np.save(embeddings_path, known_embeddings)
        with open(names_path, 'wb') as f:
            pickle.dump(known_names, f)

        return known_embeddings, known_names

    def load_embeddings(self):
        """
        Load saved face embeddings and names

        Returns:
            tuple: (known_embeddings, known_names) - the loaded embeddings and corresponding names
        """
        embeddings_path = Config.EMBEDDINGS_PATH
        names_path = Config.NAMES_PATH

        if os.path.exists(embeddings_path) and os.path.exists(names_path):
            try:
                known_embeddings = np.load(embeddings_path)
                with open(names_path, 'rb') as f:
                    known_names = pickle.load(f)
                return known_embeddings, known_names
            except Exception as e:
                print(f"Error loading embeddings: {str(e)}")
                return None, None
        else:
            # If no embeddings exist, extract them from dataset
            return self.extract_face_embeddings()

    def find_match(self, embedding, known_embeddings, known_names):
        """
        Find the closest match for a face embedding

        Args:
            embedding: The face embedding to match
            known_embeddings: Array of known embeddings
            known_names: List of corresponding names

        Returns:
            str: The name of the closest match or 'Unknown'
        """
        # Calculate cosine similarity between embeddings
        scores = np.dot(embedding, known_embeddings.T)
        scores = np.clip(scores, 0., 1.)

        # Get the highest score and its index
        idx = np.argmax(scores)
        score = scores[idx]

        # Return name if the score exceeds the threshold, otherwise 'Unknown'
        return known_names[idx] if score > Config.RECOGNITION_THRESHOLD else 'Unknown'

    def process_frame(self, frame, known_embeddings, known_names):
        """
        Process a video frame with face detection and recognition

        Args:
            frame: The video frame to process
            known_embeddings: Array of known embeddings
            known_names: List of corresponding names

        Returns:
            tuple: (processed_frame, detected_names) - the frame with overlays and list of detected names
        """
        # Ensure models are loaded
        if self.det_model is None or self.rec_model is None:
            self.load_models()

        detected_names = []

        # Detect faces in the frame
        bboxes, kpss = self.det_model.detect(frame, max_num=0, metric='default')

        if len(bboxes) > 0:
            for i in range(len(bboxes)):
                bbox = bboxes[i, :4]
                kps = kpss[i]
                face = Face(bbox=bbox, kps=kps, det_score=bboxes[i, 4])

                # Extract embedding for the face
                self.rec_model.get(frame, face)
                test_embedding = face.normed_embedding

                # Find the closest match
                pred_name = self.find_match(test_embedding, known_embeddings, known_names)

                # Add the name to the detected list if not Unknown
                if pred_name != 'Unknown':
                    detected_names.append(pred_name)

                # Draw bounding box and name
                x1, y1, x2, y2 = map(int, bbox)

                # Set color based on name
                if pred_name == 'Unknown':
                    color = (0, 0, 255)  # Red for unknown
                elif pred_name == 'sayan':
                    color = (215, 168, 150)  # Custom color for sayan
                else:
                    color = (70, 255, 20)  # Green for other known people

                # Draw rectangle and text
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, pred_name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, color, 2)

        return frame, detected_names
