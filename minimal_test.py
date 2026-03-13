import face_recognition

print("Loading test.jpg...")
image = face_recognition.load_image_file("test.jpg")
print(f"Image shape: {image.shape}, dtype: {image.dtype}")

face_locations = face_recognition.face_locations(image)
print(f"Found {len(face_locations)} faces")

if face_locations:
    encodings = face_recognition.face_encodings(image, face_locations)
    print(f"Generated {len(encodings)} encodings")
else:
    print("No faces detected.")