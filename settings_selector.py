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

        self.helptext = '''Create new settings:
1) Set the path to settings.txt and (optional) the path to Steam
2) Start the EU4 Launcher and set the settings you want to save
3) Either close the Launcher or start the game 
(otherwise the settings.txt won't be saved)
4) Enter a Name for your settings and click the button to save
        
Start the game using settings:
1) Select the settings you want to use in the dropdown menu
2) Click "Use"
3) Either start EU4 via Steam or the "Play"-Button
        
Delete settings:
1) Select the settings you want to delete in the dropdown menu
2) Click Delete'''

        self.dlc = []
        self.mod = []

    def interface(self):
        self.window.title('EU4 Settings Selector')
        self.style = ttk.Style()

        # HEADER
        self.frame_header = ttk.Frame(self.window)
        self.frame_header.grid(row=1, column=0)
        # self.logo = PhotoImage(file='eu4.gif')

        # ttk.Label(self.frame_header, image=self.logo).grid(column=0, row=0, rowspan=2)
        self.header = ttk.Label(self.frame_header, text='Europa Universalis IV\nSettings Selector', font=('Arial', 20, 'bold'), justify=CENTER).grid(row=0, column=0)

        # help
        self.helpframe = ttk.Frame(self.frame_header, padding=(5,5))
        self.helpframe.grid(row=1, column=0)
        self.help = ttk.Button(self.helpframe, text="How to use this tool", command=lambda: self.helpmessage())
        self.help.pack()

        ttk.Separator(self.window, orient=HORIZONTAL).grid(row=2, column=0, sticky="ew", pady=10)
        #give me your path
        self.frame_path = ttk.LabelFrame(self.window, text='Path', padding=(3,3), height=75, width=300, borderwidth=3)
        self.frame_path.grid(row=3, column=0)
        self.frame_path.grid_propagate(0)
        self.frame_pathentry = ttk.Entry(self.frame_path, width = 47)
        self.frame_pathentry.grid(row=0, column=0, columnspan=2)
        self.frame_pathentry.insert(0, self.path)

        # set path
        # self.frame_pathset = ttk.Button(self.frame_path, text='Set Path', command=lambda: self.set_directory('path.txt'))
        # self.frame_pathset.grid(row=1, column=1, sticky="e")

        # select path
        self.frame_pathbutton = ttk.Button(self.frame_path, text='Select Path containing settings.txt...', command=lambda: self.getdirectory())
        self.frame_pathbutton.grid(row=1, column=0, sticky="w")

        ttk.Separator(self.window, orient=HORIZONTAL).grid(row=4, column=0, sticky="ew", pady=10)

        # insert name
        self.frame_name = ttk.LabelFrame(self.window, text='Name', padding=(3, 3), height=75, width=300, borderwidth=3)
        self.frame_name.grid(row=5, column=0)
        self.frame_name.grid_propagate(0)
        self.frame_name_entry = ttk.Entry(self.frame_name, width = 47)
        self.frame_name_entry.grid(row=0, column=0, columnspan=2)

        # parsing settings.txt
        self.frame_setting = ttk.Button(self.frame_name, text='Scrape and Save Current Settings', command=lambda: self.scrape())
        self.frame_setting.grid(row=1, column=0, sticky="w")

        # using settings.txt
        # self.frame_setting = ttk.Button(self.frame_name, text='Save Scraped Settings', command=lambda: self.save_scrape())
        # self.frame_setting.grid(row=1, column=1, sticky="e")

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

        self.play_setpath = ttk.Button(self.frame_play, text="Set Steam Path...", width=20, command=lambda: self.getplaydirectory())
        self.play_setpath.grid(row=1, column=1, sticky='e')


    def scrape(self):
        set_name = self.frame_name_entry.get()
        # check if name is entered:
        if len(set_name) == 0:
            messagebox.showinfo(title="No Name", message="Please enter name for settings")
            return
        # print (self.database.check(set_name))
        # check if name is in use:
        if self.database.check(set_name):
            messagebox.showinfo(title="Duplicate", message="Name is already used for settings. Either Delete Set to create a new one under this name or choose a different name")
            return
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
        self.database.new(name=set_name, lang=self.lang, rx=self.x, ry=self.y, fs=self.fs, bl=self.bl, mods=self.mod,
                          dlc=self.dlc)
        self.populate_selectionbox()
        messagebox.showinfo(title="Done", message="Saved Current settings.txt under " + set_name)
        os.chdir(workpath)

    def helpmessage(self):
        messagebox.showinfo(title="How to use", message=self.helptext)

    def set_path(self):
        if os.path.exists('path.txt'):
            with open('path.txt', 'r') as f:
                return f.read()
        else:
            with open ('path.txt', 'w') as f:
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
        with open('path.txt', 'w') as f:
            f.write(self.path)

    def getplaydirectory(self):
        self.playpath = filedialog.askdirectory()
        self.playentry.delete(0, END)
        self.playentry.insert(0, self.playpath)
        with open('playpath.txt', 'w') as f:
            f.write(self.playpath)

    def populate_selectionbox(self):
        names = []
        for row in self.database:
            names.append(row['name'])
        self.selectionbox.config(values=names)
        if names:
            self.selectionbox.set(names[-1])

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

    def delete_settings(self):
        self.database.delete(self.selectionbox.get())
        self.populate_selectionbox()

def number_re(text):
	find = re.search('[0-9]+', text)
	if find:
		return find.group()

###############################################################################################

def main():
    window = Tk()
    #build me a GUI
    selector = Selector(window)
    window.mainloop()

if __name__ == "__main__":
    main()
