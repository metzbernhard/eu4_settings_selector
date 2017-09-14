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
        self.path = "E:\\Dokumente\\Paradox Interactive\\Europa Universalis IV"
        self.database = settings_db.db()
        self.interface()
        self.window.protocol("WM_DELETE_WINDOW", self._close)
        # for closing the db, see self._close function

        self.dlc = []
        self.mod = []

    def interface(self):
        self.window.title('EU4 Settings Selector')
        self.style = ttk.Style()

        #HEADER
        self.frame_header = ttk.Frame(self.window)
        self.frame_header.pack(side = TOP)
        self.logo = PhotoImage(file='eu4.gif')
        ttk.Label(self.frame_header, image = self.logo).grid(column = 0, row = 0)
        self.header = ttk.Label(self.frame_header, text='EU4 Settings\nSelector', font = ('Arial', 22, 'bold'), justify=CENTER).grid(row=0, column=1)

        #main body
        self.frame_body = ttk.Notebook(self.window)
        self.frame_body.config(height = 585, width = 300, padding = (10,10))
        self.frame_body.pack(side = BOTTOM)

        #two pans
        self.frame_select = ttk.Frame(self.frame_body)
        self.frame_create = ttk.Frame(self.frame_body)
        self.frame_body.add(self.frame_select, text='Select')
        self.frame_body.add(self.frame_create, text='Create')

        # selection-pane
        buttons = self.database.list()
        i = 1
        for row in self.database:
            sel = row['name'] + ' (' + str(i) + ')'
            i = i+1
            #print(sel)
            self.frame_button_sel = ttk.Button(self.frame_select, text = sel, command = lambda: self.load(row))
            self.frame_button_sel.pack()
            #print(row['name'])

        #settings name
        self.frame_name = ttk.LabelFrame(self.frame_create, text = 'Name', padding = (3,3), height = 75, width = 300, borderwidth = 3)
        self.frame_name.grid(row = 0, column = 0)
        self.frame_name.grid_propagate(0)
        self.frame_name_entry = ttk.Entry(self.frame_name, width = 46)
        self.frame_name_entry.grid(row = 0, column = 0, columnspan = 2)

        #parsing settings.txt
        self.frame_setting = ttk.Button(self.frame_name, text = 'Read Current Settings', command = lambda: self.scrape())
        self.frame_setting.grid(row = 1, column = 0)

        # using settings.txt
        self.frame_setting = ttk.Button(self.frame_name, text='Save Scraped Settings', command=lambda: self.save_scrape())
        self.frame_setting.grid(row=1, column=1)

        #give me your path
        self.frame_path = ttk.LabelFrame(self.frame_create, text = 'Path', padding = (3,3), height = 75, width = 300, borderwidth = 3)
        self.frame_path.grid(row = 1, column = 0)
        self.frame_path.grid_propagate(0)
        self.frame_pathentry = ttk.Entry(self.frame_path, width = 46)
        self.frame_pathentry.grid(row = 0, column = 0, columnspan = 3)

        # set path
        self.frame_pathbutton = ttk.Button(self.frame_path, text='Set Path')
        self.frame_pathbutton.grid(row=2, column=0)
        self.frame_pathbutton.config(command = lambda: self.getdirectory())

        #reading the .mod files
        self.frame_mods = ttk.Button(self.frame_path, text = 'List Mods', command = lambda: modlist(self.mods, self.path, self.frame_modtree))
        self.frame_mods.grid(row = 2, column=2)

        #set resolution in x&y
        self.frame_resolution = ttk.LabelFrame(self.frame_create, text = 'Resolution', padding = (3, 3), height = 55, width = 300, borderwidth = 3)
        self.frame_resolution.grid(row = 2, column = 0)
        self.frame_resolution.grid_propagate(0)
        self.frame_X = ttk.Entry(self.frame_resolution, width=10).grid(row = 0, column = 1)
        self.frame_Y = ttk.Entry(self.frame_resolution, width=10).grid(row=0, column=3)
        ttk.Label(self.frame_resolution, text='Width', padding = (3,0)).grid(row=0, column = 0)
        ttk.Label(self.frame_resolution, text='Height', padding = (3,0)).grid(row=0, column = 2)

        #set language
        self.language = StringVar()
        self.frame_language = ttk.LabelFrame(self.frame_create, text = 'Language', padding = (3, 3), height = 50, width = 300, borderwidth = 3)
        self.frame_language.grid(row = 3, column = 0)
        self.frame_language.grid_propagate(0)
        self.frame_language_box = ttk.Combobox(self.frame_language, textvariable = self.language)
        self.frame_language_box.config(values = ('English', 'Deutsch', 'Français', 'Español'))
        self.frame_language_box.grid(row = 0, column = 0)

        #settings fullscreen & borderless checkbox
        self.frame_window = ttk.LabelFrame(self.frame_create, text = 'Window', height = 45, width = 300, borderwidth = 3)
        self.frame_window.grid(row = 4, column = 0)
        self.frame_window.grid_propagate(0)
        self.frame_fullscreen = ttk.Checkbutton(self.frame_window, text='Fullscreen').grid(row = 0, column = 0)
        self.frame_borderless = ttk.Checkbutton(self.frame_window, text='Borderless').grid(row = 0, column = 1)
        ttk.Separator(self.frame_create, orient=HORIZONTAL).grid(row=5, column=0, sticky="ew", pady=5)

        #mod treeview
        self.frame_mods = ttk.Frame(self.frame_create)
        self.frame_mods.grid(row = 6, column = 0)
        self.frame_modtree = ttk.Treeview(self.frame_mods, padding = (3,3))
        self.frame_modtree.grid(row = 0, column = 0)
        self.frame_modtree.config(height = 10)
        self.frame_modtree.column('#0',minwidth = 200, width = 260)
        self.frame_modtree.heading('#0', text='Mods')
        # modlist(self.mods, self.path)

        #scrollbar
        self.frame_modscroll = ttk.Scrollbar(self.frame_mods, orient = VERTICAL, command = self.frame_modtree.yview)
        self.frame_modscroll.grid(row = 0, column = 1, sticky = 'ns')
        self.frame_modtree.config(yscrollcommand = self.frame_modscroll.set)

        #submit-button
        ttk.Separator(self.frame_create, orient = HORIZONTAL).grid(row = 7, column = 0, sticky="ew", pady=5)
        self.frame_submit = ttk.Button(self.frame_create, text = 'Submit Settings as Name', command = lambda: self.save_entry())
        self.frame_submit.grid(row = 8, column = 0, sticky="ew")
        self.frame_submit.state(['disabled'])

    def scrape(self):
        os.chdir(self.path)
        print(os.getcwd())
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
        messagebox.showinfo(title = "Done", message = """Scraped Settings, press 'Scraped Settings as Name' Button 
to save the set of settings as new entry with the given Name!""" + str(self.mod))

    def load(self, row):
        print(row)

    def select_language(self, lang):
        print(lang)
        if lang == "Deutsch":
            return 'l_german'
        elif lang == 'English':
            return 'l_english'
        elif lang == 'Français':
            return 'l_french'
        elif lang == 'Español':
            return 'l_spanish'

    def save_scrape(self):
        set_name = self.frame_name_entry.get()
        if len(set_name) == 0:
            messagebox.showinfo(title = "No Name", message = "Please enter name for settings")
        else:
            self.database.new(name = set_name, lang = self.lang, rx = self.x, ry = self.y, fs = self.fs, bl = self.bl, mods = self.mod, dlc = self.dlc)

    def save_entry(self):
        lang = self.select_language(self.language.get())
        print(lang)
        print(self.frame_modtree.selection())
        set_name = self.frame_name_entry.get()
        print(self.frame_pathentry.get())
        test = self.frame_X.get()
        print(test)
        if len(set_name) == 0:
            messagebox.showinfo(title = "No Name", message = "Please enter name for settings")
        #else:
        #    self.database.new(name = set_name, lang = lang, rx = self.entry_X.get(), ry = self.entry_Y.get(), fs = self.fs, bl = self.bl, mods = self.mod, dlc = '')

    def _close(self):
        #close db when program is closed
        #self.database.close()
        self.window.destroy()

    def getdirectory(self):
        self.path = filedialog.askdirectory()
        self.frame_pathentry.delete(0, END)
        self.frame_pathentry.insert(0, self.path)

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