# 📷 JSSATEN Face Attendance System

An AI-powered biometric attendance tracking system built with Django and OpenCV. This project uses machine learning to perform real-time facial recognition, automatically logging student attendance into a secure SQLite database.

## ✨ Key Features

* **Real-Time Facial Recognition:** Uses the `face_recognition` library (built on dlib) to achieve 99.38% accuracy on the Labeled Faces in the Wild benchmark.

* **Anti-Lag Video Processing:** Implements frame-skipping algorithms to process heavy AI math on alternating frames, keeping the live video feed smooth and lag-free.

* **Smart Cooldown System:** Prevents database spam by enforcing a 1-hour cooldown block. If a student is recognized multiple times within an hour, the system updates the UI to show they are "[Active]" without writing duplicate logs.

* **Modern "Dark Slate" UI:** A fully responsive, custom-built web dashboard featuring a sleek, dark-mode design and an OpenCV "Pro HUD" overlay on the video feed.

* **Secure Database Management:** Replaced traditional CSV logging with a robust SQLite database and a dedicated `/records` dashboard for easy viewing.

## 🛠️ Technology Stack

* **Backend:** Python, Django
* **Computer Vision:** OpenCV, `face_recognition`, `numpy`
* **Database:** SQLite
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)


## 🚀 How to Run Locally

If you want to run this project on your own machine, follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/prashantmishra2505-sketch/Face-Attendance-System.git](https://github.com/prashantmishra2505-sketch/Face-Attendance-System.git)
cd Face-Attendance-System

**2. Create a virtual environment & install dependencies**
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install django opencv-python face_recognition numpy
(Note: face_recognition requires CMake and a C++ compiler installed on your system).

**3. Run Database Migrations**
python manage.py makemigrations
python manage.py migrate

**4. Start the Server**
python manage.py runserver
