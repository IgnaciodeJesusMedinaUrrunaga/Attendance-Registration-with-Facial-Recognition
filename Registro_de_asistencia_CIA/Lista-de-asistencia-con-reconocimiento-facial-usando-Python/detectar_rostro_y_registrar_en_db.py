import face_recognition
import cv2
import numpy as np
import mysql.connector
from datetime import datetime
import os

# Establece conexión con la base de datos MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="root",
    database="asistencia_del_cia"
)
db_cursor = db_connection.cursor()

# Crea la tabla 'registro' si no existe en la base de datos
create_table_query = """
CREATE TABLE IF NOT EXISTS registro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    hora TIME NOT NULL
);
"""
db_cursor.execute(create_table_query)

# Listas para almacenar encodings y nombres de caras conocidas
known_face_encodings = []
known_face_names = []
# Dirección de la carpeta con las imágenes de las personas conocidas
destiny_path = r"C:\Users\Ignacio\Desktop\Toma-de-Asistencia-con-Reconocimiento-Facial\AsistenciaCIA\Imagenes"

# Recorre las imágenes en la carpeta especificada y genera encodings
for filename in os.listdir(destiny_path):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image = face_recognition.load_image_file(os.path.join(destiny_path, filename))
        face_encoding = face_recognition.face_encodings(image)
        if face_encoding:
            known_face_encodings.append(face_encoding[0])
            known_face_names.append(filename.split(".")[0])
        else:
            print(f"No se pudo encontrar un rostro en {filename}")

# Inicializa variables para el reconocimiento facial
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Accede a la webcam del dispositivo
video_capture = cv2.VideoCapture(0)

while True:
    # Captura la imagen actual de la webcam
    ret, frame = video_capture.read()

    # Procesa solo algunos frames para optimizar la velocidad
    if process_this_frame:
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Identifica caras en la imagen
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # Compara la cara detectada con las caras conocidas
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            # Si la cara no es reconocida (no esta en destiny_path), la etiqueta por defecto es "Desconocido"
            name = "Desconocido"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                # Obtiene la fecha y hora actual
                now = datetime.now()
                current_date = now.date()
                current_time = now.time()

                # Verifica si la persona ya fue registrada en el día
                check_query = "SELECT * FROM registro WHERE nombre = %s AND fecha = %s"
                db_cursor.execute(check_query, (name, current_date))
                result = db_cursor.fetchone()

                if not result:
                    # Si no fue registrada, agrega un nuevo registro en la base de datos
                    insert_query = "INSERT INTO registro (fecha, nombre, hora) VALUES (%s, %s, %s)"
                    db_cursor.execute(insert_query, (current_date, name, current_time))
                    db_connection.commit()
                else:
                    print(f"{name} Ya ha sido registrado el dia de hoy")

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Muestra el resultado en la ventana
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow('Video', frame)

    # Si se presiona la tecla 'q', finaliza el programa
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera la webcam y cierra las ventanas
video_capture.release()
cv2.destroyAllWindows()
