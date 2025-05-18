from PIL import Image, ImageTk
import tkinter as tk

root = tk.Tk()
img = Image.open("img/fengqianlogo2.png").resize((48, 48))
tk_img = ImageTk.PhotoImage(img)
label = tk.Label(root, image=tk_img)
label.pack()
root.mainloop()