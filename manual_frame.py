import tkinter as tk
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk
import sys
import gcodesender as gc
import os

# Constants the determine how far along each axis the imager will attempt to move. Should be set lower
# than the actual movement range, and should be adjusted each time the stop screws are changed.
maxX = 115
maxY = 125
maxZ = 100

class ManualFrame(tk.Frame):
    """Defines a tk.Frame containing all the widgets used in manual mode"""

    def __init__(self, master):
        """Initializes all the widgets for the manual mode GUI"""

        self.live = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.app = master.master

        self.app.loading_screen.label.config(text="Creating Manual Frame...")
        self.app.loading_screen.update()

        #go_home(app_master.s)
        time.sleep(2)
        #set_height(self.s)

        screen_width = self.app.screen_width
        screen_height = self.app.screen_height
        tk.Frame.__init__(self, master)


        # Button Frame is the full height and 1/2 the width of the screen
        # located in the bottom left corner
        # Contains the plate selector, well selector, 'custom path' button,
        # and 'GO' button
        self.button_frame = tk.Frame(self, height=(screen_height), width=screen_width / 2, bg="#fff")
        self.button_frame.grid_propagate(0)
        self.button_frame.grid(row=3, column=0, rowspan=6, sticky=tk.SW)

        # Video Frame is 7/9 the height and 1/2 the width of the screen
        # located in the top right corner
        # Contains live feed video as the imager works
        self.video_height = (screen_height/9) * 6
        self.video_width = (screen_width/2)
        self.video_frame = tk.Frame(self, height=self.video_height, width=self.video_width, bg= "#111")
        self.video_frame.grid_propagate(0)
        self.video_frame.grid(row = 0, column = 1, rowspan = 7, sticky=tk.NE)

        # Feedback frame is 2/9 the height and 1/2 the width of the screen
        # loacted in the bottom right corner
        # Contains the progress bar, 'Cancel' button, and output window
        self.feedback_frame = tk.Frame(self, height=(screen_height/9)*3, width=screen_width/2, bg='#222')
        self.feedback_frame.grid_propagate(0)
        self.feedback_frame.grid(row = 7, column = 1, rowspan = 3, sticky=tk.SE)
        self.progress_frame = tk.Frame(self.feedback_frame, height=self.feedback_frame.winfo_height(), width=(self.feedback_frame.winfo_width()/2), bg='#222')
        self.progress_frame.grid_propagate(0)
        self.progress_frame.grid(row=0, column=0, sticky=tk.W)

        #---------------------------------------------------------------------------------------------------------------
        xPad = screen_width/86
        yPad = ((screen_height/9)*6)/126
        style = ttk.Style()

        style.configure("TButton", font=("Sans", "12"))
        style.configure("Bold.TButton", font=("Sans", "12", "bold"), width=3)
        style.configure("Italic.TButton", font=("Sans", "12", "bold"), width=4)

        style.configure("TLabel", font=("Sans", "14"), background="#eeeeee")
        style.configure("Bold.TLabel",  relief="raised", borderwidth=5)
        style.configure("TCombobox", font=("Sans", "14"))
        style.configure("TCheckbutton", background="#eeeeee")
        style.configure("TEntry", font=("Sans", "14"), height="14")
        style.configure("TRadiobutton",  font=("Sans", "12"), background="#eeeeee")


        for i in range(28):
            ttk.Label(self.button_frame, text="", background="white").grid(row=i, column=0, ipady=yPad, ipadx=xPad)
            #ttk.Label(self.button_frame, text="", background="red").grid(row=i, column=19, ipady=yPad, ipadx=xPad)
        for i in range(20):
            ttk.Label(self.button_frame, text="", background="white").grid(row=0, column=i, ipady=yPad, ipadx=xPad)
            #ttk.Label(self.button_frame, text="", background="red").grid(row=27, column=i, ipady=yPad, ipadx=xPad)

        # Creates the background labels
        plate_background = ttk.Label(self.button_frame, text= "", style="Bold.TLabel")
        plate_background.grid(row=1, column=1, rowspan=5, columnspan=9, sticky=tk.N + tk.S + tk.E + tk.W)
        settings_background = ttk.Label(self.button_frame, text="", style="Bold.TLabel")
        settings_background.grid(row=1, column=11, rowspan=5, columnspan=8, sticky=tk.N + tk.S + tk.E + tk.W)
        control_background = ttk.Label(self.button_frame, text="", style="Bold.TLabel")
        control_background.grid(row=7, column=1, rowspan=19, columnspan=18, sticky=tk.N + tk.S + tk.E + tk.W)

        # Creates the widgets for the frame
        self.project = self.app.frames["AutoFrame"].project
        self.project_entry = ttk.Entry(self.button_frame, textvariable=self.project, font=("Sans", "12"))
        entry_label = ttk.Label(self.button_frame, text="*Project code: ")
        entry_label.grid(row=21, column=9, columnspan=5, sticky=tk.E)
        self.project_entry.grid(row=21, column=14, columnspan=6, sticky=tk.W)
        self.target = self.app.frames["AutoFrame"].target
        self.target_entry = ttk.Entry(self.button_frame, textvariable=self.target, font=("Sans", "12"))
        target_label = ttk.Label(self.button_frame, text="*Target name: ")
        target_label.grid(row=22, column=9, columnspan=5, sticky=tk.E)
        self.target_entry.grid(row=22, column=14, columnspan=6, sticky=tk.W)
        self.plate = self.app.frames["AutoFrame"].plate
        self.plate_entry = ttk.Entry(self.button_frame, textvariable=self.plate, font=("Sans", "12"))
        plate_label = ttk.Label(self.button_frame, text="*Plate name: ")
        plate_label.grid(row=23, column=9, columnspan=5, sticky=tk.E)
        self.plate_entry.grid(row=23, column=14, columnspan=6, sticky=tk.W)
        self.date = self.app.frames["AutoFrame"].date
        self.date_entry = ttk.Entry(self.button_frame, textvariable=self.date, font=("Sans", "12"))
        date_label = ttk.Label(self.button_frame, text="*Prep date: ")
        date_label.grid(row=24, column=9, columnspan=5, sticky=tk.E)
        self.date_entry.grid(row=24, column=14, columnspan=6, sticky=tk.W)
        warning_label = ttk.Label(self.button_frame, text= "(Must be 'yyyy-mm-dd' format)", font=("Sans", "12", "italic"))
        warning_label.grid(row=25, column=10, columnspan=11, sticky=tk.N)


        # Create the tray dropdown list and label
        choices = ['Intelli-plate 96-3', 'Greiner 1536']
        self.dropdown = ttk.Combobox(self.button_frame, textvariable=self.app.type, values=choices, state="readonly",
                                     font=("Sans", "16"))
        self.dropdown.bind("<<ComboboxSelected>>", self.app.frames["AutoFrame"].on_field_change)
        ttk.Label(self.button_frame, text='Plate selection', font=("Sans", "14", "bold")).grid(row=1, column=3, columnspan=5)
        self.dropdown.grid(row=2, column=1, columnspan=9, rowspan=2)

        def load():
            self.app.imager.load_tray()
            self.app.open_plate_window()
        self.load_button = ttk.Button(self.button_frame, text="Load new plate", command=load)
        self.load_button.grid(row=4, column=2, columnspan=3)


        def save():
            threading.Thread(target=self.app.save_image, args=()).start()

        self.camera_button = ttk.Button(self.button_frame, text="Save current image", command=save)
        self.camera_button.grid(row = 8, column = 11, columnspan=9)


        ttk.Label(self.button_frame, text="Settings", font=("Sans", "14", "bold")).grid(row=1, column=11, columnspan=8)

        choices = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        slices = ttk.Combobox(self.button_frame, textvariable=self.app.slices, values=choices, state="readonly", width=3)
        slices.grid(row=4, column=17, rowspan=2)
        slice_label = ttk.Label(self.button_frame, text="Slices: ")
        slice_label.grid(row=4, column=14, rowspan=2, columnspan=3, sticky=tk.E)

        lightsVar = tk.IntVar(master)
        self.lights_on_button = ttk.Radiobutton(self.button_frame, text="On", variable=lightsVar, value=1, command=self.app.arduino.lights_on)
        self.lights_on_button.grid(row=2, column=13, sticky=tk.S)
        self.lights_off_button = ttk.Radiobutton(self.button_frame, text="Off", variable=lightsVar, value=0, command=self.app.arduino.lights_off)
        self.lights_off_button.grid(row=3, column=13, sticky=tk.N)
        lights_label = ttk.Label(self.button_frame, text="Lights:")
        lights_label.grid(row=2, column=11, rowspan =2, columnspan=2, sticky=tk.E)
        #lightsVar.set(1) # Begin with lights on



        filterVar = tk.IntVar(master)
        self.green_filter_button = ttk.Radiobutton(self.button_frame, text="Green", variable=filterVar, value=1, command=self.app.arduino.servo_0) #servo_0
        self.green_filter_button.grid(row=2, column=17, columnspan=2, sticky=tk.S + tk.W)
        self.no_filter_button = ttk.Radiobutton(self.button_frame, text="None", variable=filterVar, value=0, command=self.app.arduino.servo_90) #servo_90
        self.no_filter_button.grid(row=3, column=17, columnspan=2, sticky=tk.N + tk.W)
        filter_label = ttk.Label(self.button_frame, text="Filter:")
        filter_label.grid(row=2, column=14, rowspan=2, columnspan=3, sticky=tk.E)
        filterVar.set(0)

        laserVar = tk.IntVar(master)
        self.laser_on_button = ttk.Radiobutton(self.button_frame, text="On", variable=laserVar, value=1, command=self.app.arduino.laser_on)
        self.laser_on_button.grid(row=4, column=13, sticky=tk.S)
        self.laser_off_button = ttk.Radiobutton(self.button_frame, text="Off", variable=laserVar, value=0, command=self.app.arduino.laser_off)
        self.laser_off_button.grid(row=5, column=13, sticky=tk.N)
        laser_label = ttk.Label(self.button_frame, text="Laser:")
        laser_label.grid(row=4, column=11, columnspan=2, rowspan=2, sticky=tk.E)
        laserVar.set(0)



        self.calibrate_button = ttk.Button(self.button_frame, text="Calibrate", command=self.calibrate)
        self.calibrate_button.grid(row = 4, column = 6, columnspan=3)

        # Sliders for camera Temperature and Tint (don't seem to have any significant effect)

        #self.temp_var = tk.StringVar(app_master)
        #self.tint_var = tk.StringVar(app_master)
        #temp, tint = (app_master.cam.get_temperature_tint())
        #self.temp_var.set(temp)
        #self.tint_var.set(tint)
        #self.temp_entry = ttk.Entry(self.button_frame, textvariable = self.temp_var, width=5, font=("Sans", "12"))
        #self.tint_entry = ttk.Entry(self.button_frame, textvariable = self.tint_var, width=5, font=("Sans", "12"))
        #self.temp_entry.grid(row=19, column=4, columnspan=2, sticky=tk.W)
        #self.tint_entry.grid(row=20, column=4, columnspan=2, sticky=tk.W)
        #ttk.Label(self.button_frame, text="Temp: ").grid(row=19, column=1, columnspan=3, sticky=tk.E)
        #ttk.Label(self.button_frame, text="Tint: ").grid(row=20, column=1, columnspan=3, sticky=tk.E)
        #self.temp_scale = ttk.Scale(self.button_frame, from_=2000, to=15000, command=self.set_Temp)
        #self.tint_scale = ttk.Scale(self.button_frame, from_=200, to=2500, command=self.set_Tint)
        #self.temp_scale.grid(row=19, column=5, columnspan=3)
        #self.tint_scale.grid(row=20, column=5, columnspan=3)
        #self.temp_scale.set(int(float(self.temp_var.get())))
        #self.tint_scale.set(int(float(self.tint_var.get())))

        save_camera_button = ttk.Button(self.button_frame, text="Save camera settings", command=self.app.choose_cam_save_file)
        save_camera_button.grid(row=20, column=2, columnspan=4)
        load_camera_button = ttk.Button(self.button_frame, text="Load camera settings", command=self.app.choose_cam_load_file)
        load_camera_button.grid(row=20, column=6, columnspan=4)

        self.hue_var = tk.StringVar(self.app)
        self.hue_var.set(self.app.cam.get_hue())
        self.hue_entry = ttk.Entry(self.button_frame, textvariable = self.hue_var, width=5, font=("Sans", "12"))
        self.hue_entry.grid(row = 21, column = 4, columnspan=2, sticky=tk.W)
        ttk.Label(self.button_frame, text="Hue: ").grid(row=21, column=1, columnspan=3, sticky=tk.E)
        self.hue_scale = ttk.Scale(self.button_frame, from_=-180, to=180, command=self.set_Hue)
        self.hue_scale.grid(row=21, column=5, columnspan=3)
        self.hue_scale.set(int(float(self.hue_var.get())))

        self.saturation_var = tk.StringVar(self.app)
        self.saturation_var.set(self.app.cam.get_saturation())
        self.saturation_entry = ttk.Entry(self.button_frame, textvariable = self.saturation_var, width=5, font=("Sans", "12"))
        self.saturation_entry.grid(row = 22, column = 4, columnspan=2, sticky=tk.W)
        ttk.Label(self.button_frame, text="Saturation: ").grid(row=22, column=1, columnspan=3, sticky=tk.E)
        self.saturation_scale = ttk.Scale(self.button_frame, from_=0, to=255, command=self.set_Saturation)
        self.saturation_scale.grid(row=22, column=5, columnspan=3)
        self.saturation_scale.set(int(float(self.saturation_var.get())))

        self.brightness_var = tk.StringVar(self.app)
        self.brightness_var.set(self.app.cam.get_brightness())
        self.brightness_entry = ttk.Entry(self.button_frame, textvariable = self.brightness_var, width=5, font=("Sans", "12"))
        self.brightness_entry.grid(row = 23, column = 4, columnspan=2, sticky=tk.W)
        ttk.Label(self.button_frame, text="Brightness: ").grid(row=23, column=1, columnspan=3, sticky=tk.E)
        self.brightness_scale = ttk.Scale(self.button_frame, from_=-64, to = 64, command=self.set_Brightness)
        self.brightness_scale.grid(row=23, column=5, columnspan=3)
        self.brightness_scale.set(int(float(self.brightness_var.get())))

        self.contrast_var = tk.StringVar(self.app)
        self.contrast_var.set(self.app.cam.get_contrast())
        self.contrast_entry = ttk.Entry(self.button_frame, textvariable = self.contrast_var, width=5, font=("Sans", "12"))
        self.contrast_entry.grid(row=24, column = 4, columnspan=2, sticky=tk.W)
        ttk.Label(self.button_frame, text="Contrast: ").grid(row=24, column=1, columnspan=3, sticky=tk.E)
        self.contrast_scale = ttk.Scale(self.button_frame, from_=-100, to=100, command = self.set_Contrast)
        self.contrast_scale.grid(row=24, column=5, columnspan=3)
        self.contrast_scale.set(int(float(self.contrast_var.get())))

        self.gamma_var = tk.StringVar(self.app)
        self.gamma_var.set(self.app.cam.get_gamma())
        self.gamma_entry = ttk.Entry(self.button_frame, textvariable= self.gamma_var, width=5, font=("Sans", "12"))
        self.gamma_entry.grid(row=25, column=4, columnspan=2, sticky=tk.W)
        ttk.Label(self.button_frame, text="Gamma: ").grid(row=25, column=1, columnspan=3, sticky=tk.E)
        self.gamma_scale = ttk.Scale(self.button_frame, from_=20, to=180, command=self.set_Gamma)
        self.gamma_scale.grid(row=25, column=5, columnspan=3)
        self.gamma_scale.set(int(float(self.gamma_var.get())))

        self.quad_image = Image.open("util_images/quad_arrow.png")
        self.quad_image = self.quad_image.resize((int(xPad*6), int(yPad*19)), Image.ANTIALIAS)
        self.quad_image = ImageTk.PhotoImage(self.quad_image)
        quad_arrow = ttk.Label(self.button_frame, image=self.quad_image)
        quad_arrow.grid(row=13, column=5, rowspan=3, columnspan=3)

        self.double_image = Image.open("util_images/double_arrow.png")
        self.double_image = self.double_image.resize((int(xPad*2.5), int(yPad*19)), Image.ANTIALIAS)
        self.double_image = ImageTk.PhotoImage(self.double_image)
        double_arrow = ttk.Label(self.button_frame, image=self.double_image)
        double_arrow.grid(row=13, column=14, rowspan=3, columnspan=2)

        self.x_plus_10_button = ttk.Button(self.button_frame, text="1 well", command=self.app.imager.right_one_well, style="Bold.TButton")
        self.x_plus_10_button.grid(row=14, column=10, sticky=tk.N + tk.S + tk.E + tk.W)

        self.x_plus_1_button = ttk.Button(self.button_frame, text="1.0", command=self.x_plus_1, style="Bold.TButton")
        self.x_plus_1_button.grid(row=14, column=9, sticky=tk.N + tk.S + tk.E + tk.W)

        self.x_plus_01_button = ttk.Button(self.button_frame, text="0.1", command=self.x_plus_01, style="Bold.TButton")
        self.x_plus_01_button.grid(row=14, column=8, sticky=tk.N + tk.S + tk.E + tk.W)

        self.x_minus_01_button = ttk.Button(self.button_frame, text="0.1", command=self.x_minus_01, style="Bold.TButton")
        self.x_minus_01_button.grid(row=14, column=4, sticky=tk.N + tk.S + tk.E + tk.W)

        self.x_minus_1_button = ttk.Button(self.button_frame, text="1.0", command=self.x_minus_1, style="Bold.TButton")
        self.x_minus_1_button.grid(row=14, column=3, sticky=tk.N + tk.S + tk.E + tk.W)

        self.x_minus_10_button = ttk.Button(self.button_frame, text="1 well", command=self.app.imager.left_one_well, style="Bold.TButton")
        self.x_minus_10_button.grid(row=14, column=2, sticky=tk.N + tk.S + tk.E + tk.W)

        self.y_plus_10_button = ttk.Button(self.button_frame, text="1 well", command=self.app.imager.up_one_well, style="Bold.TButton")
        self.y_plus_10_button.grid(row=10, column=5, columnspan=3, sticky=tk.N + tk.S)

        self.y_plus_1_button = ttk.Button(self.button_frame, text="1.0", command=self.y_plus_1, style="Bold.TButton")
        self.y_plus_1_button.grid(row=11, column=5, columnspan=3, sticky=tk.N + tk.S)

        self.y_plus_01_button = ttk.Button(self.button_frame, text="0.1", command=self.y_plus_01, style="Bold.TButton")
        self.y_plus_01_button.grid(row=12, column=5, columnspan=3, sticky=tk.N + tk.S)

        self.y_minus_01_button = ttk.Button(self.button_frame, text="0.1", command=self.y_minus_01, style="Bold.TButton")
        self.y_minus_01_button.grid(row=16, column=5, columnspan=3, sticky=tk.N + tk.S)

        self.y_minus_1_button = ttk.Button(self.button_frame, text="1.0", command=self.y_minus_1, style="Bold.TButton")
        self.y_minus_1_button.grid(row=17, column=5, columnspan=3,  sticky=tk.N + tk.S)

        self.y_minus_10_button = ttk.Button(self.button_frame, text="1 well", command=self.app.imager.down_one_well, style="Bold.TButton")
        self.y_minus_10_button.grid(row=18, column=5, columnspan=3, sticky=tk.N + tk.S)


        #z_plus_10_button = ttk.Button(self.button_frame, text="10", command = self.z_plus_10, style="Italic.TButton")
        #z_plus_10_button.grid(row = 10, column = 14, columnspan=2, sticky=tk.N + tk.S)

        self.z_plus_1_button = ttk.Button(self.button_frame, text="1.0", command = self.z_plus_1, style="Italic.TButton")
        self.z_plus_1_button.grid(row = 10, column = 14, columnspan=2, sticky=tk.N + tk.S)

        self.z_plus_01_button = ttk.Button(self.button_frame, text="0.1", command = self.z_plus_01, style="Italic.TButton")
        self.z_plus_01_button.grid(row = 11, column = 14, columnspan=2, sticky=tk.N + tk.S)

        self.z_plus_001_button = ttk.Button(self.button_frame, text="0.01", command = self.z_plus_001, style="Italic.TButton")
        self.z_plus_001_button.grid(row = 12, column = 14, columnspan=2, sticky=tk.N + tk.S)

        self.z_minus_001_button = ttk.Button(self.button_frame, text="0.01", command = self.z_minus_001, style="Italic.TButton")
        self.z_minus_001_button.grid(row = 16, column = 14, columnspan=2, sticky=tk.N + tk.S)

        self.z_minus_01_button = ttk.Button(self.button_frame, text="0.1", command = self.z_minus_01, style="Italic.TButton")
        self.z_minus_01_button.grid(row = 17, column = 14, columnspan=2, sticky=tk.N + tk.S)

        self.z_minus_1_button = ttk.Button(self.button_frame, text="1.0", command = self.z_minus_1, style="Italic.TButton")
        self.z_minus_1_button.grid(row = 18, column = 14, columnspan=2, sticky=tk.N + tk.S)

        #z_minus_10_button = ttk.Button(self.button_frame, text="10", command = self.z_minus_10, style="Italic.TButton")
        #z_minus_10_button.grid(row = 20, column = 14, columnspan=2, sticky=tk.N + tk.S)

        self.well = tk.StringVar(master)
        self.well.set("H12-3")
        self.well_entry = ttk.Entry(self.button_frame, textvariable=self.well, font=("Sans", "12"), width=7)
        well_label = ttk.Label(self.button_frame, text="Enter well to view: ")
        example_label = ttk.Label(self.button_frame, text="(must be 'A01-1' format)", font=("Sans", "12", "italic"))
        self.goButton = ttk.Button(self.button_frame, text="Go to well", command=self.app.imager.find_single_well)
        self.goButton.grid(row=8, column=8, columnspan=3, sticky=tk.W)
        well_label.grid(row=8, column=1, columnspan=5, sticky=tk.E)
        example_label.grid(row=9, column=2, columnspan=10, sticky=tk.N)
        self.well_entry.grid(row=8, column=6, columnspan=2)

        #---------------------------------------------------------------------------------------------------------------

        self.output = tk.Text(self.feedback_frame, background='black', foreground='white', height=15,
                              font=("Sans", "12"))
        # scroll = tk.Scrollbar(self.output, command=self.output.yview)
        # scroll.grid(sticky=tk.E)
        # self.output.config(yscrollcommand=scroll.set)

        #sys.stdout = self.app.StdRedirector([self.output, master.master.frames["AutoFrame"].output])
        #sys.stderr = self.app.StdRedirector([self.output, master.master.frames["AutoFrame"].output])
        self.output.grid(row=0, column=1, rowspan=2)
        self.video_screen = ttk.Label(self.video_frame, text='')
        self.video_screen.grid(row=0, column=0)

        def find_well(event):
            self.app.imager.find_single_well()

        self.well_entry.bind("<Return>", find_well)

        def set_hue(event):
            value = self.hue_var.get()
            v = float(value)
            v = int(v)
            self.hue_scale.set(v)

        self.hue_entry.bind("<Return>", set_hue)

        def set_saturation(event):
            value = self.saturation_var.get()
            v = float(value)
            v = int(v)
            self.saturation_scale.set(v)

        self.saturation_entry.bind("<Return>", set_saturation)

        def set_brightness(event):
            value = self.brightness_var.get()
            v = float(value)
            v = int(v)
            self.brightness_scale.set(v)

        self.brightness_entry.bind("<Return>", set_brightness)

        def set_contrast(event):
            value = self.contrast_var.get()
            v = float(value)
            v = int(v)
            self.contrast_scale.set(v)

        self.contrast_entry.bind("<Return>", set_contrast)

        def set_gamma(event):
            value = self.gamma_var.get()
            v = float(value)
            v = int(v)
            self.gamma_scale.set(v)

        self.gamma_entry.bind("<Return>", set_gamma)

 #      def set_temp(event):
 #           value = self.temp_var.get()
 #           v = float(value)
 #           v = int(v)
 #           self.temp_scale.set(v)

 #       self.temp_entry.bind("<Return>", set_temp)

 #       def set_tint(event):
 #           value = self.tint_var.get()
 #           v = float(value)
 #           v = int(v)
 #           self.tint_scale.set(v)

 #       self.tint_entry.bind("<Return>", set_tint)

        self.app.loading_screen.progress.step(33)
        self.app.loading_screen.update()

    def save_camera_settings(self):
        file = open("camera_config")





    def x_plus_10(self):
        currentX, currentY = self.app.imager.ping_location(self.master.master.s)
        if currentX > maxX-10:
            return
        else:
            gc.writeTemporary(currentX+10, currentY)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def x_plus_1(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentX > maxX-1:
            return
        else:
            gc.writeTemporary(currentX+1, currentY)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def x_plus_01(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentX > maxX-.1:
            return
        else:
            gc.writeTemporary(currentX+.1, currentY)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def x_minus_10(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentX < 10:
            return
        else:
            gc.writeTemporary(currentX-10, currentY)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def x_minus_1(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentX < 1:
            return
        else:
            gc.writeTemporary(currentX-1, currentY)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def x_minus_01(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentX < .1:
            return
        else:
            gc.writeTemporary(currentX-.1, currentY)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def y_plus_10(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentY > maxY-10:
            return
        else:
            gc.writeTemporary(currentX, currentY+10)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()

    def y_plus_1(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentY > maxY-1:
            return
        else:
            gc.writeTemporary(currentX, currentY+1)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()

    def y_plus_01(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentY > maxY-.1:
            return
        else:
            gc.writeTemporary(currentX, currentY+.1)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def y_minus_10(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentY < 10:
            return
        else:
            gc.writeTemporary(currentX, currentY-10)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def y_minus_1(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentY < 1:
            return
        else:
            gc.writeTemporary(currentX, currentY-1)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def y_minus_01(self):
        currentX, currentY = self.app.imager.ping_location()
        if currentY <0.1:
            return
        else:
            gc.writeTemporary(currentX, currentY-0.1)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def z_plus_10(self):
        currentX, currentY, currentZ = self.app.imager.ping_location(z=True)
        if currentZ > maxZ-10:
            return
        else:
            gc.writeTemporary(currentX, currentY, z=currentZ+10)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()

    def z_plus_1(self):
        currentX, currentY, currentZ = self.app.imager.ping_location(z=True)
        if currentZ > maxZ-1:
            return
        else:
            gc.writeTemporary(currentX, currentY, z=currentZ+1)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()

    def z_plus_01(self):
        currentX, currentY, currentZ = self.app.imager.ping_location(z=True)
        if currentZ > maxZ-0.1:
            return
        else:
            gc.writeTemporary(currentX, currentY, z=currentZ+0.1)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()

    def z_plus_001(self):
        currentX, currentY, currentZ = self.app.imager.ping_location(z=True)
        if currentZ > maxZ-0.01:
            return
        else:
            gc.writeTemporary(currentX, currentY, z=currentZ+0.01)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def z_minus_10(self):
        currentX, currentY, currentZ = self.app.imager.ping_location(z=True)
        if currentZ < 10:
            return
        else:
            gc.writeTemporary(currentX, currentY, z=currentZ-10)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()

    def z_minus_1(self):
        currentX, currentY, currentZ = self.app.imager.ping_location(z=True)
        if currentZ < 1:
            return
        else:
            gc.writeTemporary(currentX, currentY, z=currentZ-1)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()

    def z_minus_01(self):
        currentX, currentY, currentZ = self.app.imager.ping_location(z=True)
        if currentZ < 0.1:
            return
        else:
            gc.writeTemporary(currentX, currentY, z=currentZ-0.1)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()

    def z_minus_001(self):
        currentX, currentY, currentZ = self.app.imager.ping_location(z=True)
        if currentZ < 0.01:
            return
        else:
            gc.writeTemporary(currentX, currentY, z = currentZ-0.01)
            gc.sendGCode(self.app.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            self.app.imager.print_current_location()


    def calibrate(self):

        currentX, currentY, currentZ = self.app.imager.ping_location(z=True)
        if self.master.master.type.get() == "Intelli-plate 96-3":
            print("> Calibrated location of A01-1 for Intelli-plate 96-3")
            print("> ")
            initFile = open("96-3_init.txt", "w")

            self.app.FIRST_X = currentX
            initFile.write(str(currentX) + '\n')

            self.app.FIRST_Y = currentY
            initFile.write(str(currentY) + '\n')

            self.app.FIRST_Z = currentZ
            initFile.write(str(currentZ))

            initFile.close()

    def set_Hue(self, v):
        v = float(v)
        v = int(v)
        self.hue_var.set(v)
        self.app.cam.set_hue(v)


    def set_Saturation(self, v):
        v = float(v)
        v = int(v)
        self.saturation_var.set(v)
        self.app.cam.set_saturation(v)

    def set_Brightness(self, v):
        v = float(v)
        v = int(v)
        self.brightness_var.set(v)
        self.app.cam.set_brightness(v)

    def set_Contrast(self, v):
        v = float(v)
        v = int(v)
        self.contrast_var.set(v)
        self.app.cam.set_contrast(v)

    def set_Gamma(self, v):
        v = float(v)
        v = int(v)
        self.gamma_var.set(v)
        self.app.cam.set_gamma(v)

  #  def set_Temp(self, v):
  #      v = float(v)
  #      v = int(v)
  #      self.temp_var.set(v)
  #      v2 = self.tint_var.get()
  #      self.master.master.cam.set_temperature_tint(v, v2)

  #  def set_Tint(self, v):
  #      v = float(v)
  #      v = int(v)
  #      self.tint_var.set(v)
  #      v1 = self.temp_var.get()
  #      self.master.master.cam.set_temperature_tint(v1, v)
