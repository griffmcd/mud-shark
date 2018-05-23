from tkinter import *
from tkinter import messagebox
from client import *

class MeterValueFrame(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, kwargs)
        # create canvas object and vertical scrollbar
        self.vscrollbar = Scrollbar(self, orient=VERTICAL)
        # self.vscrollbar.grid(sticky=E)
        self.vscrollbar.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(self,
                             bg='#444444', bd=0,
                             height=350,
                             highlightthickness=0,
                             yscrollcommand=self.vscrollbar.set)
        # self.canvas.grid(sticky=W)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        #reset view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = Frame(self.canvas, **kwargs)
        self.canvas.create_window(0,0, window=self.interior, anchor="nw")
        self.bind('<Configure>', self.set_scrollregion)

        # add checkboxes etc
        var1 = IntVar()
        Checkbutton(self, text="test", variable=var1).pack(fill=BOTH, anchor=W, side=TOP)
        # Checkbutton(self, text="test", variable=var1).grid(row=0, sticky=W)

    def set_scrollregion(self, event=None):
        """Set the scroll region of the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))


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
        file.add_command(label="Disconnect", command=self.disconnect)
        file.add_command(label="Exit", command=self.client_exit)
        menu.add_cascade(label="File", menu=file)
        self.logs = {'System'     : 0, 
                     'Alarm'      : 1, 
                     'Hist. Log 1': 2, 
                     'Hist. Log 2': 3, 
                     'Hist. Log 3': 4, 
                     'I/O Changes': 5}

        self.modes = {'Program log' :0, 
                      'Retrieve log':1}
        # initialize default fields 
        self.connected = False
        self.host = "None"
        self.port = "None"
        self.log_name = "None"
        self.mode = "Retrieve log"
        self.client = None
        # set up status bar
        self.status_string = "Host: " + self.host + " | Port: " + str(self.port) + " | Log: " + self.log_name + " | Mode: " + self.mode + " | Connection Status: " + str(self.connected)
        self.statusHost = Label(self, text=self.status_string, bd=1, relief=SUNKEN, anchor=W)
        self.statusHost.pack(side=BOTTOM, fill=X)
        # TEST FOR PROGRAMMING LOG INTERFACE, REFACTOR INTO ITS OWN THING LATER
        checkbox_pane = MeterValueFrame(self, bg='#444444')
        checkbox_pane.pack(fill=Y, side=RIGHT)

    def attempt_connection(self):
        """Saves the host and port to fields, deletes the boxes, closes top
        level window"""
        self.host = self.hostBox.get()
        self.port = self.portBox.get()
        self.log_name = self.logChoice.get()
        self.log_num = self.logs.get(self.logChoice.get())
        self.mode = self.modeChoice.get()
        if not self.log_mode_programmable():
            self.incompatible_mode_err()
            return
        # try to connect 
        while True:
            try:
                client = connect(self.host, self.port)
                self.connected = True
                break
            except Exception as e:
                self.popup_connection_err(self.host, self.port)
                return
        self.hostBox.delete(0, 'end')
        self.portBox.delete(0, 'end')
        self.client = client
        self.top.withdraw()
        self.update_statusbar()

    def disconnect(self):
        self.reset_connect_fields()
        if self.client != None:
            self.client.close()
        self.connected = False
        self.update_statusbar()

    def connect_popup(self):
        """Popup for file->connect. Popup asks for host and port, stores them,
        and will attempt to connect to given host and port. On fail, throws an
        error messagebox."""
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
        self.modeChoice.set('Program log')
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

### Helper Functions for GUI ### 
    def client_exit(self):
        exit()

    def close_connect_pop(self):
        self.hostBox.delete(0, 'end')
        self.portBox.delete(0, 'end')
        self.top.withdraw()

    def update_statusbar(self):
        self.status_string = "Host: " + self.host + " | Port: " + str(self.port) + " | Log: " + self.log_name + " | Mode: " + self.mode + " | Connection Status: " + str(self.connected)
        self.statusHost.config(text=self.status_string)

    def reset_connect_fields(self):
        self.host = "None"
        self.port = "None"
        self.log_name = "None"
        self.mode = "None"

    def log_mode_programmable(self):
        if self.mode == 'Retrieve log':
            return True
        elif self.mode == 'Program log':
            if self.log_num == 2 or self.log_num == 3 or self.log_num == 4:
                return True
            else:
                return False

### ERROR FUNCTIONS ###
    def incompatible_mode_err(self):
        messagebox.showinfo("Incompatible Mode", "Can only program historical"
                + " logs 1, 2, and 3!")
        # self.reset_connect_fields()

    def popup_connection_err(self, h, p):
        messagebox.showinfo("Connection Error", "Could not connect to "
                + h + " on port " +  str(p))
        self.reset_connect_fields()

### END ERROR FUNCTIONS ###
def main():
    gui = GUI()
    gui.mainloop()
if __name__== '__main__':
    main()

