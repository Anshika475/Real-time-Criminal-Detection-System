

import mysql.connector
import os

# Create a folder to save all images
os.makedirs("criminal_photos", exist_ok=True)

# Connect to the remote MySQL database
conn = mysql.connector.connect(
    host='192.168.137.4',       # Replace with your actual IP
    user='Anshika',
    password='remoteuser123',
    database='mydb',
    port=3306
)

cursor = conn.cursor()

# Fetch all criminal names and photos
cursor.execute("SELECT Criminal_id, name, photo FROM Criminal")

for criminal_id, name, photo in cursor.fetchall():
    print(f"👤 Criminal ID: {criminal_id} | Name: {name}")

    # Save each photo with a unique filename
    filename = f"criminal_photos/{criminal_id}{name.replace(' ', '')}.jpg"
    with open(filename, "wb") as file:
        file.write(photo)
    print(f"📸 Photo saved as {filename}\n")

cursor.close()
conn.close()
print("✅ All records retrieved and saved.")
