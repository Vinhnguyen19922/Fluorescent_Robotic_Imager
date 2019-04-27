import math
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import pdf_writer
from PIL import Image, ImageTk
from tkinter import filedialog
import threading
from utils import *


class ViewingFrame(tk.Frame):

    def __init__(self, master):
        """Initializes all the widgets for the viewing mode GUI"""

        self.live = 0
        self.app = master.master

        self.app.loading_screen.label.config(text="Creating Viewing Frame...")
        self.app.loading_screen.update()

        self.temp_shape = None
        self.textX = 0
        self.textY = 0
        self.flag = False
        self.directory = None
        self.image_list = []
        self.thumbnail_list = {}
        self.text_list = {}
        self.scroll_size = 0
        self.timeline_size = 0
        self.selected = None
        self.selected_index = -1
        self.classifications = []
        self.sorting = tk.IntVar()
        self.sorting.set(-1)
        self.loaded = False
        self.heat_window = None

        screen_width = self.app.screen_width
        self.screen_width = screen_width
        screen_height = self.app.screen_height
        tk.Frame.__init__(self, master)


        # Button Frame is the full height and 1/2 the width of the screen
        # located in the bottom left corner
        # Contains the plate selector, well selector, 'custom path' button,
        # and 'GO' button

        self.button_frame = tk.Frame(self, height=(screen_height/9)*6, width=screen_width / 2, bg="#fff")
        self.button_frame.grid_propagate(0)


        self.button_frame.grid(row=0, column=0, rowspan=6, sticky=tk.SW)

        self.list_panel = tk.Canvas(self.button_frame)
        scrollbar = ttk.Scrollbar(self.list_panel)
        self.list_panel.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar.config(command=self.list_panel.yview)
        self.list_panel.grid(row=7, column=1, rowspan=8, columnspan=8, sticky=tk.N + tk.S + tk.E + tk.W)

        self.all_button = ttk.Radiobutton(self.button_frame, text="All", variable=self.sorting, value=-1, command=self.update_images)
        self.all_button.grid(row=6, column=1)
        self.unsorted_button = ttk.Radiobutton(self.button_frame, text="Unsorted", variable=self.sorting, value=0, command=self.update_images)
        self.unsorted_button.grid(row=6, column=2)
        self.clear_button = ttk.Radiobutton(self.button_frame, text="Clear", variable=self.sorting, value=1, command=self.update_images)
        self.clear_button.grid(row=6, column=3)
        self.precip_button = ttk.Radiobutton(self.button_frame, text="Precipitate", variable=self.sorting, value=2, command=self.update_images)
        self.precip_button.grid(row=6, column=4)
        self.crystal_button = ttk.Radiobutton(self.button_frame, text="Crystal", variable=self.sorting, value=3, command=self.update_images)
        self.crystal_button.grid(row=6, column=5)
        self.other_button = ttk.Radiobutton(self.button_frame, text="Other", variable=self.sorting, value=4, command=self.update_images)
        self.other_button.grid(row=6, column=6)

        #lights_on_button = ttk.Radiobutton(self.button_frame, text="On", variable=lightsVar, value=1, command=lights_on)

        # Video Frame is 7/9 the height and 1/2 the width of the screen
        # located in the top right corner
        # Contains live feed video as the imager works
        self.image_height = (screen_height/9) * 6
        self.image_width = (screen_width/2)
        self.image_frame = tk.Frame(self, height=self.image_height, width=self.image_width, bg= "#111")
        self.image_frame.grid_propagate(0)
        self.image_frame.grid(row = 0, column = 1, rowspan = 6, sticky=tk.NE)

        # Feedback frame is 2/9 the height and 1/2 the width of the screen
        # loacted in the bottom right corner
        # Contains the progress bar, 'Cancel' button, and output window
        self.feedback_frame = tk.Frame(self, height=(screen_height/9)*3, width=screen_width, bg='#eeeeee')
        self.feedback_frame.grid_propagate(0)
        self.feedback_frame.grid(row = 7, column = 0, rowspan = 3, columnspan=2, sticky=tk.SE)

        #---------------------------------------------------------------------------------------------------------------
        self.xPad = screen_width/42
        self.yPad = ((screen_height/9)*6)/66
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


        for i in range(22):
            ttk.Label(self.button_frame, text="", background="white").grid(row=i, column=0, ipady=self.yPad, ipadx=self.xPad)
            #ttk.Label(self.button_frame, text="", background="red").grid(row=i, column=9, ipady=self.yPad, ipadx=self.xPad)
        for i in range(10):
            ttk.Label(self.button_frame, text="", background="white").grid(row=0, column=i, ipady=self.yPad, ipadx=self.xPad)
            #ttk.Label(self.button_frame, text="", background="red").grid(row=21, column=i, ipady=self.yPad, ipadx=self.xPad)
        for i in range(30):
            ttk.Label(self.feedback_frame, text="", background="#eeeeee").grid(row=0, column=i, ipady=15, ipadx=30)
        for i in range(6):
            ttk.Label(self.feedback_frame, text="", background="#eeeeee").grid(row=i, column=0, ipady=15, ipadx=30)
        #---------------------------------------------------------------------------------------------------------------

        directory_background = ttk.Label(self.button_frame, text= "", style="Bold.TLabel")
        directory_background.grid(row=1, column=1, rowspan=4, columnspan=8, sticky=tk.N + tk.S + tk.E + tk.W)

        self.project = tk.StringVar(master)
        self.project.set("----")
        project_entry = ttk.Label(self.button_frame, textvariable=self.project, font=("Sans", "14", "bold"))
        entry_label = ttk.Label(self.button_frame, text="Project code: ")
        entry_label.grid(row=2, column=1, columnspan=2, sticky=tk.E)
        project_entry.grid(row=2, column=3, columnspan=2, sticky=tk.W)
        self.target = tk.StringVar(master)
        self.target.set("----")
        target_entry = ttk.Label(self.button_frame, textvariable=self.target, font=("Sans", "14", "bold"))
        target_label = ttk.Label(self.button_frame, text="Target name: ")
        target_label.grid(row=3, column=5, columnspan=2, sticky=tk.E)
        target_entry.grid(row=3, column=7, columnspan=2, sticky=tk.W)
        self.plate = tk.StringVar(master)
        self.plate.set("----")
        plate_entry = ttk.Label(self.button_frame, textvariable=self.plate, font=("Sans", "14", "bold"))
        plate_label = ttk.Label(self.button_frame, text="Plate name: ")
        plate_label.grid(row=2, column=5, columnspan=2, sticky=tk.E)
        plate_entry.grid(row=2, column=7, columnspan=2, sticky=tk.W)
        self.date = tk.StringVar(master)
        self.date.set("----")
        self.prep_date = tk.StringVar(master)
        self.prep_date.set("----")
        prep_date_entry = ttk.Label(self.button_frame, textvariable=self.prep_date, font=("Sans", "14", "bold"))
        prep_date_label = ttk.Label(self.button_frame, text = "Prep date: ")
        prep_date_label.grid(row=3, column=1, columnspan=2, sticky=tk.E)
        prep_date_entry.grid(row=3, column=3, columnspan=2, sticky=tk.W)
        date_entry = ttk.Label(self.button_frame, textvariable=self.date, font=("Sans", "14", "bold"))
        date_label = ttk.Label(self.button_frame, text= "Image date: ")
        date_label.grid(row=4, column=1, columnspan=2, sticky=tk.E)
        date_entry.grid(row=4, column=3, columnspan=2, sticky=tk.W)

        # All the widgets concerning supplementary image data

        ttk.Label(self.feedback_frame, text="Notes:").grid(row=0, column=2, columnspan=3, sticky=tk.S + tk.W)
        self.notes_entry = tk.Text(self.feedback_frame, width=45, height=15)
        self.notes_entry.grid(row=1, column=1, columnspan=5, rowspan=5, sticky=tk.N)

        ttk.Label(self.feedback_frame, text="Classification:").grid(row=0, column=7, columnspan=3, sticky=tk.S + tk.W)
        self.classification = tk.StringVar()
        self.classification.set("Unspecified")
        self.clear_class = ttk.Radiobutton(self.feedback_frame, text="Clear", variable=self.classification, value="Clear")
        self.clear_class.grid(row=1, column=7, columnspan=2, sticky=tk.W)
        self.precip_class = ttk.Radiobutton(self.feedback_frame, text="Precipitate", variable=self.classification, value="Precipitate")
        self.precip_class.grid(row=2, column=7, columnspan=2, sticky=tk.W)
        self.crystal_class = ttk.Radiobutton(self.feedback_frame, text="Crystal", variable=self.classification, value="Crystal")
        self.crystal_class.grid(row=3, column=7, columnspan=2, sticky=tk.W)
        self.other_class = ttk.Radiobutton(self.feedback_frame, text="Other", variable=self.classification, value="Other")
        self.other_class.grid(row=4, column=7, columnspan=2, sticky=tk.W)


        def save_changes():
            if self.related:
                path = self.related_images[self.related_index]
                path = path.replace("Images", "Image_Data")
                path = path + "/"
                ensure_directory(path)
            else:
                path = os.path.join(os.pardir, os.pardir, "Image_Data/" + self.project.get() + "/")
                ensure_directory(path)
                path = path + self.target.get() + "/"
                ensure_directory(path)
                path = path + self.plate.get() + "/"
                ensure_directory(path)
                path = path + self.date.get() + "/"
                ensure_directory(path)

                well_parts = self.image_list[self.selected_index].split(".")
                path = path + well_parts[0] + "/"
                ensure_directory(path)

            data_file = open(path + "image_data_0.txt", "w+")
            data_file.write("Project Code:" + self.project.get() + ':\n')
            data_file.write("Target Name:" + self.target.get() + ':\n')
            data_file.write("Plate Name:" + self.plate.get() + ':\n')
            data_file.write("Date:" + self.date.get() + ':\n')
            data_file.write('\n')

            data_file.write("Classification:" + self.classification.get() + ':\n')
            data_file.write('\n')
            data_file.write('\n')
            data_file.write("Notes:" + '\n')
            data_file.write('\n')
            data_file.write(self.notes_entry.get("1.0","end-1c"))
            data_file.close()
            self.update_images()
            save_mask(path)


        def save_mask(path):
            mask_file = open(path + "image_mask_0.txt", "w+")
            for item in self.view_panel.find_all():
                if self.view_panel.type(item) == "rectangle":
                    mask_file.write("rectangle" + ':\n')
                    pixel_coordinates = self.view_panel.coords(item)
                    #print(pixel_coordinates)
                    x1 = self.view_panel.canvasx(pixel_coordinates[0])
                    y1 = self.view_panel.canvasy(pixel_coordinates[1])
                    x2 = self.view_panel.canvasx(pixel_coordinates[2])
                    y2 = self.view_panel.canvasy(pixel_coordinates[3])
                    #print(str(x1) + ":" + str(y1) + ":" + str(x2) + ":" + str(y2) + ":")
                    mask_file.write("coordinates:" + str(x1) + ":" + str(y1) + ":" + str(x2) + ":" + str(y2) +":" + '\n')
                elif self.view_panel.type(item) == "text":
                    mask_file.write("text" + ':\n')
                    notes = self.text_list[item]
                    mask_file.write(notes + ":\n")
                    pixel_coordinates = self.view_panel.coords(item)
                    x1 = self.view_panel.canvasx(pixel_coordinates[0])
                    y1 = self.view_panel.canvasy(pixel_coordinates[1])
                    mask_file.write("coordinates:" + str(x1) + ":" + str(y1) + ":" + '\n')
            mask_file.close()


        def check_mask(mask_file):
            mask_file = mask_file + "/" + "image_mask_0.txt"
            if Path(mask_file).exists():
                #print("Path exists")
                mask_file = open(mask_file, "r")
                #print("file opened")
                line = mask_file.readline()
                while line:
                    #print("line")
                    parts = line.split(":")
                    if parts[0] == "rectangle":
                        #print("rectangle")
                        coordinates = mask_file.readline()
                        coordinates=coordinates.split(":")
                        x1 = int(float(coordinates[1]))
                        y1 = int(float(coordinates[2]))
                        x2 = int(float(coordinates[3]))
                        y2 = int(float(coordinates[4]))
                        self.view_panel.create_rectangle(x1, y1, x2, y2, width=5, outline="#ee0000")
                    elif parts[0] == "text":
                        #print("text")
                        notes = mask_file.readline()
                        notes = notes.split(":")
                        notes = notes[0]
                        coordinates = mask_file.readline()
                        coordinates = coordinates.split(":")
                        x1 = int(float(coordinates[1]))
                        y1 = int(float(coordinates[2]))
                        item_id = self.view_panel.create_text((x1, y1), anchor=tk.NW, text=notes, font=("Sans", "16"), fill="#ee0000")
                        self.text_list[item_id] = notes
                    line = mask_file.readline()
                mask_file.close()

        def check_notes():
            if self.related:
                path = self.related_images[self.related_index]
                data_file = path + "/"
                data_file = data_file.replace("Images", "Image_Data")
                data_file = data_file + "image_data_0.txt"
            else:
                well_parts = self.image_list[self.selected_index].split(".")
                well = well_parts[0]
                path = (os.path.join(os.pardir, os.pardir, "Image_Data/" + self.project.get() + "/" + self.target.get()
                                          + "/" + self.plate.get() + "/" + self.date.get() + "/" + well))
                data_file = path + "/" + "image_data_0.txt"

            if Path(data_file).exists():
                data_file = open(data_file, "r")

                # disregards the first four lines, already know them
                data_file.readline()
                data_file.readline()
                data_file.readline()
                data_file.readline()

                # empty space line
                data_file.readline()

                classifications = data_file.readline().split(":")
                self.classification.set(classifications[1])

                # More empty spaces
                data_file.readline()
                data_file.readline()
                data_file.readline()
                data_file.readline()
                notes = ""
                line = data_file.readline()
                while line:
                    notes += line
                    line = data_file.readline()

                self.notes_entry.insert(1.0, notes)

                data_file.close()

            check_mask(path)

        def export_pdf():
            values = []
            name = ""

            values.append(name)

            path = os.path.join(os.pardir, os.pardir, "Images/" + self.project.get() + "/")
            path = path + self.target.get() + "/"
            path = path + self.plate.get() + "/"
            path = path + self.date.get() + "/"

            well = self.image_list[self.selected_index]
            path = path + well

            values.append(path)

            values.append(self.project.get())
            values.append(self.target.get())
            values.append(self.plate.get())
            values.append(self.date.get())

            values.append(self.notes_entry.get("1.0", "end-1c"))

            pdf_writer.create_pdf(values)

        def add_wells():
            if len(self.image_list) > 0:
                for well in self.image_list:
                    well = well.split(".")[0]
                    if well in self.app.locations:
                        continue
                    else:
                        self.app.locations.append(well)
                self.app.custom.set(1)
                if self.app.selection_panel is not None:
                    self.app.paint_custom_diagram()
                self.app.frames["AutoFrame"].paint_selections()


        self.save = ttk.Button(self.feedback_frame, text="Add wells to path", command=add_wells)
        self.save.grid(row=2, column=19, columnspan=4)
        #self.save.config(state="disabled")

        self.export = ttk.Button(self.feedback_frame, text="Export to PDF", command=export_pdf)
        self.export.grid(row=4, column=19, columnspan=4)
        self.export.config(state="disabled")

        self.heat = ttk.Button(self.feedback_frame, text="Display heat map", command=self.show_heat_map)
        self.heat.grid(row=3, column=19, columnspan=4)

        self.view_panel = tk.Canvas(self.image_frame, image=None, height=self.image_height, width=self.image_width)
        self.view_panel.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)

        self.timeline = tk.Canvas(self.feedback_frame, image=None, height=self.feedback_frame.winfo_width()-40)
        self.timeline.grid(row=1, column=10, columnspan=9, rowspan=4, sticky=tk.N + tk.E + tk.W + tk.S)
        time_scrollbar = ttk.Scrollbar(self.timeline, orient=tk.HORIZONTAL)
        self.timeline.config(xscrollcommand=time_scrollbar.set)
        time_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        time_scrollbar.config(command=self.timeline.xview)
        ttk.Label(self.feedback_frame, text="Timeline for well: ").grid(row =0, column =12, columnspan=5, sticky=tk.S)
        self.selected_well = ttk.Label(self.feedback_frame, text="---")
        self.selected_well.grid(row=0, column =16, columnspan=2, sticky=tk.W + tk.S)


        self.related = False
        self.related_images = []
        self.related_PhotoImages = []
        self.related_index = -1

        def load_related():
            self.timeline.delete("all")
            directory = Path(self.directory)
            related_directory = str(directory.parent)
            other_dates = []
            for file in os.listdir(related_directory):
                if os.path.isdir(related_directory + "/" + file):
                    other_dates.append(related_directory + "/" + file)
            other_dates.sort()
            well = self.image_list[self.selected_index]
            for date in other_dates:
                if os.path.isfile(date + "/" + well):
                    self.related_images.append(date + '/' + well)
            display_related()


        def display_related():

            self.timeline_size = 0
            initial_point = self.xPad
            for i in range(len(self.related_images)):
                path = self.related_images[i]
                image = Image.open(path)

                name = path[-20:-10]
                image = image.resize(((int(self.xPad * 3.6)), int(self.xPad * 3.0)), Image.ANTIALIAS)
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
                image = ImageTk.PhotoImage(image)
                self.related_PhotoImages.append(image)

                x_coordinates = initial_point * i * 5 + self.xPad

                self.timeline.create_image(x_coordinates, initial_point, image=image, anchor=tk.NW)
                self.timeline.create_text(x_coordinates + self.xPad / 1.3, initial_point - self.yPad * 2,
                                            anchor=tk.NW, text=name)
                if (x_coordinates + 4 * self.xPad) > self.timeline_size:
                    self.timeline_size = (x_coordinates + 5 * self.xPad)
            self.timeline.config(scrollregion=(0, 0, self.timeline_size, 1000))


        def select_related(event):
            item = self.timeline.find_withtag("current")
            if self.timeline.type(item) == "image":
                x = self.timeline.canvasx(event.x)
                index = math.floor(x/(5*self.xPad))
                update_view_panel(index, related=True)

    #-------------------------------------------------------------------------------------------------------------------

        def choose_directory():

            self.directory = filedialog.askdirectory(parent=self, title="Please select a folder", initialdir=(os.path.join(os.pardir, os.pardir, "Images/")))
            update_directory()

            order = []
            for file in os.listdir(self.directory):
                if os.path.isfile(self.directory + "/" + file):
                    order.append(file)
            order.sort()

            self.disable_sorting()
            self.loaded = False

            self.update_images()


        def update_directory():
            directory = self.directory.split("/")
            self.project.set(directory[5])
            self.target.set(directory[6])
            self.plate.set(directory[7])
            prep_date_path = directory[0] + "/" + directory[1] + "/" + directory[2] + "/" + directory[3] + "/" +\
                             directory[4] + "/" + directory[5] + "/" + directory[6] + "/" + directory[7] + "/" + "prep_date.txt"
            if Path(prep_date_path).exists():
                file = open(prep_date_path)
                contents = file.read()
                self.prep_date.set(contents)
            else:
                print("> No prep date available, deprecated image set")
                self.prep_date.set("----")
            self.date.set(directory[8])
            print("> Loading images in directory:")
            print("> " + self.directory)
            print("> ")

        directory_select_button = ttk.Button(self.button_frame, text="Choose directory to view/edit", command=choose_directory)
        directory_select_button.grid(row=1, column=1, columnspan=7)

        def roundup(x):
            return int(math.ceil(x/4.0)) * 4


        def start_shape(event):
            self.view_panel.focus_set()
            self.x1, self.y1 = event.x, event.y

        def trace_shape(event):
            if self.temp_shape:
                self.view_panel.delete(self.temp_shape)
            temp_shape = self.view_panel.create_rectangle(self.x1, self.y1, event.x, event.y, dash=(10,10), width=5, outline="#ee0000")
            self.temp_shape = temp_shape

        def end_shape(event):
            if self.temp_shape:
                self.view_panel.delete(self.temp_shape)
            self.view_panel.create_rectangle(self.x1, self.y1, event.x, event.y, width=5, outline="#ee0000")

        def clear_all(event):
            self.view_panel.delete("all")
            self.text_list = {}
            self.view_panel.create_image(0, 0, image=self.selected, anchor=tk.NW, state=tk.DISABLED)

        def clear_nearest(event):
            item = self.view_panel.find_closest(event.x, event.y)
            if self.view_panel.type(item) != "image":
                if self.view_panel.type(item) == "text":
                    del self.text_list[item]
                self.view_panel.delete(item)

        def start_text(event):
            self.view_panel.focus_set()
            self.textX, self.textY = event.x, event.y
            self.open_notes_window()

        def select_image(event):
            item = self.list_panel.find_withtag("current")
            if self.list_panel.type(item) == "image":
                x = self.list_panel.canvasx(event.x)
                y = self.list_panel.canvasy(event.y)
                index = roundup(math.floor(((y - self.xPad) / (self.xPad))) -1)
                index += math.floor((x - self.xPad) / (4*self.xPad))

                update_view_panel(index)

        def update_view_panel(index, related=False):

            if self.selected is not None:
                save_changes()

            self.text_list = {}
            self.classification.set("Unknown")
            self.notes_entry.delete(1.0, tk.END)
            if related:
                image = self.related_images[index]
                image = Image.open(image)
                image = image.resize((int(self.image_width), int(self.image_height)), Image.ANTIALIAS)
                image = ImageTk.PhotoImage(image)
                self.save.config(state='enabled')
                self.export.config(state="enabled")
                self.selected = image
                self.view_panel.delete("all")
                self.view_panel.create_image(0,0, image=image, anchor=tk.NW, state=tk.DISABLED)
                self.related_index = index
                self.related = True
                check_notes()
                return

            self.related_index = -1
            self.related = False
            self.related_names = []
            self.related_images = []
            self.related_PhotoImages = []
            name = self.image_list[index]
            name = name[:-4]
            image = Image.open(self.directory + "/" + self.image_list[index])
            width, height = image.size
            ratio = height/width
            image = image.resize((int(self.image_width), int(self.image_height)), Image.ANTIALIAS)
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
            image = ImageTk.PhotoImage(image)
            self.selected = image
            self.selected_index = index
            #self.save.config(state="enabled")
            self.export.config(state='enabled')
            self.selected_well.config(text=name)
            threading.Thread(target=load_related(), args=())

            self.view_panel.delete("all")
            self.view_panel.create_image(0,0, image=self.selected, anchor=tk.NW, state=tk.DISABLED)
            check_notes()

        def iterate_right(event):
            if not self.directory:
                return
            if self.selected_index == -1 or self.selected_index == len(self.image_list)-1:
                index = 0
            else:
                index = self.selected_index + 1
            update_view_panel(index)

        def iterate_left(event):
            if not self.directory:
                return
            if self.selected_index == -1 or self.selected_index == 0:
                index = len(self.image_list)-1
            else:
                index = self.selected_index - 1
            update_view_panel(index)

        def set_focus(event):
            self.list_panel.focus_set()




        self.list_panel.bind("<Right>", iterate_right)
        self.list_panel.bind("<Left>", iterate_left)
        self.list_panel.bind("<Button-1>", set_focus)

        self.view_panel.bind("<Right>", iterate_right)
        self.view_panel.bind("<Left>", iterate_left)
        self.feedback_frame.bind("<Right>", iterate_right)
        self.feedback_frame.bind("<Left>", iterate_left)
        self.bind("<Right>", iterate_right)
        self.bind("<Left>", iterate_left)
        self.master.bind("<Right>", iterate_right)
        self.master.bind("<Left>", iterate_left)
        self.clear_class.bind("<Right>", iterate_right)
        self.clear_class.bind("<Left>", iterate_left)
        self.precip_class.bind("<Right>", iterate_right)
        self.precip_class.bind("<Left>", iterate_left)
        self.crystal_class.bind("<Right>", iterate_right)
        self.crystal_class.bind("<Left>", iterate_left)
        self.other_class.bind("<Right>", iterate_right)
        self.other_class.bind("<Left>", iterate_left)
        self.view_panel.bind("<Button-1>", start_shape)
        self.view_panel.bind("<B1-Motion>", trace_shape)
        self.view_panel.bind("<ButtonRelease-1>", end_shape)

        self.view_panel.bind("<Button-2>", clear_nearest)
        self.view_panel.bind("<Shift-Button-2>", clear_all)

        self.view_panel.bind("<Button-3>", start_text)

        self.list_panel.bind("<Button-1>", select_image)

        self.timeline.bind("<Button-1>", select_related)

        self.app.loading_screen.progress.step(33)
        self.app.loading_screen.label.config(text="Loading complete!")
        self.app.loading_screen.update()

    #-------------------------------------------------------------------------------------------------------------------

    def display_images(self, order, j):
        size = len(order)
        j = j * 10
        initial_point = self.xPad * 2
        for i in range(size):
            name = order[i]
            image = self.thumbnail_list[order[i]]

            x_coordinates = initial_point * ((i + j) % 4) * 2 + self.xPad
            y_coordinates = initial_point * (math.floor((i + j) / 4) * 2) + self.xPad
            if (y_coordinates + 4 * self.xPad) > self.scroll_size:
                self.scroll_size = (y_coordinates + 4 * self.xPad)
            self.list_panel.create_image(x_coordinates, y_coordinates, image=image, anchor=tk.NW)
            self.list_panel.create_text(x_coordinates + self.xPad / 2, y_coordinates + self.yPad + (self.xPad * 2),
                                        anchor=tk.NW, text=name)
        self.list_panel.config(scrollregion=(0, 0, 1000, self.scroll_size))

    #-------------------------------------------------------------------------------------------------------------------

    def display_first(self, order, j):
        size = len(order)
        j = j * 10
        initial_point = self.xPad * 2
        for i in range(size):
            name = order[i]

            image = Image.open(self.directory + "/" + name)
            image = image.resize((int(self.xPad * 2.4), int(self.xPad * 2)), Image.ANTIALIAS)
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
            image = ImageTk.PhotoImage(image)
            self.thumbnail_list[name] = image

            x_coordinates = initial_point * ((i + j) % 4) * 2 + self.xPad
            y_coordinates = initial_point * (math.floor((i + j) / 4) * 2) + self.xPad
            if (y_coordinates + 4 * self.xPad) > self.scroll_size:
                self.scroll_size = (y_coordinates + 4 * self.xPad)
            self.list_panel.create_image(x_coordinates, y_coordinates, image=image, anchor=tk.NW)
            self.list_panel.create_text(x_coordinates + self.xPad / 2, y_coordinates + self.yPad + (self.xPad * 2),
                                        anchor=tk.NW, text=name)
        self.list_panel.config(scrollregion=(0, 0, 1000, self.scroll_size))

    #-------------------------------------------------------------------------------------------------------------------

    def determine_classifications(self, order):
        self.classifications = []
        size = len(order)
        path = (os.path.join(os.pardir, os.pardir, "Image_Data/" + self.project.get() + "/" + self.target.get()
                             + "/" + self.plate.get() + "/" + self.date.get() + "/"))
        # data_file = path + "/" + "image_data_0.txt"
        for i in range(size):
            well = order[i]
            well = well.split(".")
            well = well[0]
            data_file = path + well + "/" + "image_data_0.txt"
            if Path(data_file).exists():
                data_file = open(data_file, "r")

                # disregards the first four lines, already know them
                data_file.readline()
                data_file.readline()
                data_file.readline()
                data_file.readline()

                # empty space line
                data_file.readline()

                data_classifications = data_file.readline().split(":")
                if len(data_classifications) > 1:
                    classification = data_classifications[1]
                    if (classification == "Clear"):
                        self.classifications.append(1)
                    elif (classification == "Precipitate"):
                        self.classifications.append(2)
                    elif (classification == "Crystal"):
                        self.classifications.append(3)
                    elif (classification == "Other"):
                        self.classifications.append(4)
                else:
                    self.classifications.append(0)
                data_file.close()
            else:
                self.classifications.append(0)

    #-------------------------------------------------------------------------------------------------------------------

    def update_images(self):

        self.disable_sorting()
        self.list_panel.delete("all")
        self.scroll_size = 0
        val = self.sorting.get()
        selected = []
        order = []
        for file in os.listdir(self.directory):
            if os.path.isfile(self.directory + "/" + file):
                order.append(file)
        order.sort()
        self.determine_classifications(order)
        for i in range(len(self.classifications)):
            if self.classifications[i] == val:
                selected.append(order[i])


        if val == -1:
            self.image_list = order
        else:
            self.image_list = selected

        chunks = [self.image_list[x:x+10] for x in range(0, len(self.image_list), 10)]
        threads = []

        if self.loaded == False:
            for i in range(len(chunks)):
                threading.Thread(target=self.display_first, args=(chunks[i], i)).start()
            self.loaded = True
        else:
            for i in range(len(chunks)):
                threading.Thread(target=self.display_images, args=(chunks[i], i)).start()

        self.enable_sorting()


    #-------------------------------------------------------------------------------------------------------------------

    def disable_sorting(self):
        self.all_button.config(state="disabled")
        self.unsorted_button.config(state="disabled")
        self.clear_button.config(state="disabled")
        self.precip_button.config(state="disabled")
        self.crystal_button.config(state="disabled")
        self.other_button.config(state="disabled")

    #-------------------------------------------------------------------------------------------------------------------

    def enable_sorting(self):
        self.all_button.config(state="enabled")
        self.unsorted_button.config(state="enabled")
        self.clear_button.config(state="enabled")
        self.precip_button.config(state="enabled")
        self.crystal_button.config(state="enabled")
        self.other_button.config(state="enabled")


    #-------------------------------------------------------------------------------------------------------------------

    def open_notes_window(self):
        """Opens a window with a text box for typing notes
        """

        top = tk.Toplevel()
        width = 300
        height = 40
        top.geometry("%dx%d+%d+%d" % (width, height, self.screen_width/2 + self.textX + width/2, self.textY + height/2))
        top.title("Press 'Enter' key to post")
        self.text_box = tk.Text(top, height=1, width=50, font=("Sans", "12"))
        self.text_box.grid(row=1, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.text_box.focus_set()
        def finish(event):
            notes = self.text_box.get("1.0", "end-1c")
            top.destroy()
            item_id = self.view_panel.create_text((self.textX, self.textY), anchor=tk.NW, text=notes, font=("Sans", "16"), fill="#ee0000")
            self.text_list[item_id] = notes

        self.text_box.bind("<Return>", finish)
        top.mainloop()

    #-------------------------------------------------------------------------------------------------------------------

    def show_heat_map(self):

        if self.heat_window is not None:
            self.heat_window.lift()
            return

        top = tk.Toplevel()
        top.title("Custom well input")

        self.heat_map = tk.Canvas(top, height=760, width=1040)
        self.heat_map.create_rectangle(10, 10, 1030, 720, fill="#cccccc")

        self.heat_map.grid(row=0, column=0)

        def close():
            self.heat_window = None
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", close)

        OKButton = tk.Button(top, text="Close", command=close)
        OKButton.grid(row=1, column=0)

        self.paint_heat_diagram()

        self.heat_window = top
        self.heat_window.mainloop()

    def paint_heat_diagram(self):

        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        cols = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        wells = ['1', '2', '3']

        total_wells = [row + str(col) + '-' + str(well) for row in rows for col in cols for well in wells]

        for row in rows:
            row_int = int(ord(row)) - 65
            y1 = 110 + row_int * 80
            self.heat_map.create_text(40, y1, text=row, font=("Sans", "20", "bold"))

        for column in cols:
            col_int = int(column) - 1
            x1 = 90 + (col_int * 80)
            self.heat_map.create_text(x1, 40, text=column, font=("Sans", "20", "bold"))

        for well in total_wells:
            coordinates = self.app.well_to_coordinates(well)
            self.heat_map.create_rectangle(coordinates[0], coordinates[1], coordinates[2], coordinates[3],
                                                  fill="white")

        for i in range(len(self.image_list)):
            well = self.image_list[i].split(".")[0]
            coordinates = self.app.well_to_coordinates(well)
            classification = self.classifications[i]
            color = ""
            if classification == 0:
                color = "black"
            elif classification == 1:
                color = "white"
            elif classification == 2:
                color = "red"
            elif classification == 3:
                color = "green"
            elif classification == 4:
                color = "yellow"
            self.heat_map.create_rectangle(coordinates[0], coordinates[1], coordinates[2], coordinates[3],
                                                  fill=color)