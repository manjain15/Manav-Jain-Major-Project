import tkinter as tk


root = tk.Tk()
# create a grid of 2x6
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
for i in range(6):
    root.columnconfigure(i, weight=1)

# by playing around with columnspan, you can get the layout that you need
button1 = tk.Button(root, text='1')
button1.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
button2 = tk.Button(root, text='2')
button2.grid(row=0, column=2, columnspan=2, sticky=tk.NSEW)
button3 = tk.Button(root, text='3')
button3.grid(row=0, column=4, columnspan=2, sticky=tk.NSEW)
button4 = tk.Button(root, text='4')
button4.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)
button5 = tk.Button(root, text='5')
button5.grid(row=1, column=3, columnspan=3, sticky=tk.NSEW)

root.mainloop()