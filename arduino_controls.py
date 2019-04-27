import serial

class arduino_control():

    def __init__(self, arPort):
        self.arduino = serial.Serial(arPort, 9600)

#-----------------------------------------------------------------------------------------------------------------------

    def lights_on(self):
        """Sends a signal to the arduino to turn on the electroluminescent plate

        On signal is the char 'a', because parsing ints from byte data
        was initially ineffective
        """

        self.arduino.write(b'a')


#-----------------------------------------------------------------------------------------------------------------------

    def lights_off(self):
        """Sends a signal to the arduino to turn off the electroluminescent plate

        Off signal is the char 'b'
        """

        self.arduino.write(b'b')

#-----------------------------------------------------------------------------------------------------------------------

    def laser_on(self):
        """Sends a signal to the arduino to turn on the blue laser

        On signal is the char 'c'
        """

        self.arduino.write(b'c')

#-----------------------------------------------------------------------------------------------------------------------

    def laser_off(self):
        """Sends a signal to the arduino to turn off the blue laser

        Off signal is the char 'd'
        """

        self.arduino.write(b'd')

#-----------------------------------------------------------------------------------------------------------------------

    def servo_0(self):
        """Sends a signal to the arduino to turn the filter wheel servo to 0 degrees

        0 signal is the char 'e'
        """

        self.arduino.write(b'e')

#-----------------------------------------------------------------------------------------------------------------------

    def servo_90(self):
        """Sends a signal to the arduino to turn the filter wheel servo to 90 degrees

        90 signal is the char 'f'
        """

        self.arduino.write(b'f')

#-----------------------------------------------------------------------------------------------------------------------

    def servo_180(self):
        """Sends a signal to the arduino to turn the filter wheel servo to 180 degrees

        180 signal is the char 'g'
        """

        self.arduino.write(b'g')

#-----------------------------------------------------------------------------------------------------------------------

    def open_sesame(self):
        """Opens the pod bay doors to load or remove a tray

        Open signal is the char 'h'
        """

        self.arduino.write(b'h')

#-----------------------------------------------------------------------------------------------------------------------

    def close_sesame(self):
        """Closes the loading panel

        Close signal is the char 'i'
        """

        self.arduino.write(b'i')

#-----------------------------------------------------------------------------------------------------------------------

    def fan_on(self):
        """Turns the cooling fans on

        On signal is the char 'j'
        """

        self.arduino.write(b'j')

#-----------------------------------------------------------------------------------------------------------------------

    def fan_off(self):
        """Turns the cooling fans off

        Off signal is the char 'k'
        """

        self.arduino.write(b'k')

#-----------------------------------------------------------------------------------------------------------------------

    def UV_on(self):
        """Turns the UV LED on"""

        self.arduino.write(b'm')

#-----------------------------------------------------------------------------------------------------------------------

    def UV_off(self):
        """Turns the UV LED off"""

        self.arduino.write(b'n')

#-----------------------------------------------------------------------------------------------------------------------