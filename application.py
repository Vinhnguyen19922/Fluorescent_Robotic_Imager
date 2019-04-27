import math
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import datetime
from camera import ToupCamCamera
from pathlib import Path
import cv2 as cv2
import pyramid as pyramid
from shutil import copyfile

from arduino_controls import arduino_control
from utils import *
from imager_controls import imager_controls
from auto_frame import AutoFrame
from manual_frame import ManualFrame
from viewing_frame import ViewingFrame

port = "/dev/ttyUSB0"
arPort = "/dev/ttyACM0"
arduino = None
cancel_flag = False

app = None

#-----------------------------------------------------------------------------------------------------------------------




class Application(tk.Tk):
    """Class housing the GUI and logic required to run the HarkerBio Robotic Imager

    Attributes:
        locations: A list of locations to image.
    """

    locations = []
    slices = None


    ####################################################################################################################

    def __init__(self, master=None):
        """Initializes the application and the three separate frames,
         builds and configures the menu.
        """
        tk.Tk.__init__(self)

        # Instances for serial connections and imager controls
        self.arduino = arduino_control(arPort)
        self.s = gc.openSerialPort(port)
        self.imager = imager_controls(self.s, self)

        self.withdraw()
        self.do_autocorrect = tk.BooleanVar(self)
        self.do_autocorrect.set(True)
        self.selection_panel = None

        # Sets up a loading screen when the program is first initialized
        self.loading_screen = tk.Toplevel()
        self.loading_screen.title("Loading HBRI software...")
        self.loading_screen.progress = ttk.Progressbar(self.loading_screen, style="red.Horizontal.TProgressbar",
                                                  orient="horizontal", length=400, mode="determinate")
        self.loading_screen.progress.grid(row=0, column=0, columnspan=4, padx=30, pady=50)
        self.loading_screen.task = tk.Label(self.loading_screen, text="Task: ")
        self.loading_screen.label = tk.Label(self.loading_screen, text="------------------")
        self.loading_screen.label.grid(row=1, column=1, columnspan=2, sticky=tk.W)
        self.loading_screen.task.grid(row=1, column=0, sticky=tk.E)
        self.loading_screen.update()

        self.slices= tk.IntVar(self)
        self.z_dist = tk.IntVar(self)
        self.custom = tk.IntVar(self)
        self.custom.set(0)
        self.custom_window = None
        self.locations = []
        self.z_dist.set(5)
        style = ttk.Style()
        style.theme_use("clam")
        self._frame = None
        self.active = False

        self.cam = ToupCamCamera()
        self.cam._master = self
        self.cam.set_esize(1)
        self.cam.set_with_callback()

        # Variables for the initial starting location, read from file and set by the "calibrate" function
        self.FIRST_X = 0
        self.FIRST_Y = 0
        self.FIRST_Z = 0

        self.screen_width = tk.Tk.winfo_screenwidth(self)
        self.screen_height = tk.Tk.winfo_screenheight(self)


        self.cancelled = False
        self.type = tk.StringVar(self)
        self.type.set('Intelli-plate 96-3')

        container = tk.Frame(self, height = self.screen_height, width = self.screen_width)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Defines a list of frames, initializes and adds the three mode frames
        self.frames = {}
        def make_auto():
            autoframe = AutoFrame(container)
            autoframe.grid(row=0, column=0, sticky="nsew")
            self.frames["AutoFrame"] = autoframe

        def make_manual():
            manualframe = ManualFrame(container)
            manualframe.grid(row=0, column=0, sticky="nsew")
            self.frames["ManualFrame"] = manualframe

        def make_viewing():
            viewingframe = ViewingFrame(container)
            viewingframe.grid(row=0, column=0, sticky="nsew")
            self.frames["ViewingFrame"] = viewingframe

        make_auto()
        make_manual()
        make_viewing()

        # Default mode on startup is manual, can be changed by uncommenting other lines
        self.switch_frame("ManualFrame")
        #self.switch_frame("ViewingFrame")
        #self.switch_frame("AutoFrame")

        self.set_camera_default()
        self.vid = None
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.project = None
        self.target = None
        self.plate = None

        # Builds the menu
        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load plate configuration", command=self.choose_load_file)
        filemenu.add_command(label="Save current configuration", command=self.choose_save_file)
        filemenu.add_separator()
        filemenu.add_command(label="Show current configuration", command=self.display_custom_diagram)
        filemenu.add_command(label="Clear current configuration", command=self.clear_locations)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="Imager", menu=filemenu)

        modemenu = tk.Menu(menubar, tearoff=0)
        modemenu.add_command(label="Automatic", command=self.auto)
        modemenu.add_command(label="Manual", command=self.manual)
        modemenu.add_command(label="Viewing/Editing", command = self.view)
        menubar.add_cascade(label="Mode", menu=modemenu)

        maintenance = tk.Menu(menubar, tearoff=0)
        maintenance.add_command(label="Open shell", command=self.arduino.open_sesame)
        maintenance.add_command(label="Close shell", command=self.arduino.close_sesame)
        maintenance.add_command(label="Fan On", command=self.arduino.fan_on)
        maintenance.add_command(label="Fan Off", command=self.arduino.fan_off)
        maintenance.add_command(label="Disable test", command=self.disable_manual)
        maintenance.add_command(label="Enable test", command=self.enable_manual)
        maintenance.add_command(label="UV on", command=self.arduino.UV_on)
        maintenance.add_command(label="UV off", command=self.arduino.UV_off)
        menubar.add_cascade(label="Maintenance", menu=maintenance)


        # Camera commands currently don't work with the python library,
        # chaging resolution causes the program to hang

        #camera = tk.Menu(menubar, tearoff=0)
        #camera.add_command(label="Reset camera", command=self.reset_camera)
        #camera.add_separator()
        #self.resolution = tk.IntVar()
        #self.resolution.set(1)
        #camera.add_command(label="Resolution")
        #camera.add_radiobutton(label="4912 x 3684", command=self.reset_camera, value=0, variable=self.resolution)
        #camera.add_radiobutton(label="2456 x 1842", command=self.reset_camera, value=1, variable=self.resolution)
        #camera.add_radiobutton(label="1228 x 922", command=self.reset_camera, value=2, variable=self.resolution)
        #menubar.add_cascade(label="Camera", menu=camera)



        self.blue_laser = tk.BooleanVar(self)

        feature_menu = tk.Menu(menubar, tearoff = 0)
        feature_menu.add_checkbutton(label="X/Y Autocorrect", onvalue=True, offvalue=False, variable=self.do_autocorrect)
        feature_menu.add_separator()
        feature_menu.add_separator()
        feature_menu.add_checkbutton(label="Blue laser", onvalue=True, offvalue=False, variable=self.blue_laser)
        feature_menu.add_separator()

        # Sets default number of z-slices to 7
        self.slices.set(7)

        slice_menu = tk.Menu(feature_menu, tearoff=0)
        feature_menu.add_cascade(label="Number of slices", menu=slice_menu)

        # Creates slice options 1 - 20
        for i in range(1, 21):
            slice_menu.add_radiobutton(label=str(i), value=i, variable=self.slices)

        # Creates total z-distance options, 0.1mm - 1.0mm
        z_menu = tk.Menu(feature_menu, tearoff=0)
        feature_menu.add_cascade(label="Z-span", menu=z_menu)
        for i in range(1, 11):
            z_menu.add_radiobutton(label=str(float(i)/10.0) + " mm", value=i, variable=self.z_dist)

        menubar.add_cascade(label="Settings", menu=feature_menu)

        self.config(menu=menubar)

    ####################################################################################################################

    def clear_locations(self):
        """Resets the list of locations so that no wells are selected"""
        self.locations = []
        self.custom.set(0)

    ####################################################################################################################

    def set_camera_default(self):
        """Loads the default camera settings on startup"""
        self.load_camera_config("camera_config/camera_init.txt")

    ####################################################################################################################

    def set_camera_fluorscent(self):
        """Loads the default fluorescent settings during fluorescent imaging"""
        self.load_camera_config("camera_config/laser_default.txt")

    ####################################################################################################################

    def disable_manual(self):

        # Disables the movement controls in manual mode
        # Used when autorun seizes control so settings can't be changed mid-run
        manual = self.frames["ManualFrame"]
        manual.project_entry.config(state="disabled")
        manual.target_entry.config(state="disabled")
        manual.plate_entry.config(state="disabled")
        manual.date_entry.config(state="disabled")
        manual.dropdown.config(state="disabled")
        manual.load_button.config(state="disabled")
        manual.camera_button.config(state="disabled")
        manual.lights_on_button.config(state="disabled")
        manual.lights_off_button.config(state="disabled")
        manual.green_filter_button.config(state="disabled")
        manual.no_filter_button.config(state="disabled")
        manual.laser_on_button.config(state="disabled")
        manual.laser_off_button.config(state="disabled")
        manual.calibrate_button.config(state="disabled")
        manual.x_plus_10_button.config(state="disabled")
        manual.x_plus_1_button.config(state="disabled")
        manual.x_plus_01_button.config(state="disabled")
        manual.x_minus_01_button.config(state="disabled")
        manual.x_minus_1_button.config(state="disabled")
        manual.x_minus_10_button.config(state="disabled")
        manual.y_plus_10_button.config(state="disabled")
        manual.y_plus_1_button.config(state="disabled")
        manual.y_plus_01_button.config(state="disabled")
        manual.y_minus_01_button.config(state="disabled")
        manual.y_minus_1_button.config(state="disabled")
        manual.y_minus_10_button.config(state="disabled")
        manual.z_plus_1_button.config(state="disabled")
        manual.z_plus_01_button.config(state="disabled")
        manual.z_plus_001_button.config(state="disabled")
        manual.z_minus_001_button.config(state="disabled")
        manual.z_minus_01_button.config(state="disabled")
        manual.z_minus_1_button.config(state="disabled")
        manual.well_entry.config(state="disabled")
        manual.goButton.config(state="disabled")

        auto = self.frames["AutoFrame"]
        auto.dropdown.config(state="disabled")
        auto.loadButton.config(state="disabled")
        auto.project_entry.config(state="disabled")
        auto.target_entry.config(state="disabled")
        auto.plate_entry.config(state="disabled")
        auto.date_entry.config(state="disabled")

    ####################################################################################################################

    def enable_manual(self):

        # Enables the movement controls in manual mode
        # Normally active, this is called when autorun releases control

        manual = self.frames["ManualFrame"]
        manual.project_entry.config(state="enabled")
        manual.target_entry.config(state="enabled")
        manual.plate_entry.config(state="enabled")
        manual.date_entry.config(state="enabled")
        manual.dropdown.config(state="enabled")
        manual.load_button.config(state="enabled")
        manual.camera_button.config(state="enabled")
        manual.lights_on_button.config(state="enabled")
        manual.lights_off_button.config(state="enabled")
        manual.green_filter_button.config(state="enabled")
        manual.no_filter_button.config(state="enabled")
        manual.laser_on_button.config(state="enabled")
        manual.laser_off_button.config(state="enabled")
        manual.calibrate_button.config(state="enabled")
        manual.x_plus_10_button.config(state="enabled")
        manual.x_plus_1_button.config(state="enabled")
        manual.x_plus_01_button.config(state="enabled")
        manual.x_minus_01_button.config(state="enabled")
        manual.x_minus_1_button.config(state="enabled")
        manual.x_minus_10_button.config(state="enabled")
        manual.y_plus_10_button.config(state="enabled")
        manual.y_plus_1_button.config(state="enabled")
        manual.y_plus_01_button.config(state="enabled")
        manual.y_minus_01_button.config(state="enabled")
        manual.y_minus_1_button.config(state="enabled")
        manual.y_minus_10_button.config(state="enabled")
        manual.z_plus_1_button.config(state="enabled")
        manual.z_plus_01_button.config(state="enabled")
        manual.z_plus_001_button.config(state="enabled")
        manual.z_minus_001_button.config(state="enabled")
        manual.z_minus_01_button.config(state="enabled")
        manual.z_minus_1_button.config(state="enabled")
        manual.well_entry.config(state="enabled")
        manual.goButton.config(state="enabled")

        auto = self.frames["AutoFrame"]
        auto.dropdown.config(state="enabled")
        auto.loadButton.config(state="enabled")
        auto.project_entry.config(state="enabled")
        auto.target_entry.config(state="enabled")
        auto.plate_entry.config(state="enabled")
        auto.date_entry.config(state="enabled")

    ####################################################################################################################

    def choose_save_file(self):
        """Method used when choosing filenames for saving well configuration files"""
        name = filedialog.asksaveasfilename(initialdir="well_config/")
        self.save_config(name)

    ####################################################################################################################

    def choose_load_file(self):
        """Method used when choosing filenames for loading well configuration files"""
        name = filedialog.askopenfilename(initialdir="well_config/")
        self.load_config(name)

    ####################################################################################################################

    def choose_cam_save_file(self):
        """Method used when choosing filenames for saving camera configuration files"""
        name = filedialog.asksaveasfilename(initialdir="camera_config/")
        self.save_camera_config(name)

    ####################################################################################################################

    def choose_cam_load_file(self):
        """Method used when choosing filenames for loading camera configuration files"""
        name = filedialog.askopenfilename(initialdir="camera_config/")
        self.load_camera_config(name)

    ####################################################################################################################

    def save_config(self, name):
        """Saves the current well configuration to the path determined by name"""

        if not self.locations:
            print("> No wells have been selected for this configuration")
            print("> ")
            return
        else:
            if ".txt" in name:
                file = open(name, "w+")
            else:
                name = name + ".txt"
                file = open(name, "w+")
            for well in self.locations:
                file.write(well + ",")
            file.close()
            print("> Configuration saved as:")
            print("> '" + name +"'")
            print("> ")

    ####################################################################################################################

    def save_camera_config(self, name):
        """Saves the current camera configuration to the path determined by name"""

        if ".txt" in name:
            file = open(name, "w+")
        else:
            name = name + ".txt"
            file = open(name, "w+")
        manual = self.frames["ManualFrame"]
        file.write(str(manual.hue_var.get()) + ",")
        file.write(str(manual.saturation_var.get()) + ",")
        file.write(str(manual.brightness_var.get()) + ",")
        file.write(str(manual.contrast_var.get()) + ",")
        file.write(str(manual.gamma_var.get()))
        file.close()
        print("> Camera configuration saved as:")
        print("> '" + name + "'")
        print("> ")

    ####################################################################################################################

    def load_config(self, name):
        """Loads the current well configuration from the path determined by name"""
        if Path.is_file(Path(name)):
            file = open(name, "r+")
            wells = []
            contents = file.read()
            contents = contents.split(",")
            for well in contents:
                if well == "":
                    continue
                wells.append(well)
            self.locations = wells
            file.close()
            print("> Sucessfully loaded configuration:")
            print("> '" + name + "'")
            print("> ")
        else:
            print("> Invalid configuration file chosen")
            print("> ")

    ####################################################################################################################

    def load_camera_config(self, name):
        """Loads the current camera configuration from the path determined by name"""
        if Path.is_file(Path(name)):
            file = open(name, "r+")
            contents = file.read()
            contents = contents.split(",")
            manual = self.frames["ManualFrame"]
            manual.set_Hue(int(contents[0]))
            manual.set_Saturation(int(contents[1]))
            manual.set_Brightness(int(contents[2]))
            manual.set_Contrast(int(contents[3]))
            manual.set_Gamma(int(contents[4]))
            file.close()
            print("> Successfully loaded camera configuration: ")
            print("> '" + name + "'")
            print("> ")
        else:
            print("> Invalid camera configuration file chosen")
            print("> ")

    ####################################################################################################################

    def auto(self):
        """Switches the current GUI frame to show automatic mode settings
        """

        self.switch_frame("AutoFrame")

    ####################################################################################################################

    def manual(self):
        """Switches the current GUI frame to show manual mode settings
        """

        self.switch_frame("ManualFrame")

    ####################################################################################################################

    def view(self):
        """Switches the current GUI frame to allow image viewing and editing
        """

        self.switch_frame("ViewingFrame")

    ####################################################################################################################

    def close(self):
        """Cleans up before closing application window.

         Includes the following:
            Sends the imager home
            Shuts off the EL sheet
            Shuts off the laser
            Resets the filter servo for standard imaging
            Shuts off the fans
            Closes the serial port to the imager
            Destroys the main window
        """

        self.imager.go_home()
        self.arduino.lights_off()
        self.arduino.laser_off()
        self.arduino.servo_90()
        self.arduino.fan_off()
        gc.closeSerialPort(self.s)
        self.destroy()

    ####################################################################################################################

    def save_image(self):
        """Saves the current image displayed on the screen

        Checks for user-entered tray information and creates a directory based on this data
        """

        self.disable_manual()

        project = self.frames["ManualFrame"].project.get()
        target = self.frames["ManualFrame"].target.get()
        plate = self.frames["ManualFrame"].plate.get()
        prep_date = self.frames["ManualFrame"].date.get()
        well = self.frames["ManualFrame"].well.get()


        date = datetime.date.today()

        if project == "" or target == "" or plate == "":
            print("> Must fill out project, target, and ")
            print("> plate name before imaging can begin")
            print("> ")
            self.enable_manual()
            return

        path = os.path.join(os.pardir, os.pardir, "Images/" + project + "/")
        ensure_directory(path)
        path = path + target + "/"
        ensure_directory(path)
        path = path + plate + "/"
        ensure_directory(path)
        if prep_date != "":
            self.write_prep_date(prep_date, path)
        else:
            self.frames["ManualFrame"].date.set(self.read_prep_date(path))
        path = path + str(date) + "/"
        final_path = path
        ensure_directory(path)
        path = path + well + "/"
        ensure_directory(path)
        #path = path + name + "/"
        #ensure_directory(path)

        x, y, z = self.imager.ping_location(z=True)
        z_dist = (float(self.z_dist.get()) / 10) / float(self.slices.get())


        for i in range(self.slices.get()):

            save_path = path + "slice" + str(i + 1) + ".jpg"
            self.cam.save(save_path)
            z += z_dist
            #print(z)
            gc.writeTemporary(x, y, z=z)
            gc.sendGCode(self.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            time.sleep(1.5)

        order = []
        for file in os.listdir(path):
            order.append(file)
        order.sort()
        images = []
        for file in order:
            image = cv2.imread(path + file)
            #image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            images.append(image)

        z -= float(self.z_dist.get() / 10)
        gc.writeTemporary(x, y, z=z)
        gc.sendGCode(self.s, "gcode/temp.gcode")
        os.remove("gcode/temp.gcode")

        print("> Fusing slices...")
        print("> ")

        pyramid.stack_focus(images, final_path, well)

        print("> Image successfully saved as:")
        print("> " + final_path + well + ".jpg")

        self.enable_manual()

    ####################################################################################################################

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one.
        """

        if self._frame is not None:
            self._frame.live = 0
        self._frame = self.frames[frame_class]
        self._frame.tkraise()

        #sys.stdout = self.StdRedirector(self._frame.output)
        #sys.stderr = self.StdRedirector(self._frame.output)
        if frame_class == "AutoFrame" or frame_class == "ManualFrame":
            self._frame.live = 1
        if frame_class == "AutoFrame" and self.active == False:
            self.imager.go_home()
        if frame_class == "ViewingFrame":
            self._frame.focus_set()

    ####################################################################################################################

    class StdRedirector(object):
        """Class for redirecting output to a text display in the GUI
        """

        def __init__(self, text_widgets):
            self.text_spaces = text_widgets

        def write(self, string):
            for text_space in self.text_spaces:
                text_space.config(state=tk.NORMAL)
                text_space.insert("end", string)
                text_space.see("end")
                text_space.config(state=tk.DISABLED)

    ####################################################################################################################

    def set_time(self, start, size):
        """Displays the estimated remaining time to complete the current run.

           Computes the time taken to complete one well and extrapolates across number
           of remaining wells.

        Args:
            start: time (in seconds) when imaging of current well began
            size: number of remaining wells
        """
        if size == 0:
            self.frames["AutoFrame"].time_label.config(text="-------")
            return
        total_time = int((time.time() - start) * size)
        hours = math.floor(total_time / 3600)
        h = "hour"
        if hours < 10:
            hours = "0" + str(hours)
        else:
            hours = str(hours)
        total_time = total_time % 3600
        minutes = math.floor(total_time / 60)
        if minutes < 10:
            minutes = "0" + str(minutes)
        else:
            minutes = str(minutes)
        seconds = math.floor(total_time % 60)
        if seconds < 10:
            seconds = "0" + str(seconds)
        else:
            seconds = str(seconds)
        time_string = hours + ":" + minutes + ":" + seconds

        self.frames["AutoFrame"].time_label.config(text=time_string)

    ####################################################################################################################

    def cancel(self):
        """Raises the cancelled flag, causing imager to abort current run and reset at next check
        """

        print("> Imaging cancelled")
        self.cancelled = True

    ####################################################################################################################

    def abort(self):
        """Resets the imager to its initial state after being cancelled.

        Wipes locations, resets button/setting availability, and resets cancelled flag.
        """

        self.enable_manual()
        self.cancelled = False
        self.active = False
        self.arduino.lights_off()
        self.arduino.fan_off()
        self.frames["AutoFrame"].cancelButton['state'] = tk.DISABLED
        self.frames["AutoFrame"].time_label.config(text="-------")
        self.frames["AutoFrame"].reset_progress()
        self.frames["AutoFrame"].goButton['state'] = tk.NORMAL
        self.locations = []
        for i in range(10):
            print(" ")
        setup()

    ####################################################################################################################

    def clean_up(self):
        """Resets the imager to its initial state after completing a run.
        """

        self.locations = []
        self.enable_manual()
        self.frames["AutoFrame"].time_label.config(text="-------")
        self.frames["AutoFrame"].reset_progress()
        self.active = False
        self.arduino.lights_off()
        self.arduino.laser_off()
        self.arduino.servo_90()
        self.arduino.fan_off()
        self.frames["AutoFrame"].cancelButton['state'] = tk.DISABLED
        self.frames["AutoFrame"].goButton['state'] = tk.NORMAL
        print("> Imaging complete!")
        print(" ")

    ####################################################################################################################

    def open_custom_window(self):
        """Allows user to choose a custom pattern of wells to image.

        Opens up a window containing checkboxes arranged in the pattern of
        the wells on the chosen tray. Users can check which wells to image,
        and clicking the 'Save Choices' button saves this data in the global
        'locations' list and closes the window.
        """

        top = tk.Toplevel()
        top.title("Custom well input")

        msg = tk.Message(top, text="Please choose the wells to image")

        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        wells = [1,2,3]

        total_wells = [row + str(col) + '-' + str(well) for row in rows for col in cols for well in wells]
        total_wells.sort(key=operator.itemgetter(2,1))
        checkboxes = []
        variables = []
        for i in range(288):
            name = total_wells[i]
            variables.append(tk.IntVar(top))
            checkboxes.append(tk.Checkbutton(top, variable=variables[i], text=name))

        k = 0
        for i in range(24):
            for j in range(32):
                if(j % 4 == 0):
                    tk.Label(top, text="").grid(row = j, column = i)
                elif(i % 2 == 0):
                    tk.Label(top, text="              ").grid(row = j, column = i)
                else:
                    checkboxes[k].grid(row = j, column = i)
                    k+=1

            def combined():
                self.determine_custom_wells(total_wells, variables)
                top.destroy()
                self.well1['state'] = tk.DISABLED
                self.well2['state'] = tk.DISABLED
                self.well3['state'] = tk.DISABLED
                self.custom = True

        saveButton = tk.Button(top, text="Save Choices", command=combined)
        saveButton.grid(row = 32, column = 12, columnspan=2)
        top.mainloop()

    ####################################################################################################################

    def open_plate_window(self):
        """Opens a instruction window for loading a new tray

        Window includes a diagram of how tray should be loaded and an 'OK' button.
        Pressing the button closes the window and sends the imager to home coordinates
        """

        top = tk.Toplevel(background="#ffffff")
        top.title("Please load plate as shown below")
        self.arduino.open_sesame()

        def finish():
            top.destroy()
            self.arduino.close_sesame()
            self.imager.go_home()

        self.plate_image = Image.open("util_images/simple_96-3.png")
        self.plate_image = ImageTk.PhotoImage(self.plate_image)

        image_label = ttk.Label(top, text="", image=self.plate_image)
        image_label.grid(row=0, column=0)
        ok_button = tk.Button(top, text="OK", command=finish)
        ok_button.grid(row=1, column=0, ipadx=20, ipady=20)

    ####################################################################################################################

    def update_image(self):
        """Updates the video screen with the current camera data

        Pulls the current camera data as a PIL image and resizes it to fit
        on the video screen. Updates the video and the self.vid variable.

        IMPORTANT: updating self.vid before the screen causes awful flickering.
        """
        #print("updating")
        if type(self._frame) is ViewingFrame:
            return
        elif self._frame is None:
            return

        else:
            #print("showing")

            im = self.cam.get_pil_image()
            if im is not None:
                width, height = im.size
                ratio = height/width
                im = im.resize((int(self._frame.video_width), int(self._frame.video_width * ratio)), Image.ANTIALIAS)
                vid = im.transpose(Image.FLIP_LEFT_RIGHT)

                vid = ImageTk.PhotoImage(image=vid)
                #print(vid)
                self._frame.video_screen.config(image=vid)
                self._frame.video_screen.image = vid

    ####################################################################################################################

    def determine_wells(self):
        """Determines a list of wells to image based on user-selected options

        Args:
            None

        Returns:
            A list of strings representing each well to be imaged based on the user's input
            STRING FORMAT: A01-1
        """

        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        cols = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        wells = []

        if self.type.get() == "Intelli-plate 96-3":
            if self.frames["AutoFrame"].w1.get() == 1:
                wells.append(1)
            if self.frames["AutoFrame"].w2.get() == 1:
                wells.append(2)
            if self.frames["AutoFrame"].w3.get() == 1:
                wells.append(3)

            retVal = [row + col + '-' + str(well) for row in rows for col in cols for well in wells]

            def sort_to_snake(value):
                row = value[1]
                if value[2] is not '-':
                    row += value[2]
                if int(row) % 2 == 0:
                    return operator.itemgetter(value, 1, 0, reversed)
                else:
                    return operator.itemgetter(value, 2, 1)

            retVal.sort(key=operator.itemgetter(2,1))
            return retVal

        elif self.type.get() == "Greiner 1536":
            well_rows = set()
            well_cols = set()
            if self.frames["AutoFrame"].w1_1.get() == 1:
                well_rows.add(1)
                well_cols.add(1)
            if self.frames["AutoFrame"].w1_2.get() == 1:
                well_rows.add(1)
                well_cols.add(2)
            if self.frames["AutoFrame"].w1_3.get() == 1:
                well_rows.add(1)
                well_cols.add(3)
            if self.frames["AutoFrame"].w1_4.get() == 1:
                well_rows.add(1)
                well_cols.add(4)
            if self.frames["AutoFrame"].w2_1.get() == 1:
                well_rows.add(2)
                well_cols.add(1)
            if self.frames["AutoFrame"].w2_2.get() == 1:
                well_rows.add(2)
                well_cols.add(2)
            if self.frames["AutoFrame"].w2_3.get() == 1:
                well_rows.add(2)
                well_cols.add(3)
            if self.frames["AutoFrame"].w2_4.get() == 1:
                well_rows.add(2)
                well_cols.add(4)
            if self.frames["AutoFrame"].w3_1.get() == 1:
                well_rows.add(3)
                well_cols.add(1)
            if self.frames["AutoFrame"].w3_2.get() == 1:
                well_rows.add(3)
                well_cols.add(2)
            if self.frames["AutoFrame"].w3_3.get() == 1:
                well_rows.add(3)
                well_cols.add(3)
            if self.frames["AutoFrame"].w3_4.get() == 1:
                well_rows.add(3)
                well_cols.add(4)
            if self.frames["AutoFrame"].w4_1.get() == 1:
                well_rows.add(4)
                well_cols.add(1)
            if self.frames["AutoFrame"].w4_2.get() == 1:
                well_rows.add(4)
                well_cols.add(2)
            if self.frames["AutoFrame"].w4_3.get() == 1:
                well_rows.add(4)
                well_cols.add(3)
            if self.frames["AutoFrame"].w4_4.get() == 1:
                well_rows.add(4)
                well_cols.add(4)

            retVal = [row + col + '-' + str(well_row) + '-' + str(well_col) for row in rows for col in cols
                      for well_row in well_rows for well_col in well_cols]

            retVal.sort(key=operator.itemgetter(0, 4))
            return retVal

    ####################################################################################################################

    def determine_custom_wells(self, wells, variables):
        """Determines wells to image from a custom selection decided by the user

        Args:
            wells: A list of all available wells for the tray.
            variables: A list of tk.IntVar's corresponding to the checkboxes for each well.

        Returns:
            Nothing, but updates global locations list.
        """

        locations = []
        for i in range(288):
            if (variables[i]).get() == 1:
                locations.append(wells[i])
        self.locations = locations

    ####################################################################################################################


    def determine_coordinates(self, locations):
        """Determines coordinates (in mm) of each well in the list of locations.

        Uses the coordinates of A01-1 (read from file) and tray data to
        determine the absolute coordinates of all other wells.

        Args:
            locations: a list of strings representing the wells chosen to be imaged.

        Returns:
            A dictionary mapping string locations(e.g., B05-2) with x/y coordinate pairs"""

        if self.type.get() == "Intelli-plate 96-3":

            initFile = open("96-3_init.txt", 'r')
            self.FIRST_X = float(initFile.readline())
            self.FIRST_Y = float(initFile.readline())
            self.FIRST_Z = float(initFile.readline())
            initFile.close()

            retVal = {}
            for loc in locations:
                row = ord(loc[0]) - 64
                col = loc[1]
                if loc[2] is not '-':
                    col += loc[2]
                col = int(col)
                if loc[3] is not '-':
                    well = int(loc[3])
                else:
                    well = int(loc[4])
                    # 2.5416
                    # 8.9916
                x = self.FIRST_X - (((row - 1) * 8.996) + ((well - 1) * 2.5416))
                y = self.FIRST_Y - ((col - 1) * 8.996)
                retVal[loc] = x, y

            return retVal

        elif self.type.get() == "Greiner 1536":

            initFile = open("1536_init.txt", "r")
            self.FIRST_X = float(initFile.readline())
            self.FIRST_Y = float(initFile.readline())
            self.FIRST_Z = float(initFile.readline())
            initFile.close()

            retVal = {}
            for loc in locations:
                row = ord(loc[0]) - 64
                col = loc[1] + loc[2]
                col = int(col)
                well_row = int(loc[4])
                well_col = int(loc[6])

                x = self.FIRST_X + (((row - 1) * 11) + ((well_row - 1) * 2.25))
                y = self.FIRST_Y + (((col - 1) * 11) + ((well_col - 1) * 2.25))
                retVal[loc] = x, y

            return retVal

    ####################################################################################################################


    def display_custom_diagram(self):

        if self.custom_window is not None:
            self.custom_window.lift()
            return

        top = tk.Toplevel()
        top.title("Custom well input")


        msg = tk.Message(top, text="click wells to toggle imaging")
        self.selection_panel = tk.Canvas(top, height=760, width=1040, background="#cccccc")
        #self.selection_panel.create_rectangle(10, 10, 1030, 720, fill="#cccccc")

        self.selection_panel.grid(row=0, column=0)

        def close():
            self.custom_window = None
            self.selection_panel = None
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", close)


        OKButton = tk.Button(top, text="Close", command=close)
        OKButton.grid(row=1, column=0)

        self.paint_custom_diagram()

        def toggle(event):
            item = self.selection_panel.find_withtag("current")
            if self.selection_panel.type(item) == "rectangle":
                row = ""
                column = ""
                subrow = ""
                x = self.selection_panel.canvasx(event.x)
                y = self.selection_panel.canvasy(event.y)
                row_int = int((y-80)/80 + 65)
                row = chr(row_int)
                column = int((x-80)/80 + 1)
                if column < 10:
                    column = "0" + str(column)
                else:
                    column = str(column)
                subrow = str(int((y-80-(80*(row_int-65)))/20 + 1))
                well = (row + column + "-" + subrow)
                #print(well)
                if well in self.locations:
                    self.locations.remove(well)
                else:
                    self.locations.append(well)

                if len(self.locations) > 0:
                    self.custom.set(1)
                else:
                    self.custom.set(0)

                self.paint_custom_diagram()
                self.frames["AutoFrame"].paint_selections()

        self.selection_panel.bind("<Button-1>", toggle)

        self.custom_window = top
        self.custom_window.mainloop()

    def paint_custom_diagram(self):

        if self.selection_panel is None:
            return

        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        cols = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        wells = ['1', '2', '3']

        total_wells = [row + str(col) + '-' + str(well) for row in rows for col in cols for well in wells]

        for row in rows:
            row_int = int(ord(row))-65
            y1 = 110 + row_int*80
            self.selection_panel.create_text(40, y1, text=row, font=("Sans", "20", "bold"))

        for column in cols:
            col_int = int(column) - 1
            x1 = 90 + (col_int*80)
            self.selection_panel.create_text(x1, 40, text=column, font=("Sans", "20", "bold"))

        for well in total_wells:
            coordinates = self.well_to_coordinates(well)
            self.selection_panel.create_rectangle(coordinates[0], coordinates[1], coordinates[2], coordinates[3], fill="white", activefill="yellow")

        for location in self.locations:
            coordinates = self.well_to_coordinates(location)
            self.selection_panel.create_rectangle(coordinates[0], coordinates[1], coordinates[2], coordinates[3], fill="red", activefill="yellow")

    ####################################################################################################################

    def well_to_coordinates(self, well):
        row = int(ord(well[0])) - 65
        column = int(well[1:3]) - 1
        subrow = int(well[4]) - 1
        x1 = 80 + (column * 80)
        x2 = x1 + 20
        y1 = (80 + row * 80) + (subrow * 20)
        y2 = y1 + 20
        return x1, y1, x2, y2

    ####################################################################################################################

    def well_to_little_coordinates(self, well):
        row = int(ord(well[0])) - 65
        column = int(well[1:3]) - 1
        subrow = int(well[4]) - 1
        x1 = 360 - (row*45) - (subrow*12)
        x2 = x1 + 12
        y1 = 25 + (column*45)
        y2 = y1+12
        return x1, y1, x2, y2

    ####################################################################################################################

    def go(self):
        """Determines which tray configuration to use and begins the autoimager thread.
        """

        extension = ''
        plateChoice = self.type.get()
        self.active = True

        if plateChoice == 'Intelli-plate 96-3':
            extension = 'gcode/96-3/'
        elif plateChoice == 'Greiner 1536':
            extension = 'gcode/1536/'

        if len(self.locations) > 0:
            threading.Thread(target=self.imager.run_custom_imager, args=(extension, self.locations)).start()
        else:
            locations = self.determine_wells()
            self.locations = sort_to_snake(locations, self.type.get())
            threading.Thread(target=self.imager.run_auto_imager, args=(extension, self.locations)).start()


    ####################################################################################################################

    def write_prep_date(self, date, path):
        file = open(path + "prep_date.txt", "w+")
        file.write(date)
        file.close()

    ####################################################################################################################

    def read_prep_date(self, path):
        file = open(path + "prep_date.txt", "r+")
        date = file.read()
        file.close()
        return date

    ####################################################################################################################

    def check_previous_notes(self, path, current_date):
        path = path.replace("Images", "Image_Data")
        if not Path(path).exists():
            print("> No previous notes found in directory:")
            print("> " + path)
            return

        def compare_most_recent(most_recent, date):
            most_recent_parts = most_recent.split("-")
            date_parts = date.split("-")
            if most_recent_parts[0] > date_parts[0]:
                return most_recent
            elif most_recent_parts[0] < date_parts[0]:
                return date
            # Reaching here means years are equal
            if most_recent_parts[1] > date_parts[1]:
                return most_recent
            elif most_recent_parts[1] < date_parts[1]:
                return date
            # Reaching here means months are equal
            if most_recent_parts[2] > date_parts[2]:
                return most_recent
            elif most_recent_parts[2] < date_parts[2]:
                return date
            return most_recent

        most_recent = "1800-01-01"
        for folder in os.listdir(path):
            folder = folder.split("/")
            date = folder[len(folder)-1]
            if date == current_date:
                return
            most_recent = compare_most_recent(most_recent, date)

        newPath = path + current_date + "/"
        #print(newPath)
        ensure_directory(newPath)
        path = path + most_recent + "/"

        for well in os.listdir(path):
            current_Path = newPath + well + "/"
            ensure_directory(current_Path)
            copyfile(path + well +  "/image_data_0.txt", current_Path + "image_data_0.txt")

        print("> Copied previous notes from: " + most_recent)
        print("> ")

        ################################################################################################################
    # End of Application class