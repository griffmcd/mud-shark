from tkinter import *
from client import *

class GUI(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Mud Shark v0.1")
        self.geometry('640x480')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # set up menu bar
        menu = Menu(self)
        self.config(menu=menu)
        file = Menu(menu)
        file.add_command(label="Connect", command=self.connect_popup)
        file.add_command(label="Exit", command=self.client_exit)
        menu.add_cascade(label="File", menu=file)
        self.logs = {'System':0, 'Alarm':1, 'Hist. Log 1': 2, 'Hist. Log 2' : 3, 'Hist. Log 3' : 4, 'I/O Changes' : 5}
        self.modes = {'Program log', 'Retrieve log'}
        # initialize fields for status bar
        self.connected = False
        self.host = "None"
        self.port = "None"
        self.log_name = "None"
        self.mode = "None"
        # set up status bar
        self.status_string = "Host: " + self.host + " | Port: " + str(self.port) + " | Log: " + self.log_name + " | Mode: " + self.mode + " | Connection Status: " + str(self.connected)
        self.statusHost = Label(self, text=self.status_string, bd=1, relief=SUNKEN, anchor=W)
        self.statusHost.pack(side=BOTTOM, fill=X)

    def update_statusbar(self):
        self.status_string = "Host: " + self.host + " | Port: " + str(self.port) + " | Log: " + self.log_name + " | Mode: " + self.mode + "| Connection Status: " + str(self.connected)
        self.statusHost.config(text=self.status_string)

    def connect_popup(self):
        """Popup for file->connect. Popup asks for host and port, stores them,
        and will attempt to connect to given host and port. (CONNECTION ITSELF
        NOT INTEGRATED YET)"""
        self.top = Toplevel(self)
        self.top.title("Connect to Server")
        # host entry field
        hostLabel = Label(self.top, text="Host: ")
        hostLabel.grid(sticky=E)
        self.hostBox = Entry(self.top)
        self.hostBox.grid(row=0, column=1)
        # port entry field
        portLabel = Label(self.top, text="Port: ")
        portLabel.grid(sticky=E)
        self.portBox = Entry(self.top)
        self.portBox.grid(row=1, column=1)
        # log dropdown box
        self.logChoice = StringVar()
        self.logChoice.set('System')
        self.logDropdown = OptionMenu(self.top, self.logChoice, *self.logs)
        logLabel = Label(self.top, text="Log: ")
        logLabel.grid(sticky=E)
        self.logDropdown.grid(row=2, column=1, sticky=W)
        # mode dropdown box
        self.modeChoice = StringVar()
        self.modeChoice.set('Program Log')
        self.modeDropdown = OptionMenu(self.top, self.modeChoice, *self.modes)
        modeLabel = Label(self.top, text="Mode: ")
        modeLabel.grid(sticky=E)
        self.modeDropdown.grid(row=3, column=1, sticky=W)
        # submit button
        submitButton = Button(self.top, text="Enter", command=self.attempt_connection)
        submitButton.grid(row=2, column=2)
        # close button
        closeButton = Button(self.top, text="Close", command=self.close_connect_pop)
        closeButton.grid(row=3, column=2)



    def close_connect_pop(self):
        self.hostBox.delete(0, 'end')
        self.portBox.delete(0, 'end')
        self.top.withdraw()

    def attempt_connection(self):
        """Saves the host and port to fields, deletes the boxes, closes top
        level window"""
        self.host = self.hostBox.get()
        self.port = self.portBox.get()
        self.log_name = self.logChoice.get()
        self.log_num = self.logs.get(self.logChoice.get())
        # try to connect 
        while True:
            try:
                client = connect(self.host, self.port)
                self.connected = True
                break
            except Exception as e:
                raise Exception("Unable to connect to " + self.host + ":"
                        + str(self.port))
                break
        self.hostBox.delete(0, 'end')
        self.portBox.delete(0, 'end')
        self.top.withdraw()
        self.update_statusbar()
        # testing print statements
        print(self.host)
        print(self.port)
        print(self.logChoice.get())
        print(self.logs.get(self.logChoice.get()))

    def client_exit(self):
        exit()

def main():
    gui = GUI()
    gui.mainloop()
if __name__== '__main__':
    main()

