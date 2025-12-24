import os
import re
import json
import threading
import time
import numpy as np
from queue import Queue
import yaml
import re

import cv2
import dlib
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import QtGui
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

class UI_SaveImg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Training Dialog")
        self.resize(800, 600)

        # Giao diện người dùng
        self.setupUi()

        # Các biến khởi tạo
        self.camera_active = False
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.face_detector = dlib.get_frontal_face_detector()
        self.save_queue = Queue()
        self.save_thread = threading.Thread(target=self.save_image_thread, daemon=True)
        self.save_thread.start()

        # Load cấu hình
        self.load_config()

    def setupUi(self):
        
        main_layout = QVBoxLayout(self)

        # Camera feed
        self.camera_label = QLabel("Camera Feed")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.camera_label)

        # Countdown Label
        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.countdown_label)

        # Button layout
        button_layout = QHBoxLayout()

        # Capture button
        self.capture_button = QPushButton("Chụp hình")
        button_layout.addWidget(self.capture_button)

        # Train button
        self.train_button = QPushButton("Training")
        button_layout.addWidget(self.train_button)

        # User name input
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("Nhập Mã Sinh Viên")
        button_layout.addWidget(self.lineEdit)

        main_layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Button connections
        self.capture_button.clicked.connect(self.toggle_camera_and_capture)
        self.train_button.clicked.connect(self.train_model)

    def load_config(self):
        """
        Load cấu hình từ file `config.json`.
        """
        default_config = {
            "dataset_path": "C:\\Users\\PC\\Desktop\\t2_02\\t2\\trainer\\dataset",
            "camera_width": 640,
            "camera_height": 480,
        }

        try:
            with open('config.json', 'r') as config_file:
                self.config = json.load(config_file)
            print("[INFO] Configuration loaded from config.json")
        except (FileNotFoundError, json.JSONDecodeError):
            print("[WARNING] Using default configuration.")
            self.config = default_config

        os.makedirs(self.config['dataset_path'], exist_ok=True)

    def toggle_camera_and_capture(self):
        if not self.camera_active:
            self.start_camera()
            self.capture_button.setText("Bắt đầu chụp")
        else:
            self.capture_images()

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.config['camera_width'])
        self.cap.set(4, self.config['camera_height'])
        self.timer.start(30)
        self.camera_active = True

    def stop_camera(self):
        self.timer.stop()
        self.cap.release()
        self.camera_active = False
        self.capture_button.setText("Chụp Ảnh")
        self.camera_label.setText("Camera Feed")
        self.status_label.clear()
        self.countdown_label.clear()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(image)
            self.camera_label.setPixmap(pixmap)

    def sanitize_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    def capture_images(self):
        face_name = self.lineEdit.text().strip()
        if not face_name:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng Mã Sinh Viên trước khi chụp ảnh!")
            return

        face_name = self.sanitize_filename(face_name)
        user_folder = os.path.join(self.config['dataset_path'], face_name)
        os.makedirs(user_folder, exist_ok=True)
        print(f"Đang lưu ảnh tại: {user_folder}")
        
        angles = ['Front', 'Left', 'Right', 'Up']
        for angle in angles:
            self.capture_angle_images(angle, user_folder, face_name)

        self.status_label.setText("Hoàn thành quá trình chụp ảnh!")
        self.stop_camera()
        self.show_completion_message()

    def capture_angle_images(self, angle, user_folder, face_name):
        count = 0
        while count < 2:  # Capture 2 images
            self.start_countdown()

            ret, img = self.cap.read()
            if not ret:
                self.status_label.setText("Không thể lấy khung hình")
                return

            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = self.face_detector(gray)
            if not faces:
                self.status_label.setText("Không phát hiện khuôn mặt, vui lòng điều chỉnh!")
                continue  # Skip to the next capture attempt if no face is detected

            for face in faces:
                x, y, w, h = (face.left(), face.top(), face.width(), face.height())
                buffer = 40  # Add padding to capture the entire face
                face_img = gray[max(0, y-buffer):y+h+buffer, max(0, x-buffer):x+w+buffer]

                if cv2.mean(face_img)[0] > 30:  # Check brightness
                    file_name = os.path.join(user_folder, f"{face_name}_{angle}_{count + 1}.jpg")
                    self.save_queue.put((file_name, face_img))
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    self.status_label.setText(f"Đã chụp ảnh {count + 1}/2 cho góc {angle}.")
                    count += 1  # Increment the captured images count
                else:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    self.status_label.setText("Ảnh quá tối, không lưu.")
                break  # Only capture the first detected face

            frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(image)
            self.camera_label.setPixmap(pixmap)

            if count < 2:  # Only sleep if not enough images captured
                time.sleep(1)  # Delay between captures

        # Longer delay when switching angles
        time.sleep(3)

    def start_countdown(self):
        for i in range(3, 0, -1):
            self.countdown_label.setText(f"Chụp ảnh trong {i} giây...")
            QApplication.processEvents()
            time.sleep(1)
        self.countdown_label.clear() 

    def save_image_thread(self):
        while True:
            file_name, image = self.save_queue.get()
            cv2.imwrite(file_name, image)
            self.save_queue.task_done()

    def show_completion_message(self):
        QMessageBox.information(self, "Hoàn thành", "Quá trình chụp ảnh hoàn tất!")

    def train_model(self):
        self.status_label.setText("Đang huấn luyện mô hình...")
        self.countdown_label.setText("Vui lòng chờ...")
        threading.Thread(target=self.train_model_thread).start()

    def train_model_thread(self):
        images = []
        labels = []
        label_dict = {}
        
        # Load and preprocess data
        for user_folder in os.listdir(self.config['dataset_path']):
            user_path = os.path.join(self.config['dataset_path'], user_folder)
            if os.path.isdir(user_path):
                image_count = 0
                for image_file in os.listdir(user_path):
                    image_path = os.path.join(user_path, image_file)
                    img = cv2.imread(image_path)
                    if img is not None:
                        # Normalize size based on aspect ratio
                        aspect_ratio = img.shape[1] / img.shape[0]
                        if aspect_ratio > 1:
                            new_width = 224
                            new_height = int(224 / aspect_ratio)
                        else:
                            new_height = 224
                            new_width = int(224 * aspect_ratio)
                        
                        img = cv2.resize(img, (new_width, new_height))
                        images.append(img)
                        labels.append(user_folder)
                        image_count += 1
                
                if image_count > 0:
                    label_dict[user_folder] = len(label_dict)

        # Encode labels
        le = LabelEncoder()
        labels_encoded = le.fit_transform(labels)

        # Split dataset
        X_train, X_test, y_train, y_test = train_test_split(
            images, labels_encoded, test_size=0.2, random_state=42, stratify=labels_encoded
        )

        # Initialize face recognizer
        self.face_recognizer = dlib.face_recognition_model_v1('C:\\Users\\PC\\Desktop\\t2_02\\t2\\dlib_face_recognition_resnet_model_v1.dat')
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor('C:\\Users\\PC\\Desktop\\t2_02\\t2\\shape_predictor_68_face_landmarks.dat')

        # Training
        train_encodings = []
        train_labels = []
        
        for img, label in zip(X_train, y_train):
            faces = self.face_detector(img, 1)
            for face in faces:
                shape = self.shape_predictor(img, face)
                face_encoding = np.array(
                    self.face_recognizer.compute_face_descriptor(img, shape)
                )
                train_encodings.append(face_encoding.tolist())
                train_labels.append(int(label))

        # Validation
        test_encodings = []
        test_labels = []
        
        for img, label in zip(X_test, y_test):
            faces = self.face_detector(img, 1)
            for face in faces:
                shape = self.shape_predictor(img, face)
                face_encoding = np.array(
                    self.face_recognizer.compute_face_descriptor(img, shape)
                )
                test_encodings.append(face_encoding.tolist())
                test_labels.append(int(label))

        # Save model and metadata
        model_data = {
            'train_encodings': train_encodings,
            'train_labels': train_labels,
            'test_encodings': test_encodings,
            'test_labels': test_labels,
            'label_encoder': le.classes_.tolist()
        }

        with open(os.path.join(self.config['dataset_path'], "model_data.yml"), "w") as f:
            yaml.dump(model_data, f)

        with open(os.path.join(self.config['dataset_path'], "label_dict.json"), "w") as f:
            json.dump(label_dict, f)

        # Calculate accuracy on test set
        correct = 0
        total = len(test_encodings)
        
        if total > 0:
            for test_encoding, test_label in zip(test_encodings, test_labels):
                distances = [np.linalg.norm(np.array(test_encoding) - np.array(train_enc)) 
                           for train_enc in train_encodings]
                min_distance_idx = np.argmin(distances)
                predicted_label = train_labels[min_distance_idx]
                
                if predicted_label == test_label:
                    correct += 1
            
            accuracy = (correct / total) * 100
            self.status_label.setText(f"Huấn luyện hoàn tất! Độ chính xác: {accuracy:.2f}%")
        else:
            self.status_label.setText("Huấn luyện hoàn tất!")
        
        self.countdown_label.clear()