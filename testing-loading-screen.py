import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter import PhotoImage
import threading
import time
import unittest

# Import the code to be tested
from main import *

class TestLoadingScreen(unittest.TestCase):
    def setUp(self):
        # Create a Tkinter window
        self.root = tk.Tk()
        self.root.title("ViewTrip")
        self.root.geometry("600x200")
        self.root.eval("tk::PlaceWindow . center")
        self.root.configure(bg="white")

        # Set up GUI elements
        global loading_label, bus_sprite, progress_bar
        global_font = tkfont.Font(family="Canela Text Trial", size=18, weight="bold")
        self.root.option_add("*Font", global_font)

        loading_label = tk.Label(self.root, text="Obtaining real-time data...", bg="white", fg="black")
        loading_label.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=600, height=100, bg='white', highlightthickness=0)
        self.canvas.pack(pady=10)

        bus_image_path = "start_screen_logo.png"
        bus_image = tk.PhotoImage(file=bus_image_path)
        bus_sprite = self.canvas.create_image(50, 50, image=bus_image, anchor=tk.CENTER)

        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(self.root, length=300, variable=progress_var, maximum=100)
        progress_bar.pack(pady=13)

    def tearDown(self):
        # Close the Tkinter window after the test
        try:
            self.root.destroy()
        except tk.TclError:
            pass  # If already destroyed, ignore the error

    def test_loading_screen(self):
        # Function to move the bus
        def move_bus(canvas, bus_sprite):
            canvas.move(bus_sprite, 5, 0)  # Move the bus to the right
            # Check if the bus has moved off the screen
            x, _ = canvas.coords(bus_sprite)
            if x > 600:
                canvas.coords(bus_sprite, 50, 50)  # Reset the position
            self.bus_update_after_id = self.root.after(50, move_bus, canvas, bus_sprite)  # Schedule the next movement

        # Start the bus animation
        move_bus(self.canvas, bus_sprite)

        # Start updating the progress bar
        def update_progress():
            if progress_var.get() < 100:
                progress_var.set(progress_var.get() + 10)
                self.root.after(1000, update_progress)
            else:
                if hasattr(self, 'bus_update_after_id'):
                    # Cancel the scheduled update_wheel call before destroying
                    self.root.after_cancel(self.bus_update_after_id)
                self.root.destroy()  # Close the loading screen when complete

        update_progress()

        # Start the Tkinter main event loop
        self.root.mainloop()

        # Check if the loading label is no longer displayed after application is destroyed
        loading_label_exists = hasattr(self, 'loading_label') and loading_label.winfo_exists()
        print("Input: Loading label exists before destroying:", hasattr(self, 'loading_label'))
        print("Output: Loading label exists after destroying:", loading_label_exists)
        self.assertFalse(loading_label_exists)

        # Check if the bus image is no longer displayed after application is destroyed
        bus_sprite_exists = hasattr(self, 'bus_sprite') and bus_sprite.winfo_exists()
        print("Input: Bus sprite exists before destroying:", hasattr(self, 'bus_sprite'))
        print("Output: Bus sprite exists after destroying:", bus_sprite_exists)
        self.assertFalse(bus_sprite_exists)

        # Check if the progress bar is no longer displayed after application is destroyed
        progress_bar_exists = hasattr(self, 'progress_bar') and progress_bar.winfo_exists()
        print("Input: Progress bar exists before destroying:", hasattr(self, 'progress_bar'))
        print("Output: Progress bar exists after destroying:", progress_bar_exists)
        self.assertFalse(progress_bar_exists)

if __name__ == "__main__":
    unittest.main()
