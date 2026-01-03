i want push my import cv2
from ultralytics import YOLO
import time
import win32com.client as wincl
from collections import Counter


voice = wincl.Dispatch("SAPI.SpVoice")
voice.Rate = 0
voice.Volume = 100


model = YOLO("yolov8n.pt")  


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Webcam not opening")
    exit()

CONF_THRESHOLD = 0.4
REENTRY_TIMEOUT = 1.5  
active_objects = {}    

print("✅ Webcam started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_frame_objects = []

    results = model(frame, stream=True)
    current_time = time.time()

    
    for r in results:
        for box in r.boxes:
            confidence = float(box.conf[0])
            if confidence < CONF_THRESHOLD:
                continue
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            current_frame_objects.append(class_name)

            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{class_name} {confidence:.2f}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    for obj, last_seen in list(active_objects.items()):
        if obj not in current_frame_objects and (current_time - last_seen > REENTRY_TIMEOUT):
            del active_objects[obj]

    
    new_objects = []
    for obj in current_frame_objects:
        if obj not in active_objects:
            new_objects.append(obj)
        active_objects[obj] = current_time 
    
    if new_objects:
        counts = Counter(new_objects)
        parts = []
        for obj, count in counts.items():
            if count > 1:
                parts.append(f"{count} {obj}s")
            else:
                parts.append(f"{obj}")
        announcement = "carefull there is  " + ", ".join(parts)
        print("Speaking:", announcement)
        voice.Speak(announcement)

    
    cv2.imshow("YOLOv8 Real-Time Detection & Grouped Speech", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()  
