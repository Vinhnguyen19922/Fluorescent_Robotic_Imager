import gcodesender as gc
import image_utils
import time
import tkinter as tk
from utils import *
import datetime
import cv2
import threading
import pyramid
import Automated_MARCO


class imager_controls():

    def __init__(self, serial_port, app):
        self.app = app
        self.s = serial_port

    def ping_location(self, z=False):
        """Pings the imager for its current location

        Sends a signal to the imager asking for current position along the 3-axes.
        Parses the received string into floating point values representing mm from home.

        (Caution: Coordinates are directly updated to destination position after transit has begun,
        but often before is has completed. This can serve as a suitable holding
        mechanism for small distances (well to well), but doesn't work for longer transits
        (well to home, home to first well, etc.))

        Args:
            s: The serial port connecting the imager
            z: Optional variable which determines whether z-axis data is also parsed and returned

        Returns:
            2 or 3 floating point values representing the 'current' position of the imager
            along the X, Y, and optionally Z axes.
        """

        gc.sendGCode(self.s, "gcode/ping_location.gcode")
        stuff = self.s.readline() # Format [VALUE] X:xx.xxx Y:yy.yyy Z:zz.zzz E:e.eeeee
        grbl_out = stuff.decode()  # Wait for response with carriage return
        feedback = grbl_out.strip()
        while (feedback[1] != 'V'):
            stuff = self.s.readline()  # Format [VALUE] X:xx.xxx Y:yy.yyy Z:zz.zzz E:e.eeeee
            grbl_out = stuff.decode()  # Wait for response with carriage return
            feedback = grbl_out.strip()
        if (feedback[11] == "."):
            currentX = float(feedback[10:15])
            feedback = feedback[16:]
        elif(feedback[12] == "."):
            currentX = float(feedback[10:16])
            feedback = feedback[17:]
        elif(feedback[13] == "."):
            currentX = float(feedback[10:17])
            feedback = feedback[18:]

        if (feedback[3] == "."):
            currentY = float(feedback[2:7])
            feedback = feedback[8:]
        elif (feedback[4] == "."):
            currentY = float(feedback[2:8])
            feedback = feedback[9:]
        elif (feedback[5] == "."):
            currentY = float(feedback[2:9])
            feedback = feedback[10:]

        if z == False:

            return currentX, currentY

        else:
            if (feedback[3] == "."):
                currentZ = float(feedback[2:7])

            elif (feedback[4] == "."):
                currentZ = float(feedback[2:8])

            elif (feedback[5] == "."):
                currentZ = float(feedback[2:9])

        return currentX, currentY, currentZ

#-----------------------------------------------------------------------------------------------------------------------

    def load_tray(self):
        """Moves the plate into position for easy tray loading.

        Raises Z axis by 50mm and moves Y axis forward by 120mm

        Args:
            s: The serial port connecting to the imager
        """

        self.go_home()
        gc.sendGCode(self.s, "gcode/load_tray.gcode")
        print("> Press 'OK' when tray is loaded")
        print(" ")

#-----------------------------------------------------------------------------------------------------------------------

    def set_height(self):
        """Sets the imager to an in-focus height during manual-mode initialization

        Raises Z axis by 20.3mm

        Args:
            s: The serial port connecting to the imager"""

        gc.sendGCode(self.s, "gcode/set_height.gcode")

#-----------------------------------------------------------------------------------------------------------------------

    def go_home(self):
        """Moves the imager to the default home position.

        Home is determined by the screws and contacts along each axis,
        and can be adjusted with a small phillips screwdriver.
        (Caution: DO NOT ADJUST WITHOUT CHANGING THE MAX X,Y,Z VALUES.
        SEVERE MOTOR DAMAGE MAY OCCUR.)

        Args:
            s: The serial port connecting the imager
        """

        gc.sendGCode(self.s, "gcode/home.gcode")

#-----------------------------------------------------------------------------------------------------------------------

    def autocorrect(self, currentX, currentY):
        """Centers the camera on the current well.

        Uses the method of Hough Circles to detemine the circle closest to the center
        of the image. Calculates the distance between the center of this circle and the
        center of the image, and adjusts the imager by this distance.

        REQUIREMENTS:
            Camera must be kept at a fixed orientation, with the cord facing
            away from the front of the machine.
            Lighting must also be kept constant across all images, otherwise false
            positives may arise during circle detection.

        Args:
            currentX: The current X location, in mm
            currentY: The current Y location, in mm

        Returns:
            Updated values for x and y
        """

        mm_per_pixel = 0.0020  # Value should be between 0.0020 and 0.0025
        image = self.app.cam.get_pil_image()

        X, Y, R = image_utils.find_largest_circle(image)

        #print("X: " + str(X))
        #print("Y: " + str(Y))
        #print("Radius: " + str(R))

        centerX = 614
        centerY = 461

        #print("Center point: " + str(centerX) + " " + str(centerY))

        if R == 0:
            #print("unable to autocorrect")
            return 0,0

        delX = (centerX-(X*2))
        delY = (centerY-(Y*2))

        mmX = delX * mm_per_pixel
        mmY = delY * mm_per_pixel

        x = currentX + mmX
        y = currentY + mmY

        return x, y

    ####################################################################################################################

    def run_auto_imager(self, extension, locations):
        """Runs the auto imager using one of the pre-defined well patterns.

        Args:
            extension: The plate extension used to send the correct G-code
            locations: a list of strings representing wells to be imaged.
        """

        if len(locations) == 0:
            print("> Please select which wells to image")
            print("")
            return

        project = self.app.frames["AutoFrame"].project.get()
        target = self.app.frames["AutoFrame"].target.get()
        plate = self.app.frames["AutoFrame"].plate.get()
        prep_date = self.app.frames["AutoFrame"].date.get()

        if project == "" or target == "" or plate == "":
            print("> Must fill out project, target, and ")
            print("> plate name before imaging can begin")
            print("> ")
            return

        # Get the date and time at which imaging began
        date = datetime.date.today()
        #start_time = datetime.time
        project_data = [project, target, plate, date]

        # Ensure the directories exist to store the images
        path = os.path.join(os.pardir, os.pardir, "Images/" + project + "/")
        ensure_directory(path)
        path = path + target + "/"
        ensure_directory(path)
        path = path + plate + "/"
        ensure_directory(path)
        if prep_date != "":
            self.app.write_prep_date(prep_date, path)
        else:
            self.app.frames["AutoFrame"].date.set(self.app.read_prep_date(path))
        self.app.write_prep_date(prep_date, path)
        path = path + str(date) + "/"
        ensure_directory(path)

        self.app.disable_manual()

        self.app.frames["AutoFrame"].cancelButton['state'] = tk.NORMAL
        self.app.frames["AutoFrame"].goButton['state'] = tk.DISABLED

        print("> Running standard configuration")
        size = len(locations)
        coordinates = self.app.determine_coordinates(locations)
        new_coordinates = coordinates
        step = 100/size
        print("> Homing coordinates")

        self.app.arduino.lights_on()
        self.app.arduino.fan_on()
        self.go_home()

        x = self.app.FIRST_X
        y = self.app.FIRST_Y
        z = self.app.FIRST_Z

        if self.app.cancelled:
            self.app.abort()
            self.go_home()
            return

        if self.app.type.get() == "Intelli-plate 96-3":

            gc.writeGCode(coordinates, "gcode/96-3")
            gc.writeTemporary(self.app.FIRST_X, self.app.FIRST_Y, self.app.FIRST_Z, first=True)
            gc.sendGCode(self.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            time.sleep(20)

            delX = 0
            delY = 0
            j = 0

            for loc in locations:

                z_dist = (float(self.app.z_dist.get()) / 10.0) / float(self.app.slices.get())  # 0.5 determines the total distance
                j += 1
                start = time.time()
                if self.app.cancelled:
                    self.app.abort()
                    self.go_home()
                    return
                x = float(coordinates[loc][0]) - delX
                y = float(coordinates[loc][1]) - delY
                z = self.app.FIRST_Z
                #print(z)
                #print(x)
                #print(y)
                gc.writeTemporary(x, y, z=z)
                gc.sendGCode(self.s, "gcode/temp.gcode")
                os.remove("gcode/temp.gcode")
                #print("> Moving to well " + loc)
                #gc.sendGCode(self.s, extension + loc + '.gcode')
                time.sleep(.5)
                while(True):
                    currentX, currentY = self.ping_location()
                    if (abs(currentX - x) < .1) and (abs(currentY - y) < .1):
                        break
                    else:
                        time.sleep(.5)

                # Printer is approximately above the well. Autocorrect if desired
                time.sleep(1.5)

                if self.app.do_autocorrect.get():
                    #print("> Correcting position")
                    newX, newY = self.autocorrect(x, y)

                    if (newX is not 0 and newY is not 0):
                        delX += x - newX
                        delY += y - newY
                        x = newX
                        y = newY

                        gc.writeTemporary(x, y)
                        new_coordinates[loc] = x,y
                        gc.sendGCode(self.s, "gcode/temp.gcode")
                        os.remove("gcode/temp.gcode")

                #When we reach this step the printer is where it needs to be
                time.sleep(1.5)
                well_path = path + loc + "/"
                ensure_directory(well_path)
                for i in range(self.app.slices.get()):

                    save_path = well_path + "-slice" + str(i+1) + ".jpg"
                    self.app.cam.save(save_path)
                    z = z + z_dist
                    gc.writeTemporary(x, y, z=z)
                    gc.sendGCode(self.s, "gcode/temp.gcode")
                    os.remove("gcode/temp.gcode")
                    time.sleep(1.5)

                order = []
                for file in os.listdir(well_path):
                    order.append(file)
                order.sort()
                images = []
                for file in order:
                    image = cv2.imread(well_path + "/" + file)
                    # image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    images.append(image)

                threading.Thread(target=pyramid.stack_focus, args=(images, path, loc)).start()

                self.app.frames["AutoFrame"].progress.step(step)
                self.app.frames["AutoFrame"].output.update_idletasks()
                self.app.set_time(start, size - j)


            print("> Classifying images with MARCO...")
            Automated_MARCO.predict(path, project_data)
            print("> Classification complete")

            parts = path.split("/")
            path = ""
            for i in range(len(parts) - 2):
                path += parts[i] + "/"
            self.app.check_previous_notes(path, str(date))

            if self.app.frames["AutoFrame"].laser_var.get() == 1:
                print("> Running laser fluorescence imaging")
                self.run_auto_laser_imager(extension, locations, new_coordinates)
                return
            else:
                self.app.clean_up()
                self.go_home()
                print("> Resetting imager")
                print("")
                return

        elif self.app.type.get() == "Greiner 1536":

            gc.writeGCode(coordinates, "gcode/1536")
            gc.writeTemporary(self.app.FIRST_X, self.app.FIRST_Y, self.app.FIRST_Z)

            time.sleep(20)

            delX = 0
            delY = 0
            j = 0

            for loc in locations:
                z_dist = (float(self.app.z_dist.get()) / 10.0) / float(self.app.slices.get())  # 0.5 determines the total distance
                j += 1
                start = time.time()
                if self.app.cancelled:
                    self.app.abort()
                    self.go_home()
                    return
                x = float(coordinates[loc][0]) - delX
                y = float(coordinates[loc][1]) - delY
                z = self.app.FIRST_Z
                # print(x)
                # print(y)
                gc.writeTemporary(x, y, z=z)
                gc.sendGCode(self.s, "gcode/temp.gcode")
                os.remove("gcode/temp.gcode")
                # print("> Moving to well " + loc)
                # gc.sendGCode(self.s, extension + loc + '.gcode')
                time.sleep(.5)
                while (True):
                    currentX, currentY = self.ping_location()
                    if (abs(currentX - x) < .1) and (abs(currentY - y) < .1):
                        break
                    else:
                        time.sleep(.5)

                # Printer is approximately above the well. Autocorrect if desired
                time.sleep(1.5)

                if self.app.do_autocorrect.get():
                    # print("> Correcting position")
                    newX, newY = self.autocorrect(x, y)

                    if (newX is not 0 and newY is not 0):
                        delX += x - newX
                        delY += y - newY
                        x = newX
                        y = newY

                        gc.writeTemporary(x, y)
                        gc.sendGCode(self.s, "gcode/temp.gcode")
                        os.remove("gcode/temp.gcode")

                # When we reach this step the printer is where it needs to be
                time.sleep(1.5)
                well_path = path + loc + "/"
                ensure_directory(well_path)
                for i in range(self.app.slices.get()):

                    save_path = well_path + "-slice" + str(i + 1) + ".jpg"
                    self.app.cam.save(save_path)
                    z = z + z_dist
                    gc.writeTemporary(x, y, z=z)
                    gc.sendGCode(self.s, "gcode/temp.gcode")
                    os.remove("gcode/temp.gcode")
                    time.sleep(1.5)

                order = []
                for file in os.listdir(well_path):
                    order.append(file)
                order.sort()
                images = []
                for file in order:
                    image = cv2.imread(well_path + "/" + file)
                    # image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    images.append(image)

                self.app.frames["AutoFrame"].progress.step(step)
                self.app.frames["AutoFrame"].output.update_idletasks()
                self.app.set_time(start, size - j)


            print("> Classifying images with MARCO...")
            Automated_MARCO.predict(path, project_data)
            print("> Classification complete")
            parts = path.split("/")
            path = ""
            for i in range(len(parts) - 2):
                path += parts[i] + "/"
            self.app.check_previous_notes(path, str(date))
            self.app.clean_up()
            self.go_home()

    ####################################################################################################################


    def run_custom_imager(self, extension, locations):
        """Runs the auto imger using a custom-defined well pattern.

        Ends of rows are predefined to ensure snake-like movement throughout imaging.

        Args:
            extension: The plate extension used to send the correct G-code
            locations: a list of strings representing wells to be imaged.
        """

        if len(locations) == 0:
            print("> Please select which wells to image")
            print("")
            return

        project = self.app.frames["AutoFrame"].project.get()
        target = self.app.frames["AutoFrame"].target.get()
        plate = self.app.frames["AutoFrame"].plate.get()
        prep_date = self.app.frames["AutoFrame"].date.get()


        if project == "" or target == "" or plate == "":
            print("> Must fill out project, target, and ")
            print("> plate name before imaging can begin")
            print("")
            return

        self.app.disable_manual()

        # Get the date and time at which imaging began
        date = datetime.date.today()
        #start_time = datetime.time
        project_data = [project, target, plate, date]

        # Ensure the directories exist to store the images
        path = os.path.join(os.pardir, os.pardir, "Images/" + project + "/")
        ensure_directory(path)
        path = path + target + "/"
        ensure_directory(path)
        path = path + plate + "/"
        ensure_directory(path)
        if prep_date != "":
            self.app.write_prep_date(prep_date, path)
        else:
            self.app.frames["AutoFrame"].date.set(self.app.read_prep_date(path))
        path = path + str(date) + "/"
        ensure_directory(path)

        self.app.frames["AutoFrame"].cancelButton['state'] = tk.NORMAL
        self.app.frames["AutoFrame"].goButton['state'] = tk.DISABLED

        z_dist = (float(self.app.z_dist.get()) / 10.0) / float(self.app.slices.get())
        self.app.arduino.lights_on()
        self.app.arduino.fan_on()
        x = self.app.FIRST_X
        y = self.app.FIRST_Y
        z = self.app.FIRST_Z

        newLocations = locations.copy()
        print("> Running custom configuration")
        print("> ")

        cols = [[]]

        for i in range(12):
            cols.append([])

        for loc in newLocations:
            column = int(loc[1] + loc[2]) - 1
            cols[column].append(loc)

        for col in cols[1::2]:
            col.sort(key=operator.itemgetter(0, 4), reverse=True)

        self.go_home()

        if self.app.cancelled:
            self.app.abort()
            self.go_home()
            return

        coordinates = self.app.determine_coordinates(newLocations)
        new_coordinates = coordinates
        gc.writeGCode(coordinates, "gcode/96-3")
        gc.writeTemporary(self.app.FIRST_X, self.app.FIRST_Y, self.app.FIRST_Z, first=True)
        gc.sendGCode(self.s, "gcode/temp.gcode")
        os.remove("gcode/temp.gcode")
        time.sleep(20)

        delX = 0
        delY = 0
        j = 0

        size = len(newLocations)
        step = (100/size)

        for i in range(12):
            for loc in cols[i]:
                if self.app.cancelled:
                    self.app.abort()
                    self.go_home()
                    return

                z_dist = (float(self.app.z_dist.get()) / 10.0) / float(self.app.slices.get())  # 0.5 determines the total distance
                j += 1
                start = time.time()
                gc.writeGCode(coordinates, "gcode/96-3")
                x = float(coordinates[loc][0]) - delX
                y = float(coordinates[loc][1]) - delY
                new_coordinates[loc] = x,y
                gc.writeTemporary(x, y, self.app.FIRST_Z)
                gc.sendGCode(self.s, "gcode/temp.gcode")
                os.remove("gcode/temp.gcode")
                #print("> Moving to well " + loc)
                #gc.sendGCode(self.s, extension + loc + '.gcode')
                newLocations.pop(0)

                time.sleep(1.5)
                while (True):
                    currentX, currentY = self.ping_location()
                    if (abs(currentX - x) < .1) and (abs(currentY - y) < .1):
                        break
                    else:
                        time.sleep(1.5)

                time.sleep(1.5)

                if self.app.do_autocorrect.get():
                    # print("> Correcting position")
                    newX, newY = self.autocorrect(x, y)

                    if (newX is not 0 and newY is not 0):
                        delX += x - newX
                        delY += y - newY
                        x = newX
                        y = newY

                        gc.writeTemporary(x, y)
                        gc.sendGCode(self.s, "gcode/temp.gcode")
                        os.remove("gcode/temp.gcode")

                # When we reach this step the printer is where it needs to be
                time.sleep(1.5)
                z = self.app.FIRST_Z
                well_path = path + loc + "/"
                ensure_directory(well_path)
                for i in range(self.app.slices.get()):


                    save_path = well_path + "-slice" + str(i + 1) + ".jpg"
                    self.app.cam.save(save_path)
                    z = z + z_dist
                    gc.writeTemporary(x, y, z=z)
                    gc.sendGCode(self.s, "gcode/temp.gcode")
                    os.remove("gcode/temp.gcode")
                    time.sleep(1.5)
                z = self.app.FIRST_Z

                order = []
                for file in os.listdir(well_path):
                    order.append(file)
                order.sort()
                images = []
                for file in order:
                    image = cv2.imread(well_path + "/" + file)
                    # image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    images.append(image)

                threading.Thread(target=pyramid.stack_focus, args=(images, path, loc)).start()

                self.app.frames["AutoFrame"].progress.step(step)
                self.app.frames["AutoFrame"].output.update_idletasks()
                self.app.set_time(start, size - j)

                if not newLocations:
                    break

        print("> Classifying images with MARCO...")
        Automated_MARCO.predict(path, project_data)
        print("> Classification complete")

        parts = path.split("/")
        path = ""
        for i in range(len(parts)-2):
            path += parts[i] + "/"
        self.app.check_previous_notes(path, str(date))

        if self.app.frames["AutoFrame"].laser_var.get() == 1:
            self.run_custom_laser_imager(extension, locations, new_coordinates)
            return

        else:

            self.app.clean_up()
            self.go_home()
            print("> Resetting imager")
            setup()


    ####################################################################################################################

    def run_auto_laser_imager(self, extension, locations, coordinates):

        if len(locations) == 0:
            print("> Please select which wells to image")
            print("")
            return

        project = self.app.frames["AutoFrame"].project.get()
        target = self.app.frames["AutoFrame"].target.get()
        plate = self.app.frames["AutoFrame"].plate.get()
        prep_date = self.app.frames["AutoFrame"].date.get()

        if project == "" or target == "" or plate == "":
            print("> Must fill out project, target, and ")
            print("> plate name before imaging can begin")
            print("> ")
            return

        # Get the date and time at which imaging began
        date = datetime.date.today()
        # start_time = datetime.time
        project_data = [project, target, plate, date]

        # Ensure the directories exist to store the images
        path = os.path.join(os.pardir, os.pardir, "Images/" + project + "/")
        ensure_directory(path)
        path = path + target + "/"
        ensure_directory(path)
        path = path + plate + "/"
        ensure_directory(path)
        if prep_date != "":
            self.app.write_prep_date(prep_date, path)
        else:
            self.app.frames["AutoFrame"].date.set(self.app.read_prep_date(path))
        self.app.write_prep_date(prep_date, path)
        path = path + str(date) + "/"
        ensure_directory(path)
        path = path + "laser_fluorescence/"
        ensure_directory(path)

        self.app.disable_manual()

        self.app.frames["AutoFrame"].cancelButton['state'] = tk.NORMAL
        self.app.frames["AutoFrame"].goButton['state'] = tk.DISABLED

        print("> Running standard fluorescence configuration")
        size = len(locations)
        step = 100 / size
        print("> Homing coordinates")

        self.go_home()
        self.app.arduino.lights_on()
        self.app.arduino.laser_on()
        self.app.arduino.fan_on()
        self.app.arduino.servo_0()
        self.app.set_camera_fluorscent()
        x = self.app.FIRST_X
        y = self.app.FIRST_Y
        z = self.app.FIRST_Z

        if self.app.cancelled:
            self.app.abort()
            self.go_home()
            return

        if self.app.type.get() == "Intelli-plate 96-3":

            gc.writeTemporary(self.app.FIRST_X, self.app.FIRST_Y, self.app.FIRST_Z, first=True)
            gc.sendGCode(self.s, "gcode/temp.gcode")
            os.remove("gcode/temp.gcode")
            time.sleep(20)

            j = 0

            for loc in locations:

                z_dist = (float(self.app.z_dist.get()) / 10.0) / float(self.app.slices.get())  # 0.5 determines the total distance
                j += 1
                start = time.time()
                if self.app.cancelled:
                    self.app.abort()
                    self.go_home()
                    return
                x = float(coordinates[loc][0])
                y = float(coordinates[loc][1])
                z = self.app.FIRST_Z
                #print(z)
                #print(x)
                #print(y)
                gc.writeTemporary(x, y, z=z)
                gc.sendGCode(self.s, "gcode/temp.gcode")
                os.remove("gcode/temp.gcode")
                #print("> Moving to well " + loc)
                #gc.sendGCode(self.s, extension + loc + '.gcode')
                time.sleep(.5)
                while(True):
                    currentX, currentY = self.ping_location()
                    if (abs(currentX - x) < .1) and (abs(currentY - y) < .1):
                        break
                    else:
                        time.sleep(.5)

                #When we reach this step the printer is where it needs to be
                time.sleep(1.5)
                well_path = path + loc + "/"
                ensure_directory(well_path)
                for i in range(self.app.slices.get()):

                    save_path = well_path + "-slice" + str(i+1) + ".jpg"
                    self.app.cam.save(save_path)
                    z = z + z_dist
                    gc.writeTemporary(x, y, z=z)
                    gc.sendGCode(self.s, "gcode/temp.gcode")
                    os.remove("gcode/temp.gcode")
                    time.sleep(1.5)

                order = []
                for file in os.listdir(well_path):
                    order.append(file)
                order.sort()
                images = []
                for file in order:
                    image = cv2.imread(well_path + "/" + file)
                    # image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    images.append(image)

                threading.Thread(target=pyramid.stack_focus, args=(images, path, loc)).start()

                self.app.frames["AutoFrame"].progress.step(step)
                self.app.frames["AutoFrame"].output.update_idletasks()
                self.app.set_time(start, size - j)


            print("> Classifying images with MARCO...")
            Automated_MARCO.predict(path, project_data)
            print("> Classification complete")

            parts = path.split("/")
            path = ""
            for i in range(len(parts) - 2):
                path += parts[i] + "/"
            self.app.check_previous_notes(path, str(date))

            self.app.clean_up()
            self.go_home()
            self.app.set_camera_default()
            print("> Resetting imager")

########################################################################################################################

    def run_custom_laser_imager(self, extension, locations, coordinates):

        if len(locations) == 0:
            print("> Please select which wells to image")
            print("")
            return

        project = self.app.frames["AutoFrame"].project.get()
        target = self.app.frames["AutoFrame"].target.get()
        plate = self.app.frames["AutoFrame"].plate.get()
        prep_date = self.app.frames["AutoFrame"].date.get()


        if project == "" or target == "" or plate == "":
            print("> Must fill out project, target, and ")
            print("> plate name before imaging can begin")
            print("")
            return

        self.app.disable_manual()

        # Get the date and time at which imaging began
        date = datetime.date.today()
        #start_time = datetime.time
        project_data = [project, target, plate, date]

        # Ensure the directories exist to store the images
        path = os.path.join(os.pardir, os.pardir, "Images/" + project + "/")
        ensure_directory(path)
        path = path + target + "/"
        ensure_directory(path)
        path = path + plate + "/"
        ensure_directory(path)
        if prep_date != "":
            self.app.write_prep_date(prep_date, path)
        else:
            self.app.frames["AutoFrame"].date.set(self.app.read_prep_date(path))
        path = path + str(date) + "/"
        ensure_directory(path)
        path = path + "fluorescence/"

        self.app.frames["AutoFrame"].cancelButton['state'] = tk.NORMAL
        self.app.frames["AutoFrame"].goButton['state'] = tk.DISABLED

        z_dist = (float(self.app.z_dist.get()) / 10.0) / float(self.app.slices.get())
        self.app.arduino.lights_on()
        self.app.arduino.laser_on()
        self.app.arduino.servo_0()
        self.app.set_camera_fluorscent()
        x = self.app.FIRST_X
        y = self.app.FIRST_Y
        z = self.app.FIRST_Z

        newLocations = locations
        print("> Running custom configuration")
        print("> ")

        cols = [[]]

        for i in range(12):
            cols.append([])

        for loc in newLocations:
            column = int(loc[1] + loc[2]) - 1
            cols[column].append(loc)

        for col in cols[1::2]:
            col.sort(key=operator.itemgetter(0, 4), reverse=True)

        self.go_home()

        if self.app.cancelled:
            self.app.abort()
            self.go_home()
            return

        gc.writeTemporary(self.app.FIRST_X, self.app.FIRST_Y, self.app.FIRST_Z, first=True)
        gc.sendGCode(self.s, "gcode/temp.gcode")
        os.remove("gcode/temp.gcode")
        time.sleep(20)

        j = 0

        size = len(newLocations)
        step = (100/size)

        for i in range(12):
            for loc in cols[i]:
                if self.app.cancelled:
                    self.app.abort()
                    self.go_home()
                    return

                z_dist = (float(self.app.z_dist.get()) / 10.0) / float(self.app.slices.get())  # 0.5 determines the total distance
                j += 1
                start = time.time()
                x = float(coordinates[loc][0])
                y = float(coordinates[loc][1])
                gc.writeTemporary(x, y, self.app.FIRST_Z)
                gc.sendGCode(self.s, "gcode/temp.gcode")
                os.remove("gcode/temp.gcode")
                #print("> Moving to well " + loc)
                #gc.sendGCode(self.s, extension + loc + '.gcode')
                newLocations.pop(0)

                time.sleep(1.5)
                while (True):
                    currentX, currentY = self.ping_location()
                    if (abs(currentX - x) < .1) and (abs(currentY - y) < .1):
                        break
                    else:
                        time.sleep(1.5)

                # When we reach this step the printer is where it needs to be
                time.sleep(1.5)
                z = self.app.FIRST_Z
                well_path = path + loc + "/"
                ensure_directory(well_path)
                for i in range(self.app.slices.get()):

                    save_path = well_path + "-slice" + str(i + 1) + ".jpg"
                    self.app.cam.save(save_path)
                    z = z + z_dist
                    gc.writeTemporary(x, y, z=z)
                    gc.sendGCode(self.s, "gcode/temp.gcode")
                    os.remove("gcode/temp.gcode")
                    time.sleep(1.5)
                z = self.app.FIRST_Z

                order = []
                for file in os.listdir(well_path):
                    order.append(file)
                order.sort()
                images = []
                for file in order:
                    image = cv2.imread(well_path + "/" + file)
                    # image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    images.append(image)

                threading.Thread(target=pyramid.stack_focus, args=(images, path, loc)).start()

                self.app.frames["AutoFrame"].progress.step(step)
                self.app.frames["AutoFrame"].output.update_idletasks()
                self.app.set_time(start, size - j)

                if not newLocations:
                    break

        print("> Classifying images with MARCO...")
        Automated_MARCO.predict(path, project_data)
        print("> Classification complete")

        parts = path.split("/")
        path = ""
        for i in range(len(parts)-2):
            path += parts[i] + "/"
        self.app.check_previous_notes(path, str(date))

        self.app.clean_up()
        self.go_home()
        self.app.set_camera_default()
        print("> Resetting imager")

    ####################################################################################################################


    def find_single_well(self):
        """Manual mode command for moving a well of the user's choice
        """

        extension = ''
        if self.app.type.get() == 'Intelli-plate 96-3':
            extension = 'gcode/96-3/'

        loc = self.app.frames["ManualFrame"].well.get()
        locations = []
        locations.append(loc)
        coordinates = self.app.determine_coordinates(locations)
        self.app.frames["ManualFrame"].x = coordinates[loc][0]
        self.app.frames["ManualFrame"].y = coordinates[loc][1]

        gc.writeTemporary(self.app.frames["ManualFrame"].x, self.app.frames["ManualFrame"].y, self.app.FIRST_Z)
        gc.sendGCode(self.s, "gcode/temp.gcode")
        os.remove("gcode/temp.gcode")


        self.print_current_location()

    ####################################################################################################################

    def right_one_well(self):
        current_well = self.app.frames["ManualFrame"].well.get()
        char = ord(current_well[0])
        if len(current_well) == 5:
            col = int(current_well[4])
        else:
            col = int(current_well[3])
        if col == 1:
            char -= 1
            if char < 65:
                return
            else:
                new_well = str(chr(char) + current_well[1:4] + str(3))
                self.app.frames["ManualFrame"].well.set(new_well)
                self.find_single_well()
        else:
            col -= 1
            new_well = current_well[:4] + str(col)
            self.app.frames["ManualFrame"].well.set(new_well)
            self.find_single_well()

    ####################################################################################################################

    def left_one_well(self):
        current_well = self.app.frames["ManualFrame"].well.get()
        char = ord(current_well[0])
        if len(current_well) == 5:
            col = int(current_well[4])
        else:
            col = int(current_well[3])
        if col == 3:
            char += 1
            if char > 72:
                return
            else:
                new_well = str(chr(char) + current_well[1:4] + str(1))
                self.app.frames["ManualFrame"].well.set(new_well)
                self.find_single_well()
        else:
            col += 1
            new_well = current_well[:4] + str(col)
            self.app.frames["ManualFrame"].well.set(new_well)
            self.find_single_well()


    ####################################################################################################################

    def up_one_well(self):
        current_well = self.app.frames["ManualFrame"].well.get()
        row = int(current_well[1:-2])
        row -= 1
        if row < 1:
            return
        elif row < 10:
            new_well = current_well[0] + str(0) + str(row) + current_well[-2:]
        else:
            new_well = current_well[0] + str(row) + current_well[-2:]

        self.app.frames["ManualFrame"].well.set(new_well)
        self.find_single_well()

    ####################################################################################################################

    def down_one_well(self):
        current_well = self.app.frames["ManualFrame"].well.get()
        row = int(current_well[1:-2])
        row += 1
        if row > 12:
            return
        elif row < 10:
            new_well = current_well[0] + str(0) + str(row) + current_well[-2:]
        else:
            new_well = current_well[0] + str(row) + current_well[-2:]
        self.app.frames["ManualFrame"].well.set(new_well)
        self.find_single_well()

    ####################################################################################################################

    def print_current_location(self):
        """Prints the current location of the imager, in mm
        """

        currentX, currentY, currentZ = self.ping_location(z=True)
        print("> Current location:")
        print("> X: " + str(currentX))
        print("> Y: " + str(currentY))
        print("> Z: " + str(currentZ))
        print("")

    ####################################################################################################################