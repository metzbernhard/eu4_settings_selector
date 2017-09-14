import sqlite3

#outsourcing the database operations.
class db:
    def __init__(self):
        # create/connnect to database and table
        self.db = sqlite3.connect('settings.db')
        self.db.row_factory = sqlite3.Row
        self.db.execute('''CREATE TABLE IF NOT EXISTS settings
                            (name text, lang text, rx integer, ry integer, 
                            fs integer, bl integer, mods text, dlc text)''')


    def new(self, **kwargs):
        # making a string of values for sqlite statement
        settings = ""
        for key, value in kwargs.items():
            if isinstance(value, str):
                settings += "'" + value + "', "
            if isinstance(value, int):
                settings += str(value) + ", "
            elif isinstance(value, list):
                # print(value)
                settings += "'" + ','.join(value) + "',"
        settings = settings[:-1]
        # there is more elegant ways of doing this ...
        # inserting a new set of settings into our db
        insert = ('insert into settings (name,lang,rx,ry,fs,bl,mods,dlc) values (' + settings + ')')
        # print (insert)
        self.db.execute(insert)
        self.db.commit()

    def delete(self, name):
        # find setting after name and delete!
        self.db.execute('delete from settings where name = ?', (name,))
        self.db.commit()

    def list(self):
        # give me info!
        self.db.execute('select * from settings')
        self.db.commit()

    def get(self, name):
        set = self.db.execute('select * from settings where name = ?', (name,))
        return dict(set.fetchone())

    def close(self):
        self.db.close()


    def __iter__(self):
        rows = self.db.execute('select * from settings')
        for row in rows:
            yield dict(row)

#main will only be executed if main-module -> for test runs

#db module for settings selector -> will not be executed

def main():
    test = db()

    print('Create rows')
    test.new(name = 'name', lang = 'german', rx = 1920, ry = 1080, fs = 0, bl = 1, mods = '', dlc = '')
    test.new(name = 'really', lang = 'english', rx = 1920, ry = 1080, fs = 0, bl = 1, mods = '', dlc = '')
    for row in test:
        print(row)

    print('Retrieve rows')
    print(test.get('name'))

    print('Delete rows')
    test.delete('really')
    for row in test:
        print(row)

if __name__ == "__main__":
    main()
