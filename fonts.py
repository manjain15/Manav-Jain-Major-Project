import tkinter as tk
from tkinter import font as tkfont

# Create the main application window
root = tk.Tk()
root.title("Custom Font Example")

# Create a custom font object
custom_font = tkfont.Font(family="Calgary", size=12, weight="normal")

# Create a label with the custom font
label = tk.Label(root, text="This is text with the Calgary font", font=custom_font)
label.pack(pady=20)

# Create a button with the custom font
button = tk.Button(root, text="Click Me", font=custom_font, command=root.destroy)
button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
