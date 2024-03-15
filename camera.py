from flask import Flask, Response, render_template_string, send_from_directory
import os
import time
from picamera2.picamera2 import Picamera2  # Assurez-vous que l'importation est correcte pour votre installation
import cv2
import numpy as np
import shutil
import threading
from collections import deque
import subprocess
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Charger le modèle SSD MobileNet pré-entraîné pour la détection d'objets
net = cv2.dnn.readNetFromTensorflow('model/ssd_mobilenet_v3_large_coco_2020_01_14/frozen_inference_graph.pb',
                                    'model/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt')


def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


video_folder = 'videos'
if os.path.exists(video_folder):
    clear_folder(video_folder)
if not os.path.exists(video_folder):
    os.makedirs(video_folder)

img_folder = 'img'
if os.path.exists(img_folder):
    clear_folder(img_folder)
if not os.path.exists(img_folder):
    os.makedirs(img_folder)

detection_interval = 30  # Intervalle de détection en frames
# Configuration du tampon vidéo
frame_buffer = deque(maxlen=60 * detection_interval)  # Taille suffisante pour stocker 2 secondes de vidéo à 30 fps
video_capture_duration = 10  # Durée totale de capture vidéo en secondes
pre_capture_duration = 2  # Durée de pré-capture en secondes
fps = 30  # À ajuster en fonction de la fréquence d'images réelle de la caméra

image_saved = False
video_saved = False
video_lock = Lock()
video_thread = None

obstruction_start_time = None
obstruction_duration = 5  # Durée d'obstruction en secondes
obstruction_mail_sent = False

thread_pool = ThreadPoolExecutor(max_workers=3)


def check_and_run_postfix_script():
    global image_saved, video_saved
    if image_saved and video_saved:
        subprocess.run(["python", "send_mail.py"])
        image_saved = False
        video_saved = False


def save_image(frame, timestamp):
    global image_saved
    img_filename = os.path.join(img_folder, f"{timestamp}.jpg")
    cv2.imwrite(img_filename, frame)
    image_saved = True
    check_and_run_postfix_script()


def save_video(frames, timestamp):
    global video_saved
    video_filename = os.path.join(video_folder, f"{timestamp}.mp4")
    actual_fps = len(frames) / video_capture_duration
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(video_filename, fourcc, actual_fps, (640, 480))
    for frame in frames:
        video_writer.write(frame)
    video_writer.release()
    video_saved = True
    check_and_run_postfix_script()


last_detection_time = None  # Marqueur de temps de la dernière détection
last_image_capture_time = None  # Marqueur de temps de la dernière capture d'image

highest_confidence = 0  # Confiance la plus élevée
highest_confidence_frame = None  # Image correspondant à la confiance la plus élevée

capture_start_time = None  # Marqueur de temps du début de la capture

frame_counter = 0  # Ajoutez un compteur de frames


def detect_movement(frame, prev_frame):
    if prev_frame is None:
        return False

    # Conversion des frames en niveaux de gris et application du flou
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    # Calcul de la différence entre les images actuelle et précédente
    delta_frame = cv2.absdiff(prev_gray, gray)
    thresh_frame = cv2.threshold(delta_frame, 25, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # Trouver les contours pour voir s'il y a un mouvement
    contours, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 1000:
            continue
        return True

    return False


def detecter_obstruction(image, obstruction_threshold=50):
    """
    Détecte une obstruction dans l'image capturée par la caméra.

    :param image: Image capturée par la caméra.
    :param obstruction_threshold: Seuil pour déterminer l'obstruction.
    :return: True si une obstruction est détectée, False sinon.
    """

    # Conversion de l'image en niveaux de gris avec OpenCV
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calcul de la luminosité moyenne
    average_brightness = np.average(gray_image)

    # Détection d'obstruction
    if average_brightness < obstruction_threshold:
        return True  # Obstruction détectée
    else:
        return False  # Pas d'obstruction détectée


def detect_objects(frame):
    global last_detection_time, highest_confidence, highest_confidence_frame, capture_start_time, frame_counter
    frame_counter += 1  # Increment the frame counter
    if frame_counter % detection_interval != 0:  # Skip detection if it's not the 30th frame
        return
    frame_counter = 0  # Reset the frame counter after detection

    timestamp = time.time()
    detected = False

    # Détectez les objets
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.6:  # Seuil de confiance pour détection
            class_id = int(detections[0, 0, i, 1])
            if class_id in [1, 3]:  # 1 pour humain, 3 pour voiture
                detected = True
                print("DETECTED !")
                last_detection_time = timestamp
                if capture_start_time is None:
                    capture_start_time = timestamp  # Réinitialise le marqueur de temps du début de la capture à chaque détection
                if confidence > highest_confidence:  # Si la confiance actuelle est supérieure à la confiance la plus élevée
                    highest_confidence = confidence
                    highest_confidence_frame = frame.copy()
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    cv2.rectangle(highest_confidence_frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    label = "Humain" if class_id == 1 else "Voiture"
                    cv2.putText(highest_confidence_frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 2)
                break


def capture_video_and_image(frame, picam2):
    global frame_buffer, last_detection_time, last_image_capture_time, highest_confidence, highest_confidence_frame, capture_start_time
    timestamp = time.time()
    frame_buffer.append(frame)

    # Enregistre l'image avec la confiance la plus élevée si 4 secondes se sont écoulées depuis le début de la capture
    if capture_start_time is not None and timestamp - capture_start_time >= 4 and highest_confidence > 0:
        if highest_confidence_frame is not None:
            print("Saving image")
            save_image(highest_confidence_frame, timestamp)
            highest_confidence = 0
            highest_confidence_frame = None
        capture_start_time = None

    # Déclenche l'enregistrement si une détection a eu lieu et que 10 secondes se sont écoulées depuis la dernière détection
    if last_detection_time and time.time() - last_detection_time < video_capture_duration:
        if time.time() - last_detection_time >= video_capture_duration - pre_capture_duration:
            if video_lock.acquire(blocking=False):
                try:
                    print("Enregistrement vidéo")
                    frames_to_save = list(frame_buffer)
                    thread_pool.submit(save_video, frames_to_save, timestamp)
                    last_detection_time = None
                    capture_start_time = None
                finally:
                    video_lock.release()


# Ajoutez une variable globale pour stocker l'image précédente
previous_frame = None
movement_detected = False


def gen_frames(picam2):
    global previous_frame, movement_detected, obstruction_start_time, obstruction_mail_sent
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if detecter_obstruction(frame):
            print("Obstruction détectée")
            if obstruction_start_time is None:
                obstruction_start_time = time.time()
            elif time.time() - obstruction_start_time >= obstruction_duration and not obstruction_mail_sent:
                subprocess.run(["python", "send_obstructed_mail.py"])
                obstruction_mail_sent = True
            previous_frame = frame
            continue
        else:
            obstruction_start_time = None
            obstruction_mail_sent = False

        # Exécution de la détection de mouvement dans un thread
        if previous_frame is not None:
            if detect_movement(frame, previous_frame):
                print("Mouvement détecté")
                # Détection d'objets uniquement si un mouvement est détecté
                detect_objects(frame)

        previous_frame = frame

        # Capture vidéo/image indépendamment de la détection de mouvement
        capture_video_and_image(frame, picam2)

        # Génération et envoi du frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/videos')  # Renommé pour mieux refléter le contenu servi
def captured_videos():
    videos = os.listdir(video_folder)
    videos.sort(reverse=True)
    video_html = "".join(
        f'<video width="320" controls><source src="/videos/{video}" type="video/mp4"></video><br>' for
        video in videos)
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="4">
        <title>Captured Videos</title>
    </head>
    <body>
        <h1>Captured Videos</h1>
        {video_html}
    </body>
    </html>
    '''


@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(video_folder, filename, mimetype='video/mp4')


@app.route('/img')
def serve_images():
    images = os.listdir(img_folder)
    images.sort(reverse=True)
    img_html = "".join(f'<img src="/img/{img}" width="320" <br>' for img in images)
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="4">
        <title>Captured Images</title>
    </head>
    <body>
        <h1>Captured Images</h1>
        {img_html}
    </body>
    </html>
    '''


@app.route('/img/<filename>')
def serve_image(filename):
    return send_from_directory(img_folder, filename, mimetype='image/jpeg')


@app.route('/video_feed')
def video_feed():
    picam2 = Picamera2()
    picam2.start_preview()  # Optionnel si vous voulez une prévisualisation sur un écran connecté
    preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(preview_config)
    picam2.start()
    return Response(gen_frames(picam2), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flux vidéo PiCamera2</title>
    </head>
    <body>
        <h1>Flux vidéo PiCamera2</h1>
        <img src="{{ url_for('video_feed') }}" style="width:auto;">
    </body>
    </html>
    ''')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True, port=5000)

