import os
import cv2
import datetime
import tkinter as tk
from tkinter import ttk, Label, Button, Canvas, Scrollbar
from PIL import Image, ImageTk

# Define paths
PHOTO_DIR = '/home/rpiserver/Pictures/Camera'
os.makedirs(PHOTO_DIR, exist_ok=True)

# Initialize main window
root = tk.Tk()
root.title("Camera Capture and Photo Viewer")
root.geometry("1000x600")
root.configure(bg='#f0f0f0')

# Initialize camera
cap = cv2.VideoCapture(0)

# Capture photo function
def capture_photo():
    ret, frame = cap.read()
    if ret:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        photo_path = os.path.join(PHOTO_DIR, f'photo_{timestamp}.jpg')
        cv2.imwrite(photo_path, frame)
        load_photos()  # Refresh photo list

# Load saved photos
def load_photos():
    for widget in photo_frame.winfo_children():
        widget.destroy()  # Clear previous photos

    photos = sorted(os.listdir(PHOTO_DIR), reverse=True)
    for photo in photos:
        photo_path = os.path.join(PHOTO_DIR, photo)
        img = Image.open(photo_path)
        img.thumbnail((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        
        # Create label for each photo
        lbl = Label(photo_frame, image=img_tk, cursor="hand2", borderwidth=2, relief="solid")
        lbl.image = img_tk  # Keep a reference to prevent garbage collection
        lbl.pack(pady=5)
        lbl.bind("<Button-1>", lambda e, p=photo_path: open_photo(p))

# Open selected photo in new window
def open_photo(photo_path):
    new_win = tk.Toplevel(root)
    new_win.title("Photo Viewer")

    img = Image.open(photo_path)
    img_tk = ImageTk.PhotoImage(img)
    lbl = Label(new_win, image=img_tk)
    lbl.image = img_tk
    lbl.pack()

# Display live camera feed
def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (640, 480))
        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(img)
        camera_label.config(image=img_tk)
        camera_label.image = img_tk
    root.after(10, update_frame)

# Create UI elements
camera_label = Label(root, borderwidth=2, relief="solid")
camera_label.place(x=20, y=20)

capture_button = Button(root, text="Capture Photo", command=capture_photo, bg='#4CAF50', fg='white')
capture_button.place(x=270, y=520)

# Create photo preview area
photo_frame = tk.Frame(root, bg='#f0f0f0')
canvas = Canvas(photo_frame)
scrollbar = Scrollbar(photo_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

photo_frame.place(x=700, y=20, width=280, height=560)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
photo_frame = scrollable_frame

# Load existing photos
load_photos()

# Start updating camera feed
update_frame()

# Run the Tkinter main loop
root.mainloop()

# Release camera resource
cap.release()
