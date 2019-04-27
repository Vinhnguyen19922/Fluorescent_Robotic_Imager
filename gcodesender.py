import serial
import time

def removeComment(string):
    if (string.find(';')==-1):
        return string
    else:
        return string[:string.index(';')]

def sendGCode(s, filename):

    # Open g-code file
    f = open(filename, 'r');
    #print ("Opening gcode file")

    #print("Sending gcode")

    for line in f:
        l = removeComment(line)
        l = l.strip() # Strip all EOL characters for streaming
        if (l.isspace()==False and len(l)>0):
            #print ("Sending: " + l)
            l = str.encode(l + '\n')
            s.write(l) # Send g-code bloc
    f.close()

def openSerialPort(port):
    try:
        s = serial.Serial(port,115200)
        print ("> Opening serial port")
        wake_up = str.encode("\r\n\r\n")
        s.write(wake_up)
        time.sleep(2)
        s.flushInput()
        return s
    except:
        print("> There seems to be a problem")
        print(" ")
        print("> Please verify that the printer")
        print("> is connected to the right port")
        print("> and try again")
        print(" ")


def closeSerialPort(s):
    s.close()


def writeGCode(coordinates, extension):
    for key in coordinates:
        file_name = extension + '/' + key + ".gcode"
        f = open(file_name, "w+")
        f.write("G0 " + "X" + str(coordinates[key][0]) + " " + "Y" + str(coordinates[key][1]))
        f.close()

def writeTemporary(x, y, z=None, first=False):
    file_name = "gcode/temp.gcode"
    f = open(file_name, "w+")
    if first:
        f.write("G90" + '\n')
    if z:
        f.write("G0 " + "X" + str(x) + " Y" + str(y) + " Z" + str(z))
    else:
        f.write("G0 " + "X" + str(x) + " Y" + str(y))
    f.close()

def writeTemporaryZ(z):
    file = "gcode/temp.gcode"
    f = open(file, "w+")
    f.write("G0 " + "Z" + str(z))
    f.close()