import cv2
import dlib
import numpy as np
import yaml

class FaceRecognition:
    def __init__(self, label_dict_path, encodings_path):
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor("C:\\Users\\PC\\Desktop\\t2_02\\t2\\shape_predictor_68_face_landmarks.dat")
        self.face_recognition_model = dlib.face_recognition_model_v1("C:\\Users\\PC\\Desktop\\t2_02\\t2\\dlib_face_recognition_resnet_model_v1.dat")
        
        self.known_face_encodings = []
        self.known_face_labels = []
        self.label_classes = []
        
        self.recognition_threshold = 0.4  # Ngưỡng nhận diện
        
        # Biến theo dõi số lần nhận diện
        self.true_positives = 0
        self.false_negatives = 0
        
        self.load_encodings(label_dict_path, encodings_path)

    def load_encodings(self, label_dict_path, encodings_path):
        try:
            with open(label_dict_path, "r") as f:
                model_data = yaml.safe_load(f)

            self.known_face_encodings = [np.array(encoding) for encoding in model_data['train_encodings']]
            self.known_face_labels = model_data['train_labels']
            self.label_classes = model_data['label_encoder']
            print("Khởi tạo nhận diện khuôn mặt thành công!")
        except Exception as e:
            print(f"Lỗi khởi tạo nhận diện khuôn mặt: {e}")

    def compute_face_distance(self, face_encoding1, face_encoding2):
        return np.linalg.norm(face_encoding1 - face_encoding2)

    def detect_face(self, frame):
        faces = self.face_detector(frame)
        if len(faces) > 0:
            return faces[0]
        return None

    def identify_face(self, face_encoding):
        if len(self.known_face_encodings) == 0:
            return "unknown", 0.0

        distances = [self.compute_face_distance(face_encoding, known_enc) 
                     for known_enc in self.known_face_encodings]
        
        min_distance_idx = np.argmin(distances)
        min_distance = distances[min_distance_idx]
        
        confidence = 1.0 - min_distance / 2.0  # Normalize distance to confidence
        
        if min_distance < self.recognition_threshold:
            label_idx = self.known_face_labels[min_distance_idx]
            ma_sv  = self.label_classes[label_idx]
            self.true_positives += 1  # Nhận diện đúng
            return ma_sv, confidence
        else:
            self.false_negatives += 1  # Nhận diện sai
            return "unknown", confidence

    def calculate_success_rate(self):
        total_attempts = self.true_positives + self.false_negatives
        if total_attempts == 0:
            return 0.0
        return (self.true_positives / total_attempts) * 100