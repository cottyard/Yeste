import pickle
import os

def printTree(node):
    '''function for testing'''
    print node.name
    if node.type == Entry.TYPE_DIR:
        for x in node.children.values():
            printTree(x)

class NoteManager:
    def __init__(self):
        self.rootDir = Dir('root')
        self.load()
        self.path = [self.rootDir]
        self.pwd = self.rootDir

    # Query Methods
    def getPath(self):
        return map(lambda x: x.name, self.path)
    
    def getNoteIter(self):
        return self.pwd.childrenIter(\
               lambda x: self.pwd.getChild(x).type == Entry.TYPE_NOTE)
    
    def getDirIter(self):
        return self.pwd.childrenIter(\
               lambda x: self.pwd.getChild(x).type == Entry.TYPE_DIR)

    def getNoteContent(self, name):
        return self.pwd.getChild(name).getContent()
        
    def getDirEntries(self, name):
        return self.pwd.getChild(name).childrenIter()
        
    def isNote(self, name):
        return self.pwd.getChild(name).type == Entry.TYPE_NOTE

    def isEncrypted(self, name):
        if self.pwd.getChild(name).type == Entry.TYPE_NOTE:
            return False
        return self.pwd.getChild(name).getPassword() != ''

    def matchPassword(self, name, password):
        return self.pwd.getChild(name).getPassword() == password

    def retrieveEntry(self, name):
        return self.pwd.getChild(name)
    
    # Setting Methods
    def enterDir(self, name):
        dir = self.pwd.getChild(name)
        if dir.type == Entry.TYPE_DIR:
            self.path.append(dir)
            self.pwd = dir
        
    def exitDir(self):
        if len(self.path) > 1:
            self.path.pop()
            self.pwd = self.path[-1]
            
    def delEntry(self, name):
        self.pwd.delChild(name)

    def newEntry(self, entry):
        self.pwd.addChild(entry.name, entry)
        
    def newNote(self, name, content):
        self.pwd.addChild(name, Note(name, content))

    def newDir(self, name, password = ''):
        self.pwd.addChild(name, Dir(name, password))

    # File Methods
    def load(self):
        try:
            p = os.getcwd() + "\\note.dat"
            print 'working path: ' + p
            length = os.path.getsize(p)
        except WindowsError:
            #dlg = MessageDialog(self, "Cannot open data file!")
            #dlg.ShowModal()
            #dlg.Destroy()
            f = open("note.dat",'wb')
            f.close()
            length = 0
            #import sys
            #sys.exit("data file error")

        if length != 0:
            with open("note.dat",'rb') as f:
                self.rootDir = pickle.load(f)

    def save(self):
        with open("note.dat",'wb') as f:
            pickle.dump(self.rootDir, f)
            
# Data Classes

class Entry(object):
    TYPE_NOTE = 0
    TYPE_DIR = 1
    def __init__(self, type, name):
        self.type = type
        self.name = name
        
class Note(Entry):
    def __init__(self, name, content = ''):
        super(Note, self).__init__(Entry.TYPE_NOTE, name)
        self.content = content

    def getContent(self):
        return self.content

class Dir(Entry):
    def __init__(self, name, password = ''):
        super(Dir, self).__init__(Entry.TYPE_DIR, name)
        self.children = dict()
        self.password = password

    def addChild(self, name, child):
        self.children[name] = child

    def delChild(self, name):
        del self.children[name]

    def getChild(self, name):
        return self.children[name]

    def getPassword(self):
        return self.password
        
    def childrenIter(self, filt = None):
        return filter(filt, self.children)
