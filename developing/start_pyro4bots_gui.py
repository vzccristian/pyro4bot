from tkinter import *
import tkinter.ttk
from developing.findrobots.findrobots import Searcher
import pygubu
from pexpect import pxssh


class Interactor:
    def __init__(self):
        pass

    @staticmethod
    def found_robots_list():
        s = Searcher()
        return s.robots if len(s.robots) > 0 else ['-']


class GUI:

    def __init__(self):
        self.master = Tk()
        self.builder = pygubu.Builder()
        self.builder.add_from_file("config/gui.ui")
        main = self.builder.get_object('main', self.master)
        self.builder.connect_callbacks(self)
        self.on_refresh_button()
        # self.root = Tk()
        # self.menu_bar = Menu(self.root)
        # self.file_menu = Menu(self.menu_bar, tearoff=0)
        # self.file_menu.add_command(label="Exit", command=exit)
        # self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        # self.root.config(menu=self.menu_bar)
        #self.robot_selection = StringVar()
        # self.robots_list = OptionMenu(self.root, self.robot_selection, *self.found_robots_list())
        # self.robots_list.config(width=10)
        # self.robots_list.grid(row=1, column=1, sticky="ew")
        # self.refresh_robots_list()
        # self.refresh_robots_button = Button(self.root, text="Refresh list", command=self.refresh_robots_list)
        # self.refresh_robots_button.grid(row=1, column=2, sticky=E)
        # self.user_label = Label(self.root, text="User: ")
        # self.user_label.grid(row=2, column=1, sticky=E)
        # self.user_input = StringVar()
        # self.user_input_box = Entry(self.root)
        # self.user_input_box.grid(row=2, column=2, sticky=E)
        self.master.mainloop()
        self.ssh = pxssh.pxssh()

    def on_refresh_button(self):
        r_list = ["aaa", "bbb"]
        robot_gui_list = self.builder.get_object("robots_list")
        robot_gui_list['menu'].delete(0, END)
        for i in r_list:
            robot_gui_list.option_add(END, i)
        robot_gui_list['state'] = DISABLED if r_list == ['-'] else NORMAL
        print(r_list)


if __name__ == '__main__':
    GUI()
