import pickle
import os

# a note has a tab(string) and a content(string)

class NoteManager:
    def __init__(self):
        self.noteList = dict()
        self.load()

    def getTabIter(self):
        return self.noteList
        
    def getContent(self, tab):
        return self.noteList[tab]

    def delNote(self, tab):
        del self.noteList[tab]
        
    def newNote(self, tab, content):
        self.noteList[tab] = content
        
    def load(self):
        try:
            length = os.path.getsize(os.getcwd()+"\\note.dat")
        except WindowsError:
            #dlg = MessageDialog(self, "Cannot open data file!")
            #dlg.ShowModal()
            #dlg.Destroy()
            f = open("note.dat",'wb')
            f.close()
            #import sys
            #sys.exit("data file error")
            
        if length != 0:
            with open("note.dat",'rb') as f:
                self.noteList = pickle.load(f)        
    def save(self):
        print self.noteList
        with open("note.dat",'wb') as f:
            pickle.dump(self.noteList, f)
