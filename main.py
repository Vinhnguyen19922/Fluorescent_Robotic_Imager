#!/usr/bin/python3
from application import Application
import threading

"""Main module for running the HarkerBio Robotic Imager
"""

if __name__ == '__main__':

    app = Application()
    app.title("HarkerBIO Fluorescent Robotic Imager")
    print("> Welcome to the HarkerBio flourescent robotic imager")
    print(" ")
    #setup()

    app.update_idletasks()
    app.update()
    app.loading_screen.destroy()
    app.deiconify()

    #app.cam.set_with_callback()

    threading.Thread(target=app.mainloop(), args=()).start()
#----------------------------------------------------------------------------------------------------















