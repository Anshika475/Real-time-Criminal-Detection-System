import cv2
import os
import datetime
import geocoder
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from deepface import DeepFace
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))
email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")
email_to = os.getenv("EMAIL_TO")

print(f"[DEBUG] EMAIL_USER={email_user}")
print(f"[DEBUG] EMAIL_PASS={'*' * len(email_pass) if email_pass else None}")
print(f"[DEBUG] EMAIL_TO={email_to}")
print(f"[DEBUG] .env exists: {os.path.exists('.env')}")

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

CRIMINAL_FACE_DIR = "criminal_photos"
alerted = set()

def send_email_alert(name, matched_img_path):
    location = geocoder.ip('me')
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    city = location.city if location.city else "Unknown"
    state = location.state if location.state else "Unknown"
    latlng = location.latlng if location.latlng else ["Unknown", "Unknown"]
    latitude = latlng[0]
    longitude = latlng[1]

    subject = f"[ALERT] Criminal Detected: {name}"
    body = f"""
    A known criminal ({name}) was detected.

    Time: {timestamp}
    Location: {city}, {state}
    Coordinates: Latitude = {latitude}, Longitude = {longitude}

    Attached are the captured face and the database match.
    """

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = email_user
    msg['To'] = email_to

    msg.attach(MIMEText(body, 'plain'))

    # Attach current captured image
    if os.path.exists("current.jpg"):
        with open("current.jpg", "rb") as f:
            img_data = f.read()
            image = MIMEImage(img_data, name="captured.jpg")
            msg.attach(image)

    # Attach matched criminal image
    if os.path.exists(matched_img_path):
        with open(matched_img_path, "rb") as f:
            db_img = f.read()
            db_image = MIMEImage(db_img, name=os.path.basename(matched_img_path))
            msg.attach(db_image)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()
        print(f"[EMAIL] Alert with images sent for {name}!")
    except Exception as e:
        print(f"[ERROR] Failed to send email with images for {name}: {e}")

# Start camera
video = cv2.VideoCapture(0)
if not video.isOpened():
    print("[ERROR] Could not access the camera.")
    exit()
else:
    print("[INFO] Camera connected.")

while True:
    ret, frame = video.read()
    if not ret:
        print("[ERROR] Failed to read from camera.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]
        cv2.imwrite("current.jpg", face_img)

        try:
            result = DeepFace.find(
                img_path="current.jpg",
                db_path=CRIMINAL_FACE_DIR,
                enforce_detection=False,
                silent=True
            )

            if result and len(result[0]) > 0:
                identity_path = result[0].iloc[0]['identity']
                name = os.path.splitext(os.path.basename(identity_path))[0]

                if name not in alerted:
                    send_email_alert(name, identity_path)
                    alerted.add(name)

                # GREEN rectangle for known
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                # YELLOW rectangle for unknown
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                cv2.putText(frame, "Unknown", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        except Exception as e:
            print(f"[ERROR] Face processing failed: {e}")

    cv2.imshow("Live CCTV Feed - Face Detection & Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

if os.path.exists("current.jpg"):
    os.remove("current.jpg")

