import tkinter as tk
from tkinter import ttk
from utils import *


class AutoFrame(tk.Frame):
    """Defines a tk.Frame containing all of the widgets used in automatic mode"""

    def __init__(self, master):
        """Initializes all of the widgets for the automatic mode GUI"""

        self.app = master.master

        self.app.loading_screen.label.config(text="Creating Auto Frame...")
        self.app.loading_screen.update()

        screen_width = self.app.screen_width
        screen_height = self.app.screen_height
        tk.Frame.__init__(self, master)


        #go_home(app_master.s)

        # Button Frame is 6/9 the height and 1/2 the width of the screen
        # located in the bottom left corner
        # Contains the plate selector, well selector, 'custom path' button,
        # and 'GO' button
        self.button_frame = tk.Frame(self, height=screen_height, width=screen_width/2 - 1, bg = "#fff")
        self.button_frame.grid_propagate(0)
        self.button_frame.grid(row = 3, column = 0, rowspan = 6, sticky=tk.SW)

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
        self.feedback_frame.grid(row = 7, column = 1, rowspan = 2, sticky=tk.SE)
        self.progress_frame = tk.Frame(self.feedback_frame, height=self.feedback_frame.winfo_height(), width=(self.feedback_frame.winfo_width()/3), bg='#222')
        self.progress_frame.grid(sticky=tk.W)

#-----------------------------------------------------------------------------------------------------------------------
        # Creates the widgets for the button frame

        xPad = screen_width/90
        yPad = ((screen_height/9)*6)/150
        style = ttk.Style()

        style.configure("TButton", font=("Sans", "12"))
        style.configure("Bold.TButton", font=("Sans", "34", "bold"))

        style.configure("TLabel", font=("Sans", "14"), background="#eeeeee")
        style.configure("Bold.TLabel",  relief="raised", borderwidth=5)
        style.configure("TCombobox", font=("Sans", "16"))
        style.configure("TCheckbutton", background="#eeeeee")
        style.configure("TEntry", font=("Sans", "14"), height="14")


        for i in range(32):
            ttk.Label(self.button_frame, text="", background="white").grid(row=0, column=i, ipady=yPad, ipadx=xPad)
            ttk.Label(self.button_frame, text="", background="white").grid(row=i, column=0, ipady=yPad, ipadx=xPad)
        for i in range(32):
            ttk.Label(self.button_frame, text="", background="white").grid(row=0, column=i, ipady=yPad, ipadx=xPad)
            #ttk.Label(self.button_frame, text="", background="red").grid(row=20, column=i, ipady=yPad, ipadx=xPad)
            #ttk.Label(self.button_frame, text="", background="red").grid(row=i, column=20, ipady=yPad, ipadx=xPad)

        self.tray_choice_background = ttk.Label(self.button_frame, text="", background="#eeeeee", style="Bold.TLabel")
        self.tray_choice_background.grid(row=1, column=1, rowspan=7, columnspan=9, sticky=tk.N + tk.S + tk.W + tk.E )
        choices = ['Intelli-plate 96-3', 'Greiner 1536']


        self.dropdown = ttk.Combobox(self.button_frame, textvariable=self.app.type, values=choices, state="readonly",
                                     font=("Sans", "16"))
        self.dropdown.bind("<<ComboboxSelected>>", self.on_field_change)
        ttk.Label(self.button_frame, text='Choose a tray:').grid(row=2, column=1, columnspan=9)
        self.dropdown.grid(row=3, column=1, columnspan=9)



        #self.customCancel = tk.Button(self.button_frame, command=self.clear_locations, )



        self.well_background=ttk.Label(self.button_frame, text="", background="#eeeeee", style="Bold.TLabel")
        self.well_background.grid(row=9, column=1, rowspan=5, columnspan=9, sticky=tk.N + tk.S + tk.E + tk.W)
        ttk.Label(self.button_frame, text="Choose which wells to image:").grid(row=9, column=2, columnspan=7)

        def paint():
            locations = self.app.determine_wells()
            self.app.locations = sort_to_snake(locations, self.app.type.get())
            self.app.paint_custom_diagram()
            self.paint_selections()


        #Sets up the widgets for Intelli-plate 96-3 wells
        self.w1 = tk.IntVar(self.master)
        self.well1 = ttk.Checkbutton(self.button_frame, variable=self.w1, command=paint)
        self.w2 = tk.IntVar(self.master)
        self.well2 = ttk.Checkbutton(self.button_frame, variable=self.w2, command=paint)
        self.w3 = tk.IntVar(self.master)
        self.well3 = ttk.Checkbutton(self.button_frame, variable=self.w3, command=paint)



        self.well1.grid(row=10, column=3)
        self.well1_label = ttk.Label(self.button_frame, text="Well 1:")
        self.well1_label.grid(row=10, column=1, columnspan=2)
        self.well2.grid(row=11, column=3)
        self.well2_label = ttk.Label(self.button_frame, text="Well 2:")
        self.well2_label.grid(row=11, column=1, columnspan=2)
        self.well3.grid(row=12, column=3)
        self.well3_label = ttk.Label(self.button_frame, text="Well 3:")
        self.well3_label.grid(row=12, column=1, columnspan=2)

        #Sets up the widgets for Greiner 1536 wells
        self.w1_1 = tk.IntVar(self.master)
        self.well_1_1 = ttk.Checkbutton(self.button_frame, variable=self.w1_1)
        self.well_1_1.grid(row=10, column=1)
        self.well_1_1.grid_remove()

        self.w1_2 = tk.IntVar(self.master)
        self.well_1_2 = ttk.Checkbutton(self.button_frame, variable=self.w1_2)
        self.well_1_2.grid(row=10, column=2)
        self.well_1_2.grid_remove()

        self.w1_3 = tk.IntVar(self.master)
        self.well_1_3 = ttk.Checkbutton(self.button_frame, variable=self.w1_3)
        self.well_1_3.grid(row=10, column=3)
        self.well_1_3.grid_remove()

        self.w1_4 = tk.IntVar(self.master)
        self.well_1_4 = ttk.Checkbutton(self.button_frame, variable=self.w1_4)
        self.well_1_4.grid(row=10, column=4)
        self.well_1_4.grid_remove()

        self.w2_1 = tk.IntVar(self.master)
        self.well_2_1 = ttk.Checkbutton(self.button_frame, variable=self.w2_1)
        self.well_2_1.grid(row=11, column=1)
        self.well_2_1.grid_remove()

        self.w2_2 = tk.IntVar(self.master)
        self.well_2_2 = ttk.Checkbutton(self.button_frame, variable=self.w2_2)
        self.well_2_2.grid(row=11, column=2)
        self.well_2_2.grid_remove()

        self.w2_3 = tk.IntVar(self.master)
        self.well_2_3 = ttk.Checkbutton(self.button_frame, variable=self.w2_3)
        self.well_2_3.grid(row=11, column=3)
        self.well_2_3.grid_remove()

        self.w2_4 = tk.IntVar(self.master)
        self.well_2_4 = ttk.Checkbutton(self.button_frame, variable=self.w2_4)
        self.well_2_4.grid(row=11, column=4)
        self.well_2_4.grid_remove()

        self.w3_1 = tk.IntVar(self.master)
        self.well_3_1 = ttk.Checkbutton(self.button_frame, variable=self.w3_1)
        self.well_3_1.grid(row=12, column=1)
        self.well_3_1.grid_remove()

        self.w3_2 = tk.IntVar(self.master)
        self.well_3_2 = ttk.Checkbutton(self.button_frame, variable=self.w3_2)
        self.well_3_2.grid(row=12, column=2)
        self.well_3_2.grid_remove()

        self.w3_3 = tk.IntVar(self.master)
        self.well_3_3 = ttk.Checkbutton(self.button_frame, variable=self.w3_3)
        self.well_3_3.grid(row=12, column=3)
        self.well_3_3.grid_remove()

        self.w3_4 = tk.IntVar(self.master)
        self.well_3_4 = ttk.Checkbutton(self.button_frame, variable=self.w3_4)
        self.well_3_4.grid(row=12, column=4)
        self.well_3_4.grid_remove()

        self.w4_1 = tk.IntVar(self.master)
        self.well_4_1 = ttk.Checkbutton(self.button_frame, variable=self.w4_1)
        self.well_4_1.grid(row=13, column=1)
        self.well_4_1.grid_remove()

        self.w4_2 = tk.IntVar(self.master)
        self.well_4_2 = ttk.Checkbutton(self.button_frame, variable=self.w4_2)
        self.well_4_2.grid(row=13, column=2)
        self.well_4_2.grid_remove()

        self.w4_3 = tk.IntVar(self.master)
        self.well_4_3 = ttk.Checkbutton(self.button_frame, variable=self.w4_3)
        self.well_4_3.grid(row=13, column=3)
        self.well_4_3.grid_remove()

        self.w4_4 = tk.IntVar(self.master)
        self.well_4_4 = ttk.Checkbutton(self.button_frame, variable=self.w4_4)
        self.well_4_4.grid(row=13, column=4)
        self.well_4_4.grid_remove()

        self.customCheck = ttk.Button(self.button_frame, command=self.app.display_custom_diagram, text='Use Custom Selection')
        self.customVar = tk.IntVar(self.master)
        self.customCheck.grid(row=11, column=5, columnspan=5)

        self.goButton = ttk.Button(self.button_frame, text="GO", command=self.app.go)
        self.goButton.grid(row=25, column=13, rowspan=3, columnspan=5)

        def load():
            """Button command to load new tray"""

            self.app.imager.load_tray()
            self.app.open_plate_window()

        self.project = tk.StringVar(self.app)
        self.entry_background = ttk.Label(self.button_frame, text="", background="#eeeeee", style="Bold.TLabel")
        self.entry_background.grid(row=1, column=11, rowspan=8, columnspan=9, sticky=tk.N + tk.S + tk.E + tk.W)
        self.loadButton = ttk.Button(self.button_frame, text="Load new tray", command=load)
        self.loadButton.grid(row=2, column=13, columnspan=5)
        self.project_entry = ttk.Entry(self.button_frame, textvariable=self.project, font=("Sans", "12", "italic"))
        entry_label = ttk.Label(self.button_frame, text="Project code: ")
        entry_label.grid(row=4, column=11, columnspan=4)
        self.project_entry.grid(row=4, column=14, columnspan=6)
        self.target = tk.StringVar(self.app)
        self.target_entry = ttk.Entry(self.button_frame, textvariable=self.target, font=("Sans", "12", "italic"))
        target_label = ttk.Label(self.button_frame, text="Target name: ")
        target_label.grid(row=5, column=11, columnspan=4)
        self.target_entry.grid(row=5, column=14, columnspan=6)
        self.plate = tk.StringVar(self.app)
        self.plate_entry = ttk.Entry(self.button_frame, textvariable=self.plate, font=("Sans", "12", "italic"))
        plate_label = ttk.Label(self.button_frame, text="Plate name: ")
        self.date = tk.StringVar(self.app)
        plate_label.grid(row=6, column=11, columnspan=4)
        self.plate_entry.grid(row=6, column=14, columnspan=6)
        self.date_entry = ttk.Entry(self.button_frame, textvariable=self.date, font=("Sans", "12", "italic"))
        date_label = ttk.Label(self.button_frame, text="Prep date: ")
        self.date_entry.grid(row=7, column=14, columnspan=6)
        date_label.grid(row=7, column=11, columnspan=4)

        # Imaging options
        self.options_background = ttk.Label(self.button_frame, text="", background="#eeeeee", style="Bold.TLabel")
        self.options_background.grid(row=15, column=1, rowspan=13, columnspan=9, sticky=tk.N + tk.S + tk.W + tk.E)
        ttk.Label(self.button_frame, text="Imaging Options:").grid(row=15, column=1, columnspan=9)
        ttk.Label(self.button_frame, text="Z-distance").grid(row=17, column=1, columnspan=4)
        ttk.Radiobutton(self.button_frame, text="0.1mm", variable=self.app.z_dist, value=1).grid(row=18, column=2, columnspan=2)
        ttk.Radiobutton(self.button_frame, text="0.2mm", variable=self.app.z_dist, value=2).grid(row=19, column=2, columnspan=2)
        ttk.Radiobutton(self.button_frame, text="0.3mm", variable=self.app.z_dist, value=3).grid(row=20, column=2, columnspan=2)
        ttk.Radiobutton(self.button_frame, text="0.4mm", variable=self.app.z_dist, value=4).grid(row=21, column=2, columnspan=2)
        ttk.Radiobutton(self.button_frame, text="0.5mm", variable=self.app.z_dist, value=5).grid(row=22, column=2, columnspan=2)
        ttk.Radiobutton(self.button_frame, text="0.6mm", variable=self.app.z_dist, value=6).grid(row=23, column=2, columnspan=2)
        ttk.Radiobutton(self.button_frame, text="0.7mm", variable=self.app.z_dist, value=7).grid(row=24, column=2, columnspan=2)
        ttk.Radiobutton(self.button_frame, text="0.8mm", variable=self.app.z_dist, value=8).grid(row=25, column=2, columnspan=2)
        ttk.Radiobutton(self.button_frame, text="0.9mm", variable=self.app.z_dist, value=9).grid(row=26, column=2, columnspan=2)
        ttk.Radiobutton(self.button_frame, text="1.0mm", variable=self.app.z_dist, value=10).grid(row=27, column=2, columnspan=2)

        slice_choices = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        slices = ttk.Combobox(self.button_frame, textvariable=self.app.slices, values=slice_choices, state="readonly", width=3)
        slices.grid(row=18, column=7)
        ttk.Label(self.button_frame, text="# of Slices").grid(row=17, column=5, columnspan=5)

        ttk.Radiobutton(self.button_frame, text="On", variable=self.app.do_autocorrect, value=True).grid(row=21, column=7)
        ttk.Radiobutton(self.button_frame, text="Off", variable=self.app.do_autocorrect, value=False).grid(row=22, column=7)

        ttk.Label(self.button_frame, text="X/Y Autocorrect").grid(row=20, column=5, columnspan=5)

        # Someday...

        ttk.Label(self.button_frame, text="Fluorescence").grid(row=24, column=5, columnspan=5)
        self.laser_var = tk.IntVar()
        self.laser_var.set(0)

        ttk.Radiobutton(self.button_frame, text="None", variable=None).grid(row=25, column=6, columnspan=3)
        ttk.Radiobutton(self.button_frame, text="UV", variable=None).grid(row=26, column=6, columnspan=3)
        ttk.Radiobutton(self.button_frame, text="Laser", variable=self.laser_var).grid(row=27, column=6, columnspan=3)

        # Canvas with well selections
        self.well_panel = tk.Canvas(self.button_frame)
        self.well_panel.grid(row=10, column=11, rowspan=15, columnspan=9, sticky=tk.N+tk.S+tk.E+tk.W)

        self.paint_selections()

        def toggle(event):
            item = self.well_panel.find_withtag("current")
            if self.well_panel.type(item) == "rectangle":
                well = self.well_panel.gettags(item)[0]
                if well in self.app.locations:
                    self.app.locations.remove(well)
                else:
                    self.app.locations.append(well)

                if len(self.app.locations) > 0:
                    self.app.custom.set(1)
                else:
                    self.app.custom.set(0)

                self.app.paint_custom_diagram()
                self.paint_selections()

        self.well_panel.bind("<Button-1>", toggle)
    #-------------------------------------------------------------------------------------------------------------------

        # Feedback frame widgets

        self.output = tk.Text(self.feedback_frame, background='black', foreground='white', height=15, font=("Sans", "12"))

        style.configure("red.Horizontal.TProgressbar", foreground='red', background='red')
        self.progress = ttk.Progressbar(self.progress_frame, style="red.Horizontal.TProgressbar", orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, padx=30)

        ttk.Label(self.progress_frame, text="Progress", background="#222", foreground="white").grid(row=2, column=0, rowspan=2, sticky=tk.N)
        self.output.grid(row=0, column=1, rowspan=4)
        self.cancelButton = ttk.Button(self.progress_frame, text='Cancel', command=self.app.cancel)
        self.cancelButton.grid(row=5, column=0, pady=20)
        self.video_screen = tk.Label(self.video_frame, text='')
        self.video_screen.grid(row=0, column=0)

        time_remaining = ttk.Label(self.progress_frame, text="Estimated time remaining:", background="#222",
                                   foreground="white")
        time_remaining.grid(row=0, column=0, sticky=tk.N)
        self.time_label = ttk.Label(self.progress_frame, text = "-------", background="#222", foreground="white")
        self.time_label.grid(row = 1, column = 0, pady = 10)

        self.app.loading_screen.progress.step(33)
        self.app.loading_screen.update()

    def reset_progress(self):
        self.progress = ttk.Progressbar(self.progress_frame, style="red.Horizontal.TProgressbar", orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, padx=30)

    def paint_selections(self):

        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        cols = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        wells = ['1', '2', '3']

        total_wells = [row + str(col) + '-' + str(well) for row in rows for col in cols for well in wells]

        for row in rows:
            row_int = int(ord(row)) - 65
            x1 = 354 - row_int * 45
            self.well_panel.create_text(x1, 15, text=row, font=("Sans", "12", "bold"))

        for column in cols:
            col_int = int(column) - 1
            y1 = 30 + (col_int * 45)
            self.well_panel.create_text(395, y1, text=column, font=("Sans", "12", "bold"))

        for well in total_wells:
            coordinates = self.app.well_to_little_coordinates(well)
            self.well_panel.create_rectangle(coordinates[0], coordinates[1], coordinates[2], coordinates[3],
                                             fill="white", activefill="yellow", tags=well)

        for location in self.app.locations:
            coordinates = self.app.well_to_little_coordinates(location)
            self.well_panel.create_rectangle(coordinates[0], coordinates[1], coordinates[2], coordinates[3], fill="red", activefill="yellow")

    def on_field_change(self, value):
        if self.master.master.type.get() == "Intelli-plate 96-3":
            self.well_1_1.grid_remove()
            self.well_1_2.grid_remove()
            self.well_1_3.grid_remove()
            self.well_1_4.grid_remove()
            self.well_2_1.grid_remove()
            self.well_2_2.grid_remove()
            self.well_2_3.grid_remove()
            self.well_2_4.grid_remove()
            self.well_3_1.grid_remove()
            self.well_3_2.grid_remove()
            self.well_3_3.grid_remove()
            self.well_3_4.grid_remove()
            self.well_4_1.grid_remove()
            self.well_4_2.grid_remove()
            self.well_4_3.grid_remove()
            self.well_4_4.grid_remove()

            self.well1.grid()
            self.well2.grid()
            self.well3.grid()
            self.well1_label.grid()
            self.well2_label.grid()
            self.well3_label.grid()

        elif self.master.master.type.get() == "Greiner 1536":

            self.well1.grid_remove()
            self.well2.grid_remove()
            self.well3.grid_remove()
            self.well1_label.grid_remove()
            self.well2_label.grid_remove()
            self.well3_label.grid_remove()

            self.well_1_1.grid()
            self.well_1_2.grid()
            self.well_1_3.grid()
            self.well_1_4.grid()
            self.well_2_1.grid()
            self.well_2_2.grid()
            self.well_2_3.grid()
            self.well_2_4.grid()
            self.well_3_1.grid()
            self.well_3_2.grid()
            self.well_3_3.grid()
            self.well_3_4.grid()
            self.well_4_1.grid()
            self.well_4_2.grid()
            self.well_4_3.grid()
            self.well_4_4.grid()