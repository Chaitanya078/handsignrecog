from flask import Flask, render_template, Response
import cv2
import numpy as np
import pickle
import mediapipe as mp
import time

app = Flask(__name__)

cap = cv2.VideoCapture(0)

# Load the trained model
model_dict = pickle.load(open('./model1.p', 'rb'))
model = model_dict['model']

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3, max_num_hands=2)
if hands:
    print("MediaPipe Hands model loaded successfully")
else:
    print("Error loading MediaPipe Hands model")


labels_dict = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I',
    9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q',
    17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y',
    25: 'Z', 26: 'del', 27: 'nothing', 28: '_'
}

predicted_labels = []  # List to store predicted labels

cap = cv2.VideoCapture(0)

app.static_folder = 'static'

@app.route('/')
def index():
    return render_template('index.html')

def process_frame(frame):
    data_aux_left = []  # for left hand
    data_aux_right = []  # for right hand

    H, W, _ = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)
    num_detected_hands = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0

    if num_detected_hands == 1:
        hand_landmarks = results.multi_hand_landmarks[0]
        for landmark in hand_landmarks.landmark:
            x = landmark.x
            y = landmark.y
            data_aux_left.append(x)
            data_aux_left.append(y)
        # Extend the features to 84 by adding zeros
        data_aux_left += [0] * (84 - len(data_aux_left))
        prediction = model.predict([np.asarray(data_aux_left)])

    elif num_detected_hands == 2:
        for hand_landmarks in results.multi_hand_landmarks:
            for landmark in hand_landmarks.landmark:
                x = landmark.x
                y = landmark.y
                data_aux_right.append(x)
                data_aux_right.append(y)
        prediction = model.predict([np.asarray(data_aux_right)])

    else:
        # If no hands are detected, set prediction to None
        prediction = None

    if prediction is not None:
        predicted_character = labels_dict[int(prediction[0])]
        print("Predicted Character:", predicted_character)
        # Only append if the predicted label is different from the last one
        if len(predicted_labels) == 0 or predicted_labels[-1] != predicted_character:
            predicted_labels.append(predicted_character)

    # Draw landmarks for all detected hands
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            print("Hand landmarks detected:", hand_landmarks)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    return frame

def generate_frames():
    while True:
        time.sleep(0.1)  # Add a short delay
        ret, frame = cap.read()

        if not ret:
            print('Failed to read frame from the webcam.')
            break
        frame = cv2.flip(frame, 1)

        print('Processing frame...')
        processed_frame = process_frame(frame)

        # Concatenate and draw the predicted labels as a string on the frame
        predicted_labels_string = ' '.join(predicted_labels)
        # Ensure the text stays inside the frame
        text_x = 50
        text_y = 50
        text_color = (0, 255, 0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        text_size, _ = cv2.getTextSize(predicted_labels_string, font, font_scale, font_thickness)
        if text_x + text_size[0] > processed_frame.shape[1]:
            text_x = processed_frame.shape[1] - text_size[0] - 10
        if text_y + text_size[1] > processed_frame.shape[0]:
            text_y = processed_frame.shape[0] - text_size[1] - 10
        cv2.putText(processed_frame, predicted_labels_string, (text_x, text_y), font, font_scale, text_color, font_thickness)

        ret, jpeg = cv2.imencode('.jpg', processed_frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)

