import wx
import data
import notepad
import copy

class MainFrame(wx.Frame):
    BUTTON_WIDTH = 30
    BUTTON_HEIGHT = 20
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Yeste 1.2.1',
                          style = wx.DEFAULT_FRAME_STYLE)
        # GUI

        # panel
        self.panel = wx.Panel(self)

        # tool bar
        self.newButton = wx.Button(self.panel, label = 'New', \
                                   size = (MainFrame.BUTTON_WIDTH,
                                           MainFrame.BUTTON_HEIGHT))
        self.Bind(wx.EVT_BUTTON, self.OnNew, self.newButton)

        self.delButton = wx.Button(self.panel, label = 'Del', \
                                   size = (MainFrame.BUTTON_WIDTH,
                                           MainFrame.BUTTON_HEIGHT))
        self.Bind(wx.EVT_BUTTON, self.OnDel, self.delButton)
        
        self.levelUpButton = wx.Button(self.panel, label = 'Up', \
                                       size = (MainFrame.BUTTON_WIDTH,
                                               MainFrame.BUTTON_HEIGHT))
        self.Bind(wx.EVT_BUTTON, self.OnLevelUp, self.levelUpButton)

        searchLabel = wx.StaticText(self.panel, label = 'search:',
                                    style = wx.ALIGN_RIGHT)
        
        self.searchBox = wx.TextCtrl(self.panel)
        self.Bind(wx.EVT_TEXT, self.OnSearch, self.searchBox)
        
        hbox = wx.FlexGridSizer(0, 6, 0, 0)
        hbox.AddMany([(self.newButton, 0, wx.EXPAND),
                      (self.delButton, 0, wx.EXPAND),
                      (self.levelUpButton, 0, wx.EXPAND),
                      ((50,1), 0, wx.EXPAND),
                      (searchLabel, 0, wx.EXPAND),
                      (self.searchBox, 0, wx.EXPAND)])
        hbox.AddGrowableCol(5,1)
        # end of tool bar

        # list
        self.listBox = wx.ListBox(self.panel, style = wx.LB_EXTENDED)
        self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.OnOpen)
        self.listBox.Bind(wx.EVT_LISTBOX, self.OnSelect)
        # popup menu
        self.popupMenu = wx.Menu()
        menuID = [wx.ID_CUT, wx.ID_COPY, wx.ID_PASTE]
        for i, text in enumerate("Cut Copy Paste".split()):
            item = self.popupMenu.Append(menuID[i], text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
            if text == 'Paste':
                self.pasteButton = item
        
        self.listBox.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        # end of popup menu
        
        self.pasteBoard = []
        self.pasteButton.Enable(False)
        # end of list

        # preview text area
        self.previewText = wx.TextCtrl(self.panel, style = wx.TE_MULTILINE |
                                       wx.TE_READONLY)

        # directory indicator
        self.dirIndicator = wx.StaticText(self.panel)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, flag = wx.EXPAND)
        vbox.Add(self.listBox, proportion = 2, flag = wx.EXPAND)
        vbox.Add(self.previewText, proportion = 1, flag = wx.EXPAND)
        vbox.Add(self.dirIndicator, flag = wx.EXPAND)
        
        self.panel.SetSizer(vbox)
        
        self.Show()
        
        # end of GUI

        # data management
        self.noteManager = data.NoteManager()
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.showEntries()

        print "initialization finished"

    # API: called by notepad.py
    def updateNote(self, name, content):
        if name == '':
            return
        if name.lower().startswith('dir:'):
            if content.strip() == '':
                content = ''
            self.noteManager.newDir(name[4:].lstrip(), content)
        else:
            self.noteManager.newNote(name, content)
            
        self.showEntries()
    # end of API


    # auxiliary methods
    def showEntries(self, filterString = ''):
        lst = list(self.noteManager.getDirIter()) +\
              list(self.noteManager.getNoteIter())
              
        lst = filter(lambda x: filterString in x, lst)
        self.listBox.Set(lst)

        self.dirIndicator.SetLabel(\
            reduce(lambda p,q: p+'/'+q ,self.noteManager.getPath()))

    def verifyPassword(self, entryName):
        dlg = wx.TextEntryDialog(None, "Enter password: ",
                                 'Access ' + entryName, '')
        if dlg.ShowModal() != wx.ID_OK:
            return False
        pw = dlg.GetValue()
        dlg.Destroy()
        if not self.noteManager.matchPassword(entryName, pw):
            dlg = wx.MessageDialog(None, "Incorrect password.",
                                   style = wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

    def cutEntries(self):
        for eName in self.copyEntries():
            self.noteManager.delEntry(eName)
        self.showEntries()
            
    def copyEntries(self):
        selectedEntries = map(self.listBox.GetString,
                              self.listBox.GetSelections())
        for eName in selectedEntries:
            self.pasteBoard.append(
                copy.deepcopy(
                    self.noteManager.retrieveEntry(eName)))
            
        if len(selectedEntries) > 0:
            self.pasteButton.Enable(True)
            
        return selectedEntries

    def pasteEntries(self):
        for entry in self.pasteBoard:
            self.noteManager.newEntry(entry)
        self.pasteBoard = []
        self.pasteButton.Enable(False)
        self.showEntries()
        
    # end of auxiliary methods

    
    # callback methods
    def OnNew(self, event):
        notepad.NotePad(parent = self, title = 'New Note')

    def OnDel(self, event):
        entryNames = map(self.listBox.GetString,
                        self.listBox.GetSelections())
        if entryNames == []:
            return
        
        # confirm deletion
        cfmMsg = "Delete "
        if len(entryNames) == 1:
            cfmMsg += entryNames[0]
        else:
            cfmMsg += str(len(entryNames)) + ' items'

        cfmMsg += '?'
        dlg = wx.MessageDialog(None, cfmMsg, 'Confirm',
                               wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result != wx.ID_YES:
            return

        # execute deletion
        for e in entryNames:
            # if entry is encrypted, request access
            if self.noteManager.isEncrypted(e):
                if not self.verifyPassword(e):
                    break
            self.noteManager.delEntry(e)
            
        self.showEntries()

    def OnSearch(self, event):
        search = self.searchBox.GetValue()
        self.showEntries(search)

    def OnOpen(self, event):
        mng = self.noteManager
        entryName = event.GetString()
        if mng.isNote(entryName):
            notepad.NotePad(parent = self, title = entryName,
                            tab = entryName,
                            content = mng.getNoteContent(entryName))
            self.noteManager.delEntry(entryName)
        else:
            if mng.isEncrypted(entryName):
                if not self.verifyPassword(entryName):
                    return
            mng.enterDir(entryName)
            
        self.showEntries()

    def OnLevelUp(self, event):
        self.noteManager.exitDir()
        self.showEntries()
        
    def OnSelect(self, event):
        entryName = event.GetString()
        if self.noteManager.isNote(entryName):
            self.previewText.SetValue(self.noteManager.getNoteContent(entryName))
        else:
            if self.noteManager.isEncrypted(entryName):
                value = '<encrypted directory>'
            else:
                value = reduce(lambda p,q: p+'\n- '+q,\
                               self.noteManager.getDirEntries(entryName),\
                               '<directory>')

            self.previewText.SetValue(value)
            
    def OnContextMenu(self, event):
        pos = event.GetPosition()
        pos = self.listBox.ScreenToClient(pos)
        self.listBox.PopupMenu(self.popupMenu, pos)

    def OnPopupItemSelected(self, event):
        id = event.GetId()
        if id == wx.ID_CUT:
            self.cutEntries()
        elif id == wx.ID_COPY:
            self.copyEntries()
        elif id == wx.ID_PASTE:
            self.pasteEntries()
            
    def OnExit(self, event):
        self.noteManager.save()
        event.Skip()
    # end of callback methods

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MainFrame(parent = None, id = -1)
    app.MainLoop()
