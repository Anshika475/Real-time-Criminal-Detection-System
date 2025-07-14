import face_recognition
import os
import pickle

KNOWN_FACES_DIR = "criminal_photos"  # Changed from criminal_faces
ENCODINGS_FILE = "known_encodings.pkl"

known_encodings = []
known_names = []

print(">>> Script started...")

# Check if the folder exists
if not os.path.exists(KNOWN_FACES_DIR):
    print(f"[ERROR] Folder '{KNOWN_FACES_DIR}' does not exist.")
    exit()

# Get all files
files = os.listdir(KNOWN_FACES_DIR)
print(f">>> Found {len(files)} file(s) in {KNOWN_FACES_DIR}")

if not files:
    print("[WARNING] No image files found in the directory.")
    exit()

# Loop through each image
for filename in files:
    print(f"[INFO] Checking file: {filename}")
    image_path = os.path.join(KNOWN_FACES_DIR, filename)
    
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])
            print(f"✔ Encoded: {filename}")
        else:
            print(f"✖ No face found in: {filename}")

    except Exception as e:
        print(f"[ERROR] Could not process {filename} — {e}")

# Save encodings
if known_encodings:
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump((known_encodings, known_names), f)
    print(f"[DONE] Encoded {len(known_names)} face(s) saved to '{ENCODINGS_FILE}'")
else:
    print("[FAIL] No encodings generated.")
