markdown
# Face Recognition Attendance System

An AI-based attendance system that automatically marks attendance using **face recognition technology**. The system detects and recognizes employee faces through a camera and records attendance in real time. It also provides an **admin dashboard** to manage employees, view logs, and generate reports.

## Features
- Employee face registration
- Real-time face recognition
- Automatic attendance logging
- Admin login and dashboard
- Employee management
- Attendance analytics
- CSV report generation
- Camera monitoring

## Tech Stack
**Backend**
- Python
- Flask
- OpenCV
- face_recognition (dlib)
- NumPy

**Frontend**
- HTML
- CSS
- JavaScript
- React (Dashboard)

**Database**
- MongoDB / JSON storage

## Project Structure

face_recognition_attendance/                                                                                                                            
│                                                                                                                                                                
├── backend/          # Backend logic and routes                                                                                                                  
├── frontend/         # UI templates and static files                                                                                                             
├── ai_model/         # AI training scripts                                                                                                                       
├── face_module/      # Face capture & recognition                                                                                                                
├── data/             # Stored embeddings and attendance                                                                                                          
│                                                                                                                                                                
├── app.py            # Main application                                                                                                                          
├── requirements.txt                                                                                                                                              
└── README.md                                                                                                                                                   


## Installation

1. Clone the repository

git clone [https://github.com/Chandana130604/face_recognition_attendance.git](https://github.com/Chandana130604/face_recognition_attendance.git)
cd face_recognition_attendance

2. Create virtual environment

python -m venv venv

Activate environment (Windows)

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt


4. Run the application
python app.py

Open in browser:
[http://127.0.0.1:5000](http://127.0.0.1:5000)


## How It Works
1. Register employee faces.
2. System captures and stores face embeddings.
3. During login, the camera detects the face.
4. The system compares embeddings with stored data.
5. If matched, attendance is recorded automatically.

## Author
**Chandana A**

GitHub:  
https://github.com/Chandana130604
