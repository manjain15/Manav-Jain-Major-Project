# Import Required Library
from tkinter import *
from tkcalendar import Calendar
import datetime
from datetime import date

today = datetime.date.today()
year = today.year
month = today.month
day = today.day

# Create Object
root = Tk()

# Set geometry
root.geometry("400x400")

# Add Calendar
cal = Calendar(root, selectmode = 'day',
			year = year, month = month,
			day = day, date_pattern = "yyyyMMdd")

cal.pack(pady = 20)

def grad_date():
	date.config(text = "Selected Date is: " + cal.get_date())

# Add Button and Label
Button(root, text = "Get Date",
	command = grad_date).pack(pady = 20)

date = Label(root, text = "")
date.pack(pady = 20)

# Execute Tkinter
root.mainloop()
