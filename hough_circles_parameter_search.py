import cv2
import os
import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from PIL import Image, ImageTk

class Application():
    def __init__(self):
        height = 1000
        width = 1500
        images = []
        tkImages = []
        self.selected = 0

        self.param1_val = 50
        self.param2_val = 100
        self.minRadius_val = 0
        self.maxRadius_val = 0
        self.cannyNum_val = 100
        self.centerDistance_val = 50

        root = tk.Tk()
        canvas_frame = tk.Frame(root, height=height, width=width)
        canvas_frame.pack()
        canvas = tk.Canvas(canvas_frame, height=461, width=614)
        canvas.pack()
        input_frame = tk.Frame(canvas_frame, height=height/2, width=width)
        input_frame.pack()

        for file in os.listdir("Test_images/"):
            #images.append(cv2.imread("Test_images/" + file))
            tkImages.append(Image.open("Test_images/" + file))


        for i in range(len(tkImages)):
            tkImages[i] = tkImages[i].resize((614, 461), Image.ANTIALIAS)
            images.append(np.array(tkImages[i]))
            tkImages[i] = ImageTk.PhotoImage(tkImages[i])

        canvas.create_image(0, 0, anchor=tk.NW, image=tkImages[self.selected])

        def set_param1(v):
            self.param1_val = int(float(v))
            param1_var.set(self.param1_val)
            Hough_circles(images[self.selected])

        def set_param2(v):
            self.param2_val = int(float(v))
            param2_var.set(self.param2_val)
            Hough_circles(images[self.selected])

        def set_minRadius(v):
            self.minRadius_val = int(float(v))
            minRadius_var.set(self.minRadius_val)
            Hough_circles(images[self.selected])

        def set_maxRadius(v):
            self.maxRadius_val = int(float(v))
            maxRadius_var.set(self.maxRadius_val)
            Hough_circles(images[self.selected])

        def set_cannyNum(v):
            self.cannyNum_val = int(float(v))
            cannyNum_var.set(self.cannyNum_val)
            Hough_circles(images[self.selected])

        def set_centerDistance(v):
            self.centerDistance_val = int(float(v))
            centerDistance_var.set(self.centerDistance_val)
            Hough_circles(images[self.selected])

        param1 = ttk.Scale(input_frame, from_=0, to=1000, command = set_param1)
        param1.set(self.param1_val)
        param1_var = tk.StringVar(root)
        param1_var.set(self.param1_val)
        param1_entry = ttk.Entry(input_frame, textvariable=param1_var, width=5)

        param2 = ttk.Scale(input_frame, from_=0, to=1000, command=set_param2)
        param2.set(self.param2_val)
        param2_var = tk.StringVar(root)
        param2_var.set(self.param2_val)
        param2_entry = ttk.Entry(input_frame, textvariable=param2_var, width=5)

        minRadius = ttk.Scale(input_frame, from_=0, to=1000, command=set_minRadius)
        minRadius.set(self.minRadius_val)
        minRadius_var = tk.StringVar(root)
        minRadius_var.set(self.minRadius_val)
        minRadius_entry = ttk.Entry(input_frame, textvariable=minRadius_var, width=5)

        maxRadius = ttk.Scale(input_frame, from_=0, to=1000, command=set_maxRadius)
        maxRadius.set(self.maxRadius_val)
        maxRadius_var = tk.StringVar(root)
        maxRadius_var.set(self.maxRadius_val)
        maxRadius_entry = ttk.Entry(input_frame, textvariable=maxRadius_var, width=5)

        cannyNum = ttk.Scale(input_frame, from_=0, to=1000, command = set_cannyNum)
        cannyNum.set(self.cannyNum_val)
        cannyNum_var = tk.StringVar(root)
        cannyNum_var.set(self.cannyNum_val)
        cannyNum_entry = ttk.Entry(input_frame, textvariable=cannyNum_var, width=5)

        centerDistance = ttk.Scale(input_frame, from_=0, to=1000, command = set_centerDistance)
        centerDistance.set(self.centerDistance_val)
        centerDistance_var = tk.StringVar(root)
        centerDistance_var.set(self.centerDistance_val)
        centerDistance_entry = ttk.Entry(input_frame, textvariable=centerDistance_var, width=5)

        param1.grid(row=0, column=1)
        tk.Label(input_frame, text="Canny Upper Threshold (Param1)").grid(row=0, column=0)
        param1_entry.grid(row=0, column=2)

        param2.grid(row=1, column=1)
        tk.Label(input_frame, text="Accumulator Threshold (Param2)").grid(row=1, column=0)
        param2_entry.grid(row=1, column=2)

        minRadius.grid(row=2, column=1)
        tk.Label(input_frame, text="Minimum Radius").grid(row=2, column=0)
        minRadius_entry.grid(row=2, column=2)

        maxRadius.grid(row=3, column=1)
        tk.Label(input_frame, text="Maximum Radius").grid(row=3, column=0)
        maxRadius_entry.grid(row=3, column=2)

        cannyNum.grid(row=4, column=1)
        tk.Label(input_frame, text="Canny Number").grid(row=4, column=0)
        cannyNum_entry.grid(row=4, column=2)

        centerDistance.grid(row=5, column=1)
        tk.Label(input_frame, text="Distance between centers").grid(row=5, column=0)
        centerDistance_entry.grid(row=5, column=2)

        def enter_param1(event):
            value = param1_var.get()
            v = int(float(value))
            self.param1_val = v
            param1.set(v)
            Hough_circles(images[self.selected])

        param1_entry.bind("<Return>", enter_param1)

        def enter_param2(event):
            value = param2_var.get()
            v = int(float(value))
            self.param2_val = v
            param2.set(v)
            Hough_circles(images[self.selected])

        param2_entry.bind("<Return>", enter_param2)

        def enter_minRadius(event):
            value = minRadius_var.get()
            v = int(float(value))
            self.minRadius_val = v
            minRadius.set(v)
            Hough_circles(images[self.selected])

        minRadius_entry.bind("<Return>", enter_minRadius)

        def enter_maxRadius(event):
            value = maxRadius_var.get()
            v = int(float(value))
            self.maxRadius_val = v
            maxRadius.set(v)
            Hough_circles(images[self.selected])

        maxRadius_entry.bind("<Return>", enter_maxRadius)

        def enter_cannyNum(event):
            value = cannyNum_var.get()
            v = int(float(value))
            self.cannyNum_val = v
            cannyNum.set(v)
            Hough_circles(images[self.selected])

        cannyNum_entry.bind("<Return>", enter_cannyNum)

        def enter_centerDistance(event):
            value = centerDistance_var.get()
            v = int(float(value))
            self.centerDistance_val = v
            centerDistance.set(v)
            Hough_circles(images[self.selected])

        centerDistance_entry.bind("<Return>", enter_centerDistance)

        def draw_circles(circles):
            canvas.delete("all")
            canvas.create_image(0, 0, anchor=tk.NW, image=tkImages[self.selected])
            circles = np.round(circles[0, :]).astype("int")
            circle_num = 0
            for(x,y,r) in circles:
                circle_num += 1
                canvas.create_oval(x-r, y-r, x+r, y+r, outline="#ee0000")
            print(circle_num)

        def reset():
            canvas.delete("all")
            canvas.create_image(0, 0, anchor=tk.NW, image=tkImages[self.selected])

        def Hough_circles(image):
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, self.centerDistance_val, param1=self.param1_val,
                                    param2=self.param2_val, minRadius=self.minRadius_val, maxRadius=self.maxRadius_val)
            if circles is not None:
                if len(circles) > 100:
                    print("too many")
                    return
                draw_circles(circles)
            else:
                reset()


        def iterate_right():
            if self.selected == len(images)-1:
                self.selected = 0
            else:
                self.selected += 1
            Hough_circles(images[self.selected])

        def iterate_left():
            if self.selected == 0:
                self.selected = len(images)-1
            else:
                self.selected -= 1
            Hough_circles(images[self.selected])

        right_button = tk.Button(input_frame, text="Right", command=iterate_right)
        left_button = tk.Button(input_frame, text="Left", command=iterate_left)
        right_button.grid(row=2, column=5)
        left_button.grid(row=2, column=4)

        root.mainloop()

if __name__ == '__main__':
    app = Application()