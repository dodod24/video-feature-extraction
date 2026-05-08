from feat import Detector
from feat.utils.io import get_test_data_path

import matplotlib.pyplot as plt

import os





detector = Detector(

    landmark_model="mobilefacenet",

    au_model="xgb",

    emotion_model="resmasknet",

    device="cuda"

)



detector





test_data_dir = get_test_data_path()

test_video_path = os.path.join(test_data_dir, "WolfgangLanger_Pexels.mp4")



# Show video

import cv2



# Carica il video

cap = cv2.VideoCapture(test_video_path)



while cap.isOpened():

    ret, frame = cap.read()

    if not ret:

        break



    # Mostra il frame in una finestra chiamata 'Video Preview'

    cv2.imshow('Video Preview', frame)



    # Premi 'q' sulla tastiera per chiudere la finestra in anticipo

    if cv2.waitKey(25) & 0xFF == ord('q'):

        break



cap.release()

cv2.destroyAllWindows()

video_prediction = detector.detect_video(

    test_video_path, skip_frames=24, face_detection_threshold=0.95

)



# Frame 48 = ~0:02

# Frame 408 = ~0:14

video_prediction.query("frame in [48, 408]").plot_detections(

    faceboxes=False, add_titles=False

)

video_prediction.head()

video_prediction.shape



axes = video_prediction.emotions.plot()

plt.show()