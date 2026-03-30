import cv2
import numpy as np
import face_recognition
import pickle
import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from .forms import StudentRegistrationForm
from .models import Student, Attendance
from django.http import StreamingHttpResponse
from datetime import date, datetime, timedelta

# 1. The Home Page View
def home(request):
    return render(request, 'home.html')

# 2. The Registration View
def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        base64_data = request.POST.get('base64_image')
        
        if form.is_valid() and base64_data:
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            class_section = form.cleaned_data['class_section']
            
            try:
                # Decode the base64 string
                format, imgstr = base64_data.split(';base64,') 
                ext = format.split('/')[-1]
                img_bytes = base64.b64decode(imgstr)

                # Process with OpenCV
                nparr = np.frombuffer(img_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                image_rgb = np.ascontiguousarray(image_rgb)
                # Generate Encoding
                encodings = face_recognition.face_encodings(image_rgb)

                if encodings:
                    file_name = f"{name.replace(' ', '_')}_{class_section.replace(' ', '')}.{ext}"
                    django_file = ContentFile(img_bytes, name=file_name)

                    # Save EVERYTHING to the Student table
                    student = Student(
                        name=name,
                        email=email,
                        class_section=class_section,
                        photo=django_file,
                        encoding=pickle.dumps(encodings[0])
                    )
                    student.save()
                    
                    # On success, send them back to the Home page
                    return redirect('home') 
                else:
                    form.add_error(None, 'No face detected! Please ensure you are looking at the camera.')
                    
            except Exception as e:
                form.add_error(None, f'Error processing image: {str(e)}')
        else:
            if not base64_data:
                form.add_error(None, 'Please take a photo using the camera before submitting.')

    else:
        form = StudentRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

# 3. The Live Attendance Page View
def live_attendance(request):
    return render(request, 'attendance.html')

# Keep your gen_frames() and video_feed() functions exactly as they are below this!
# --- MISSING FUNCTIONS RESTORED ---

def gen_frames():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # 1. THE SETUP
    known_students = list(Student.objects.all())
    known_face_encodings = []
    known_face_names_db = [] 

    for student in known_students:
        try:
            encoding = pickle.loads(student.encoding) 
            known_face_encodings.append(encoding)
            known_face_names_db.append(f"{student.name} ({student.class_section})")
        except Exception as e:
            print(f"Error loading encoding for {student.name}: {e}")

    # ==========================================
    # --- NEW 1-HOUR COOLDOWN MEMORY ---
    # ==========================================
    last_marked_dict = {}
    
    # Pre-load today's records so the 1-hour cooldown survives if you restart the server
    today = date.today()
    for record in Attendance.objects.filter(date=today):
        # Combine the date and time from the database into one datetime object
        record_dt = datetime.combine(record.date, record.time)
        if record.student.id not in last_marked_dict or record_dt > last_marked_dict[record.student.id]:
            last_marked_dict[record.student.id] = record_dt

    # --- ANTI-LAG VARIABLES ---
    process_this_frame = True
    current_face_locations = []
    current_face_names = []
    current_box_colors = []

    try:
        while True:
            success, frame = camera.read()
            if not success or frame is None:
                break

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            clean_rgb_frame = np.array(rgb_small_frame, dtype='uint8', order='C').copy()

            if process_this_frame:
                current_face_locations = face_recognition.face_locations(clean_rgb_frame)
                face_encodings = face_recognition.face_encodings(clean_rgb_frame, current_face_locations)

                current_face_names = []
                current_box_colors = []

                for face_encoding in face_encodings:
                    name = "Unknown"
                    box_color = (0, 0, 255) # Red for Unknown

                    if known_face_encodings:
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

                        if len(face_distances) > 0:
                            best_match_index = np.argmin(face_distances)
                            
                            if matches[best_match_index]:
                                matched_student = known_students[int(best_match_index)]
                                base_name = known_face_names_db[best_match_index]
                                
                                # ==========================================
                                # 5. MARK ATTENDANCE (1-Hour Check)
                                # ==========================================
                                now = datetime.now()
                                student_id = matched_student.id
                                
                                # Check if they are NOT in the dictionary, OR if 1 hour has passed
                                if student_id not in last_marked_dict or (now - last_marked_dict[student_id]) >= timedelta(hours=1):
                                    Attendance.objects.create(student=matched_student)
                                    last_marked_dict[student_id] = now
                                    name = base_name + " [LOGGED]"
                                    box_color = (0, 255, 100) # Bright Green for successful log
                                else:
                                    # They are in cooldown. Don't log to DB, just update UI.
                                    name = base_name + " [Active]"
                                    box_color = (255, 200, 0) # Cyan/Yellow to show they are already logged

                    current_face_names.append(name)
                    current_box_colors.append(box_color)

            process_this_frame = not process_this_frame

            # 6. DRAW THE PRO HUD (Keep this exactly the same as your current code)
            for (top, right, bottom, left), name, box_color in zip(current_face_locations, current_face_names, current_box_colors):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                thickness = 2
                length = 25
                
                cv2.line(frame, (left, top), (left + length, top), box_color, thickness)
                cv2.line(frame, (left, top), (left, top + length), box_color, thickness)
                cv2.line(frame, (right, top), (right - length, top), box_color, thickness)
                cv2.line(frame, (right, top), (right, top + length), box_color, thickness)
                cv2.line(frame, (left, bottom), (left + length, bottom), box_color, thickness)
                cv2.line(frame, (left, bottom), (left, bottom - length), box_color, thickness)
                cv2.line(frame, (right, bottom), (right - length, bottom), box_color, thickness)
                cv2.line(frame, (right, bottom), (right, bottom - length), box_color, thickness)

                overlay = frame.copy()
                cv2.rectangle(overlay, (left, bottom + 10), (right, bottom + 45), (20, 20, 20), cv2.FILLED)
                cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
                
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 8, bottom + 35), font, 0.6, (255, 255, 255), 1)

            # 7. COMPRESS & SEND
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
    except Exception as e:
        print(f"Camera stream stopped: {e}")
    finally:
        print("Releasing camera hardware...")
        camera.release()
        

def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

# Add this new view to the bottom of views.py
def view_records(request):
    # Fetch all attendance records, ordering by the newest first
    # .select_related('student') is a speed optimization to prevent database lag
    attendance_logs = Attendance.objects.select_related('student').order_by('-date', '-time')
    
    return render(request, 'records.html', {'logs': attendance_logs})