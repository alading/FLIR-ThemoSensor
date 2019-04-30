'''
Eample of simple PNG frame stream receiver server


Note: uses PIL, the library Pillow is recommended
https://pypi.python.org/pypi/Pillow
'''

import socket
import sys
import os
from threading import Thread
from io import BytesIO
from PIL import Image, ImageTk

try:
    import tkinter
except ImportError:
    import Tkinter

    tkinter = Tkinter

HOST = ''  # Symbolic name meaning all available interfaces
PORT = 12345  # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

# Start listening on socket
s.listen(10)
print('Socket now listening')
print(socket.gethostbyname(socket.gethostname()) + ":" + str(PORT))


# Function for handling connections. This will be used to create threads
def clientthread(conn):
    headerPending = True
    expectedData = 6
    bufferedData = ""
    rotation = 0
    # infinite loop so that function do not terminate and thread do not end.
    while True:
        if headerPending:
            bufferedData = ""
            expectedData = 6
        # Receiving from client
        try:
            data = conn.recv(expectedData)
        except:
            print('Error receiving data')
            break
        if not data:
            break
        if headerPending:
            size = (ord(data[0]) << 24) + (ord(data[1]) << 16) + (ord(data[2]) << 8) + ord(data[3])
            rotation = (ord(data[4]) << 8) + ord(data[5])
            # print('size of frame: '+str(size))
            expectedData = size
            headerPending = False
        else:
            # check that we got all the data, otherwise buffer, subtract from expectedData and loop again
            expectedData = expectedData - len(data)
            bufferedData += data

            if expectedData == 0:
                # we got more than we expected
                memoryFile = BytesIO(bufferedData)
                # rotation is only supported in multiples of 90
                rotation = -1 * int(round(float(rotation) / 90) * 90)
                # imgSize = (480,640) if rotation == 0 or rotation == 180 else (640,480)
                img = Image.open(memoryFile).resize((480, 640), Image.BICUBIC).rotate(rotation)

                try:
                    tkpi = ImageTk.PhotoImage(img)
                    imageLabel.config(image=tkpi);
                except:
                    pass
                window.after_idle(updateImageLabel, True);
                headerPending = True

    # came out of loop
    conn.close()


def listenForConnections():
    # now keep talking with the client
    while 1:
        print('Waiting for connection')
        # wait to accept a connection - blocking call
        conn, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))

        # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.

        t = Thread(target=clientthread, args=(conn,))
        t.daemon = True
        t.start()


def updateImageLabel(direct=False):
    imageLabel.config()
    if direct != True:
        window.after(100, updateImageLabel)


def onQuit():
    print('Quitting...')
    imageLabel.destroy()
    window.destroy()


class ADB():

    def __init__(self):
        self.isupdating = False
        self.count =0
        return

    def get_screenshot(self, event):
        if not self.isupdating:
            self.isupdating = True
            print "start"
            self.update()
        else:
            self.isupdating = False
        return


    ##
    ##  adb devices
        # List of devices attached
        # 84B7N16309003145	device
        # 192.168.1.73:5556	device

    # adb - s 84B7N16309003145 shell screencap - p / sdcard / screencap.png

    # adb - s 84B7N16309003145 pull /sdcard/screencap.png  resource/$target

    ##
    def update(self):
        if self.isupdating:
            print "update"
            os.system("adb shell screencap -p /sdcard/screencap.png && adb pull /sdcard/screencap.png resource/")
            self.screenshot = Image.open("resource/screencap.png").resize((270,480),Image.ANTIALIAS)
            self.tkpi = ImageTk.PhotoImage(self.screenshot)
            imageLabel.config(image=self.tkpi)
            self.count += 1
            # imageLabel.config(text="new screen : " + str(self.count))
            window.after(1000, self.update)
        else:
            self.count = 0
            print "stop updating"
        return



if __name__ == "__main__":
    window = tkinter.Tk()
    window.geometry('{}x{}'.format(270, 480))
    window.title('Android Phone')
    window.protocol("WM_DELETE_WINDOW", onQuit)
    adb = ADB()
    imageLabel = tkinter.Label(window, text="Click me to start...");
    imageLabel.pack(side="bottom", fill="both", expand="yes")
    imageLabel.place(x=0, y=0, width=270, height=480)
    imageLabel.bind("<Button>", adb.get_screenshot)

    # t = Thread(target=listenForConnections)
    # t.daemon = True
    # t.start()

    window.after(100, updateImageLabel)
    window.mainloop()

    sys.exit(0)
