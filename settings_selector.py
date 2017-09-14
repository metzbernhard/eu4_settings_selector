import shutil
import os
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import settings_db
import linecache
import re


class Selector:
    def __init__(self, window):
        #main app
        self.window = window

        #empty list for mods, read new, every start for newly added mods
        self.mods = []

        #path out of path-entry
        self.path = self.set_path()
        self.playpath = self.set_playpath()
        self.database = settings_db.db()
        self.interface()
        self.window.protocol("WM_DELETE_WINDOW", self._close)
        # for closing the db, see self._close function

        self.dlc = []
        self.mod = []

    def interface(self):
        self.window.title('EU4 Settings Selector')
        self.style = ttk.Style()

        # HEADER
        self.frame_header = ttk.Frame(self.window)
        self.frame_header.grid(row=1, column=0)
        self.logo = PhotoImage(file='eu4.gif')

        ttk.Label(self.frame_header, image=self.logo).grid(column=0, row=0)
        self.header = ttk.Label(self.frame_header, text='EU4 Settings\nSelector', font=('Arial', 22, 'bold'), justify=CENTER).grid(row=0, column=1)

        ttk.Separator(self.window, orient=HORIZONTAL).grid(row=2, column=0, sticky="ew", pady=10)
        #give me your path
        self.frame_path = ttk.LabelFrame(self.window, text='Path', padding=(3,3), height=75, width=300, borderwidth=3)
        self.frame_path.grid(row=3, column=0)
        self.frame_path.grid_propagate(0)
        self.frame_pathentry = ttk.Entry(self.frame_path, width = 47)
        self.frame_pathentry.grid(row=0, column=0, columnspan=2)
        self.frame_pathentry.insert(0, self.path)

        # set path
        self.frame_pathset = ttk.Button(self.frame_path, text='Set Path', command=lambda: self.set_directory('path.txt'))
        self.frame_pathset.grid(row=1, column=1, sticky="e")

        # select path
        self.frame_pathbutton = ttk.Button(self.frame_path, text='Select Path...', command=lambda: self.getdirectory())
        self.frame_pathbutton.grid(row=1, column=0, sticky="w")

        ttk.Separator(self.window, orient=HORIZONTAL).grid(row=4, column=0, sticky="ew", pady=10)

        # insert name
        self.frame_name = ttk.LabelFrame(self.window, text='Name', padding=(3, 3), height=75, width=300, borderwidth=3)
        self.frame_name.grid(row=5, column=0)
        self.frame_name.grid_propagate(0)
        self.frame_name_entry = ttk.Entry(self.frame_name, width = 47)
        self.frame_name_entry.grid(row=0, column=0, columnspan=2)

        # parsing settings.txt
        self.frame_setting = ttk.Button(self.frame_name, text='Read Current Settings', command=lambda: self.scrape())
        self.frame_setting.grid(row=1, column=0, sticky="w")

        # using settings.txt
        self.frame_setting = ttk.Button(self.frame_name, text='Save Scraped Settings', command=lambda: self.save_scrape())
        self.frame_setting.grid(row=1, column=1, sticky="e")

        ttk.Separator(self.window, orient=HORIZONTAL).grid(row=6, column=0, sticky="ew", pady=10)

        # selector
        self.frame_selector = ttk.LabelFrame(self.window, text='Selector', padding=(3, 3), borderwidth=3, height=55, width=300)
        self.frame_selector.grid(row=7, column=0)
        self.frame_selector.grid_propagate(0)

        selection = StringVar()
        self.selectionbox = ttk.Combobox(self.frame_selector, textvariable=selection)
        self.selectionbox.grid(row=0, column=0, sticky="e")
        self.populate_selectionbox()

        self.use_button = ttk.Button(self.frame_selector, text="Use", width=10, command=lambda: self.write_settings())
        self.use_button.grid(row=0, column=1, sticky="e")

        self.delete_button = ttk.Button(self.frame_selector, text="Delete", width=10, command=lambda: self.delete_settings())
        self.delete_button.grid(row=0, column=2, sticky="e")

        ttk.Separator(self.window, orient=HORIZONTAL).grid(row=8, column=0, sticky="ew", pady=10)

        #play-section
        self.frame_play = ttk.LabelFrame(self.window, text='Play', padding=(3,3), height=80, width=300)
        self.frame_play.grid(row=9, column=0)
        self.frame_play.grid_propagate(0)

        self.playentry = ttk.Entry(self.frame_play, width=47)
        self.playentry.grid(row=0, column=0, columnspan=2)
        self.playentry.insert(0, self.playpath)

        self.play_button = ttk.Button(self.frame_play, text="Play", width=20, command=lambda: self.start())
        self.play_button.grid(row=1, column=0, sticky='w')

        self.play_setpath = ttk.Button(self.frame_play, text="Set Steam Path", width=20, command=lambda: self.getplaydirectory())
        self.play_setpath.grid(row=1, column=1, sticky='e')


    def scrape(self):
        workpath = os.getcwd()
        os.chdir(self.path)
        # print(os.getcwd())
        # error message if path is not correct, since this will already throw an exception, no further
        # handling down for the open command.
        try:
            self.x = int(number_re(linecache.getline('settings.txt', 5)))
            self.y = int(number_re(linecache.getline('settings.txt', 6)))
        except:
            messagebox.showerror('Error parsing settings.txt, did you set the path correctly?')
        self.dlc = []
        self.mod = []
        file = open('settings.txt', 'r')
        for line in file:
            # print(line)
            if 'language' in line:
                self.lang = line[12:-2]
            elif 'fullScreen' in line:
                if ('no' in line[12:]):
                    self.fs = 0
                elif ('yes' in line[12:]):
                    self.fs = 1
            elif 'borderless' in line:
                if ('no' in line[12:]):
                    self.bl = 0
                elif ('yes' in line[12:]):
                    self.bl = 1
            elif '.dlc' in line:
                self.dlc.append(line[6:-2])
            elif '.mod' in line:
                self.mod.append(line[6:-2])
        messagebox.showinfo(title="Done", message="""Scraped Settings, press 'Save Scraped Settings' Button 
to save the set of settings as new entry with the given Name!""")
        os.chdir(workpath)

    def save_scrape(self):
        set_name = self.frame_name_entry.get()
        if len(set_name) == 0:
            messagebox.showinfo(title="No Name", message="Please enter name for settings")
        else:
            self.database.new(name=set_name, lang=self.lang, rx=self.x, ry=self.y, fs=self.fs, bl=self.bl, mods=self.mod, dlc=self.dlc)
        self.populate_selectionbox()

    def set_path(self):
        if os.path.exists('path.txt'):
            with open('path.txt', 'r') as f:
                return f.read()
        else:
            with open ('path.txt', 'w') as f:
                print('why')
                f.write('C:\\Users\\YOURUSERNAME\\Documents\\Paradox Interactive\\Europa Universalis IV')
                return 'C:\\Users\\YOURUSERNAME\\Documents\\Paradox Interactive\\Europa Universalis IV'

    def set_playpath(self):
        if os.path.exists('playpath.txt'):
            with open('playpath.txt', 'r') as f:
                return f.read()
        else:
            with open ('playpath.txt', 'w') as f:
                # print('why')
                f.write('C:\\Program Files\\Steam\\steamapps\\common\\Europa Universalis IV')
                return 'C:\\Program Files\\Steam\\steamapps\\common\\Europa Universalis IV'

    def start(self):
        workpath=os.getcwd()
        os.chdir(self.playpath)
        os.system(r'eu4.exe')
        os.chdir(workpath)

    def _close(self):
        # close db when program is closed
        self.database.close()
        self.window.destroy()

    def getdirectory(self):
        self.path = filedialog.askdirectory()
        self.frame_pathentry.delete(0, END)
        self.frame_pathentry.insert(0, self.path)

    def getplaydirectory(self):
        self.playpath = filedialog.askdirectory()
        self.playentry.delete(0, END)
        self.playentry.insert(0, self.playpath)
        self.set_directory('playpath.txt')

    def populate_selectionbox(self):
        names = []
        for row in self.database:
            names.append(row['name'])
        self.selectionbox.config(values=names)

    def write_settings(self):
        data = self.database.get(self.selectionbox.get())
        workpath = os.getcwd()
        os.chdir(self.path)
        # print(data)
        with open('settings.txt', 'r') as f:
            file = f.read()
        text = file.splitlines()
        text[1] = 'language="l_' + data['lang'] + '"'
        # print(text)
        text[4] = '\t\tx=' + str(data['rx'])
        # print(text)
        text[5] = '\t\ty=' + str(data['ry'])
        # print(text)
        fs = self.yes_no(data['fs'])
        text[(self.select_contain(text, 'fullScreen'))] = '\tfullScreen='+fs
        # print(text)
        bl = self.yes_no(data['bl'])
        text[(self.select_contain(text, 'borderless'))] = '\tborderless=' + bl
        text = [x for x in text if '.dlc' not in x]
        text = [x for x in text if '.mod' not in x]
        dlclist = data['dlc'].split(',')
        # print(dlclist)
        modlist = data['mods'].split(',')
        if dlclist != ['']:
        # evaluates to False for no dlcs
            for dlc in dlclist:
                text.insert(self.select_contain(text, 'last_dlcs')+1, '\t"dlc/'+dlc + '"')
        if modlist != ['']:
        # evaluates to False for empty list
            for mod in modlist:
                text.insert(self.select_contain(text, 'last_mods')+1, '\t"mod/' + mod + '"')
        # print(text)
        text2 = [x + '\n' for x in text]
        # print(text2)
        # print(text2)
        text2 = ''.join(text2)
        with open('settings.txt', 'w') as f:
            f.write(text2)
            f.close()
        os.chdir(workpath)

    def select_contain(self, list, string):
        for item in list:
            if string in item:
                # print(item)
                return list.index(item)

    def yes_no(self,int):
        if int==0:
            return 'no'
        elif int==1:
            return 'yes'

    def set_directory(self, file):
        self.path = self.frame_pathentry.get()
        with open(file, 'w') as f:
            f.write(self.path)
        # print(self.path)

    def set_directory(self, file):
        self.playpath = self.playentry.get()
        with open(file, 'w') as f:
            f.write(self.playpath)
        # print(self.path)

    def delete_settings(self):
        self.database.delete(self.selectionbox.get())
        self.populate_selectionbox()

def number_re(text):
	find = re.search('[0-9]+', text)
	if find:
		return find.group()

def modlist(mods, path, tree):
    #get a list of modfiles
    for file in os.listdir(path + '\\mod'):
        if file.endswith(('.mod')):
            with open(path + '\\mod\\' + file) as f:
                name = f.readline()
                name = name[6:-2]
                mods.append(name)
    #populate the tkinter-modtree
    i=1
    for mod in mods:
        #List the mods in teeview
        tree.insert('', i, 'mod'+str(i), text=mod)
        i=i+1

###############################################################################################

def main():
    window = Tk()
    #build me a GUI
    selector = Selector(window)
    window.mainloop()

if __name__ == "__main__":
    main()