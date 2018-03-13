from Tkinter import *
from misc.findrobots import findrobots


class Application:
    
    def __init__(self):
        self.window = Tk()

        # Adding a menu bar
        self.menu_bar = Menu(self.window)

        # Adding the file menu in the menu bar
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)

        # Adding buttons to file menu
        self.file_menu.add_command(label='Exit', command=exit)

        # Inserting the menu in the GUI
        self.window.config(menu=self.menu_bar)

        # Creating the robots list
        self.robots = [x["addr"] for x in self.find_robots()]
        self.robotslist = Listbox(self.window)

        # Creating user and pass boxes
        label1 = Label(self.window, text="User : ")
        label1.grid(row=2, column=2)
        self.user = StringVar()
        user_box = Entry(self.window, textvariable=self.user)
        user_box.grid(row=2, column=3)
        label2 = Label(self.window,text="Pass : ")
        label2.grid(row=3,column=2)
        self.password = StringVar()
        pass_box = Entry(self.window, textvariable=self.password)
        pass_box.grid(row=3, column=3)
        self.window.bind('<Return>', self.hehe)
        self.window.mainloop()

    def hehe(self, event):
        print self.user.get(), self.password.get()

    def find_robots(self):
        return findrobots.Searcher().robots

Application()
