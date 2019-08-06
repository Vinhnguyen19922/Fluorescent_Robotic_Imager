# Fluorescent_Robotic_Imager
Code and .obj files for construction of a robotic imager capable of using visible fluorescence to automatically image plates from protein crystallization experiments

File breakdown:

  Files used to create and control the GUI:
    
    application.py    - the main GUI file, parent of the different modes. Contains code for all common GUI functions.
    
    auto_frame.py     - the GUI frame representing automatic mode. Contains all code for automatic mode display and GUI functionality.
    
    manual_frame.py   - the GUI frame representing manual mode. Contains all code for manual mode display and GUI functionality.
    
    viewing_frame.py  - the GUI frame representing editing mode. Contains all code for editing mode display and GUI functionality.
    
    
  Files used to control the imaging robot:
  
    imager_controls.py  - the "brain" of the robot, contains the functions for the automatic capture of images, autocorrection, plate                             loading, and all other movement of the robot.
    
    arduino_controls.py - contains functions that send various serial commands to the arduino, thus controlling all of the instrument's                           peripherals.
    
    fluorescent_imager_arduino.ino    - the file to be uploaded to the arudino microcontroller. Receives the serial commands from                                               arduino_controls.py and activates the corresponding peripherals.
    
 
 Files for camera and image utilities:
 
    camera.py           - the ToupCam API, allowing interface with the Amscope camera used in this project.
    
    core.py             - sets initialization values for the ToupCam camera.
    
    image_utils.py      - a set of helper functions for manipulating images.
    
    pyramid.py          - contains the functions for constructing a Laplacian pyramid for focus-stacking separate z-slices into an                                 enhanced depth-of-field image.
    
    hough_circles_parameter_search.py   - a small GUI program that loads a set of images and allows the user to adjust individual                                                 parameters of the openCV hough_circles functions. Necessary to get pixel-perfect accuracy for                                           the XY-autocorrect feature.
    
    
 Files for other utilities:
 
    automated_MARCO.py    - contains the data for loading the MARCO system from saved_model.pb and using it to automatically classify a                             set of images.
    
    jpeg2json.py          - used with MARCO to get the data into the proper format.
    
    gcodesender.py        - contains the functions for sending gcode commands to the 3D-printer used as the base of the imaging robot.
    
    utils.py              - basic utility functions that didn't fit in any other specific category or file. 
    
    
    
    
