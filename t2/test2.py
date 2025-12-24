import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Không thể mở camera!")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc khung hình!")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        print(f"Frame shape: {frame.shape}, dtype: {frame.dtype}")
        print(f"Gray shape: {gray.shape}, dtype: {gray.dtype}")

        cv2.imshow("Camera", gray)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()