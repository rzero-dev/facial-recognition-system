from tkinter import *
import pandas as pd
import tkinter as tk
from playsound import playsound
from PIL import Image, ImageTk
import numpy as np
from tkinter import ttk
import sqlite3
import cv2
from PIL import Image
import os
import xlsxwriter
from datetime import date
from tkinter import messagebox
import sys
import random


# =====================Create Database=============================================
def createdb():
    conn = sqlite3.connect('saveddata.db')
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS users (name TEXT , passs TEXT,sqltime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)")
    conn.commit()
    conn.close()


createdb()
window2 = Tk()
f1 = Frame(window2)
f2 = Frame(window2)
f3 = Frame(window2)
f4 = Frame(window2)


def swap(frame):
    frame.tkraise()


for frame in (f1, f2, f3, f4):
    frame.place(x=0, y=0, width=400, height=400)
window2.geometry("400x400+420+170")
window2.resizable(False, False)
label3 = Label(f1, text="", font=("arial", 20, "bold"), bg="grey16", fg="white", relief=SUNKEN)
label3.pack(side=TOP, fill=X)

label4 = Label(f2, text="FaceIDapp | Sistema de Reconocimiento Facial", font=("arial", 10, "bold"), bg="black", fg="green")
label4.pack(side=BOTTOM, fill=X)
statusbar = Label(f1, text="Sistema de Reconocimiento Facial", font=("arial", 8, "bold"), bg="black", fg="green",
                  relief=SUNKEN, anchor=W)
statusbar.pack(side=BOTTOM, fill=X)


label4 = Label(f3, text="FaceIDapp | Sistema de Reconocimiento Facial", font=("arial", 10, "bold"), bg="black", fg="green")
label4.pack(side=BOTTOM, fill=X)


# ================================Train System===========================================================


def trainsystem():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    path = 'basededatos'
    if not os.path.exists('./recognizer'):
        os.makedirs('./recognizer')

    def getImagesWithID(path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faces = []
        IDs = []
        for imagePath in imagePaths:
            faceImg = Image.open(imagePath).convert('L')
            faceNp = np.array(faceImg, 'uint8')
            ID = int(os.path.split(imagePath)[-1].split('.')[1])
            faces.append(faceNp)
            IDs.append(ID)
            cv2.imshow("Cargando...", faceNp)
            cv2.waitKey(10)
        return np.array(IDs), faces

    Ids, faces = getImagesWithID(path)
    recognizer.train(faces, Ids)
    recognizer.save('recognizer/trainingData.yml')
    statusbar['text'] = 'Entrenando el sistema...'
    cv2.destroyAllWindows()


# ==============================Detector/Attendence======================================================

def markattendance():
    if not os.path.exists('./Attendance'):
        os.makedirs('./Attendance')
    statusbar['text'] = 'Asistencia marcada...'
    conn = sqlite3.connect('basededatos.db')
    c = conn.cursor()
    fname = "recognizer/trainingData.yml"
    if not os.path.isfile(fname):
        print("Debe entrenar el sistema")
        exit(0)
    face_cascade = cv2.CascadeClassifier('./Resources/haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(fname)
    while True:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)
            ids, conf = recognizer.predict(gray[y:y + h, x:x + w])
            c.execute("select Nombre from Estudiante where id = (?);", (ids,))
            result = c.fetchall()
            name = result[0][0]
            rname = str(name)
            if conf < 50:
                cv2.putText(img, name, (x + 2, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(img, 'Bienvenido' ' ' + name, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (255, 255, 255), 2)
            else:
                cv2.putText(img, 'n/a', (x + 2, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Reconocimiento Facial', img)
        k = cv2.waitKey(30) & 0xff
        if k == 13:
            c.execute("SELECT * FROM Estudiante")
            student_result = c.fetchall()
            stat = str(student_result)
            time = str(date.today())
            df = pd.DataFrame(student_result, columns=['id', 'Nombre', 'Matricula', 'Carrera'])
            datatoexcel = pd.ExcelWriter("./Attendance/Employee Attendance" + time + ".xlsx", engine='xlsxwriter')
            df.to_excel(datatoexcel, index=False, sheet_name="Sheet1")
            worksheet = datatoexcel.sheets['Sheet1']

            worksheet.set_column('A:A', 8)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 20)
            worksheet.set_column('F:F', 20)
            df.loc[stat, 'Status'] = 'present'
            # df.at[0,'status']= 'present'
            # df.set_value(stat, 'E','present')
            # df.set_value(rname, 'status','present')
            datatoexcel.save()
            playsound('./Resources/sound.mp3')
            break
    cap.release()
    conn.commit()
    conn.close()
    cv2.destroyAllWindows()


# ================================Register=================================================================

label5 = Label(f2, text="Registrar estudiante", font=("arial", 20, "bold"), bg="grey16", fg="white")
label5.pack(side=TOP, fill=X)

label6 = Label(f2, text="Nombre", font=("arial", 10, "bold"))
label6.place(x=70, y=70)
entry6 = StringVar()
entry6 = ttk.Entry(f2, textvariable=entry6)
entry6.place(x=170, y=70)
entry6.focus()

label7 = Label(f2, text="Carrera", font=("arial", 10, "bold"))
label7.place(x=70, y=100)
entry7 = StringVar()
combo = ttk.Combobox(f2, textvariable=entry7, width=15, font=("arial", 10, "bold"), state='readonly')
combo['values'] = (
"Tecnologo en Software", "Tecnologo en Multimedia", "Tecnologo en Mecatronica", "Tecnologo en Redes", "Tecnologo en Manufactura",
"Tecnologo en Sonido", "Tecnologo en Videojuegos")
combo.place(x=170, y=100)
label8 = Label(f2, text="Matricula", font=("arial", 10, "bold"))
label8.place(x=70, y=150)
entry8 = StringVar()
entry8 = ttk.Entry(f2, textvariable=entry8)
entry8.place(x=170, y=150)

btn1w2 = ttk.Button(f1, text="Registrar estudiante", command=lambda: swap(f2))
btn1w2.place(x=40, y=60, width=150, height=30)

btn2w2 = ttk.Button(f1, text="Entrenar sistema", command=trainsystem)
btn2w2.place(x=40, y=115, width=150, height=30)

btn3w2 = ttk.Button(f1, text="Reconocimiento", command=markattendance)
btn3w2.place(x=40, y=170, width=150, height=30)


# ======================Record_images_with_database======================================

def capture_images():
    conn = sqlite3.connect('basededatos.db')
    c = conn.cursor()
    sql = """;
					CREATE TABLE IF NOT EXISTS Estudiante (
								id integer unique primary key autoincrement,
								name text,dept text,contactno text,Status text
					);
					"""
    c.executescript(sql)
    if not os.path.exists('./basededatos'):
        os.makedirs('./basededatos')
    uname = entry6.get()
    up1 = uname.upper()
    dep = entry7.get()
    cont = entry8.get()
    if uname == "":
        messagebox.showerror("Error", "Ingrese el nombre del estudiante")
    elif dep == "":
        messagebox.showerror("Error", "Ingrese la carrera")
    elif cont == "":
        messagebox.showerror("Error", "Ingrese la matricula")
    else:
        c.execute('INSERT INTO Estudiante (Nombre,Matricula,Carrera) VALUES (?,?,?)', (up1, dep, cont))
        uid = c.lastrowid
        face_classifier = cv2.CascadeClassifier("./Resources/haarcascade_frontalface_default.xml")

        def face_extractor(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray, 1.2, 7)
            if faces is ():
                return None
            for (x, y, w, h) in faces:
                cropped_face = img[y:y + h, x:x + w]
            return cropped_face

        cap = cv2.VideoCapture(0)
        count = 0
        while True:
            ret, frame = cap.read()
            if face_extractor(frame) is not None:
                count += 1
                face = cv2.resize(face_extractor(frame), (400, 400))
                face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                file_name_path = "basededatos/" + up1 + "." + str(uid) + "." + str(count) + ".jpg"
                cv2.imwrite(file_name_path, face)
                cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
                cv2.imshow("Capturador de imagenes faciales", face)
            else:
                print("Rostro no encontrado")
                pass
            if cv2.waitKey(1) == 13 or count == 70:
                break
        cap.release()
        conn.commit()
        conn.close()
        statusbar['text'] = 'El estudiante ha sido registrado...'
        cv2.destroyAllWindows
        messagebox.showinfo("Information", "Las imagenes se han almacenado correctamente.")


btn5w2 = ttk.Button(f2, text="Capturar y guardar", command=capture_images)
btn5w2.place(x=170, y=200, width=130, height=30)

btn4w2 = ttk.Button(f2, text="Volver", command=lambda: swap(f1))
btn4w2.place(x=3, y=40, width=50, height=30)


def swap2(frame):
    frame.tkraise()


btn7w2 = ttk.Button(f3, text="Volver", command=lambda: swap(f1))
btn7w2.place(x=3, y=40, width=50, height=30)

btn6w2 = ttk.Button(f1, text="Ver estudiantes registrados", command=lambda: swap2(f3))
btn6w2.place(x=210, y=60, width=150, height=30)

# =========================Window2Frame4DevelopersPage=========================================

label10 = Label(f4, text="Informacion", font=("arial", 20, "bold"), bg="black", fg="green")
label10.pack(side=TOP, fill=X)
label11 = Label(f4, text="Desarrollado por Roosvelt y Lemuel", font=("arial", 10, "bold"), bg="black", fg="blue")
label11.pack(side=BOTTOM, fill=X)

label10 = Label(f4, text="Sistema de reconocimiento facial para estudiantes", font=("arial", 12, "bold"))
label10.place(x=10, y=125)


def swap4(frame):
    frame.tkraise()
    statusbar['text'] = 'Sistema de Reconocimiento Facial'


btn4w2 = ttk.Button(f4, text="Volver", command=lambda: swap4(f1))
btn4w2.place(x=3, y=40, width=50, height=30)


def swap3(frame):
    frame.tkraise()


btn9w2 = ttk.Button(f1, text="Informacion", command=lambda: swap3(f4))
btn9w2.place(x=210, y=115, width=150, height=30)


def quit():
    window2.destroy()


btn9w2 = ttk.Button(f1, text="Salir", command=quit)
btn9w2.place(x=210, y=170, width=150, height=30)


# ===========================FETCHDATABASEINLISTVIEW=========================================


def fetch():
    conn = sqlite3.connect("basededatos.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM Estudiante")
    rows=""
    rows = cur.fetchall()
    for row in rows:
        List_Table.insert("", tk.END, values=row)
    conn.close()


# ==========================RecordfromDatabase=========================================

btn8w2 = ttk.Button(f3, text="Ver estudiantes", command=fetch)
btn8w2.place(x=140, y=320, width=130, height=30)


# ================================Frame3LISTVIEW==========================================


label8 = Label(f3, text="Estudiantes guardados", font=("arial", 20, "bold"), bg="grey16", fg="white")
label8.pack(side=TOP, fill=X)

Detail_Frame = Frame(f3, bd=4, relief=RIDGE, bg="purple")
Detail_Frame.place(x=8, y=100, width=385, height=200)
scroll_x = Scrollbar(Detail_Frame, orient=HORIZONTAL)
scroll_y = Scrollbar(Detail_Frame, orient=VERTICAL)
List_Table = ttk.Treeview(Detail_Frame, columns=("1", "2", "3", "4", "5"), xscrollcommand=scroll_x.set,
                          yscrollcommand=scroll_y.set)
scroll_x.pack(side=BOTTOM, fill=X)
scroll_y.pack(side=RIGHT, fill=Y)
scroll_x.config(command=List_Table.xview)
scroll_y.config(command=List_Table.yview)
List_Table.heading("1", text="ID")
List_Table.heading("2", text="Nombre")
List_Table.heading("3", text="Carrera")
List_Table.heading("4", text="Matricula")
List_Table['show'] = 'headings'
List_Table.column("1", width=20)
List_Table.column("2", width=100)
List_Table.column("3", width=100)
List_Table.column("4", width=100)
List_Table.column("5", width=100)
List_Table.pack(fill=BOTH, expand=1)

f1.tkraise()
window2.mainloop()
