import wx
import data
import notepad
import copy
import types
import webbrowser

class MainFrame(wx.Frame):
    BUTTON_WIDTH = 30
    BUTTON_HEIGHT = 20
    def __init__(self, parent, id):

        wx.Frame.__init__(self, parent, id, 'Yeste 1.2.8',
                          style = wx.DEFAULT_FRAME_STYLE)
        # GUI

        # panel
        self.panel = wx.Panel(self)
        self.edittingNotes = set() # store opened notepad frames

        # tool bar
        self.newButton = wx.Button(self.panel, label = 'New',
                                   size = (MainFrame.BUTTON_WIDTH,
                                           MainFrame.BUTTON_HEIGHT))
        self.Bind(wx.EVT_BUTTON, self.OnNew, self.newButton)

        self.delButton = wx.Button(self.panel, label = 'Del',
                                   size = (MainFrame.BUTTON_WIDTH,
                                           MainFrame.BUTTON_HEIGHT))
        self.Bind(wx.EVT_BUTTON, self.OnDel, self.delButton)
        
        self.levelUpButton = wx.Button(self.panel, label = 'Up',
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
        
        # splitter window
        splitter = wx.SplitterWindow(self.panel, style = wx.SP_3DSASH)
        
        # list
        self.listBox = wx.ListBox(splitter, style = wx.LB_EXTENDED)
        self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.OnOpen)
        self.listBox.Bind(wx.EVT_LISTBOX, self.OnSelect)

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyBoard)

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
        self.previewText = wx.TextCtrl(splitter, style = wx.TE_MULTILINE |
                                       wx.TE_READONLY | wx.TE_AUTO_URL)
        self.previewText.Bind(wx.EVT_TEXT_URL, self.OnURL)
        def OnGetFocus(e):
            self.previewText.Navigate(flags = wx.NavigationKeyEvent.IsBackward)
        self.previewText.Bind(wx.EVT_SET_FOCUS, OnGetFocus)
        # end of preview text area

        splitter.SplitHorizontally(self.listBox, self.previewText)
        splitter.SetSashGravity(0.5)
        # end of splitter window
        
        # directory indicator
        self.dirIndicator = wx.StaticText(self.panel)


        # vertical sizer
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, flag = wx.EXPAND)
        vbox.Add(splitter, proportion = 1, flag = wx.EXPAND)
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
    def updateNote(self, noteFrame, tab, content):
        self.edittingNotes.remove(noteFrame)
        if tab == '':
            return
        if tab.lower().endswith(':dir'):
            if content.strip() == '':
                content = ''
            tab = tab[:-4].rstrip()
            self.noteManager.newDir(tab, content)
        else:
            self.noteManager.newNote(tab, content)

        self.showEntries()

        class TempClass:
            pass
        event = TempClass()
        def GetString(self):
            return tab
        event.GetString = types.MethodType(GetString, event)
        self.OnSelect(event)

    def regEdittingNote(self, noteFrame):
        self.edittingNotes.add(noteFrame)
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

    def selectedEntries(self):
        return map(self.listBox.GetString,
                   self.listBox.GetSelections())

    def cutEntries(self):
        def bFunc(eName):
            if self.noteManager.isEncrypted(eName):
                return self.verifyPassword(eName)
            return True
        
        def aFunc(eName):
            self.noteManager.delEntry(eName)

        self.entriesToPasteBoard(bFunc, aFunc)
        self.showEntries()

    def copyEntries(self):
        def bFunc(eName):
            if self.noteManager.isEncrypted(eName):
                return self.verifyPassword(eName)
            return True
        self.entriesToPasteBoard(bFunc, lambda n: True)

    def entriesToPasteBoard(self, beforeFunc, afterFunc):
        items = 0
        for eName in self.selectedEntries():
            if beforeFunc(eName):
                items += 1
                self.pasteBoard.append(
                    copy.deepcopy(
                        self.noteManager.retrieveEntry(eName)))
                afterFunc(eName)
            
        if items > 0:
            self.pasteButton.Enable(True)

    def pasteEntries(self):
        for entry in self.pasteBoard:
            self.noteManager.newEntry(entry)
        self.pasteBoard = []
        self.pasteButton.Enable(False)
        self.showEntries()

    def openNote(self, name):        
        notepad.NotePad(parent = self, title = name, tab = name,
                        content = self.noteManager.getNoteContent(name))
        self.noteManager.delEntry(name)

    def openDir(self, name):
        if self.noteManager.isEncrypted(name):
            if not self.verifyPassword(name):
                return
        self.noteManager.enterDir(name)
        
    # end of auxiliary methods

    
    # callback methods
    def OnNew(self, event = None):
        notepad.NotePad(parent = self, title = 'New Note')

    def OnDel(self, event = None):
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

    def OnSearch(self, event = None):
        search = self.searchBox.GetValue()
        self.showEntries(search)

    def OnOpen(self, event):
        entryName = event.GetString()
        if self.noteManager.isNote(entryName):
            self.openNote(entryName)
        else:
            self.openDir(entryName)
            
        self.showEntries()
        
    def OnKeyBoard(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            dirs, dirName = 0, ''
            # open all notes selected
            for eName in self.selectedEntries():
                if self.noteManager.isNote(eName):
                    self.openNote(eName)
                else:
                    dirs += 1
                    dirName = eName
            # open a directory only when 1 dir is selected
            if dirs == 1:
                self.openDir(dirName)

            self.showEntries()
            
        elif event.GetKeyCode() == wx.WXK_DELETE:
            self.OnDel()
            
        event.Skip()

            
    def OnLevelUp(self, event = None):
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

    def OnURL(self, event):
        webbrowser.open(self.previewText.GetRange(
            event.GetURLStart(), event.GetURLEnd()))

    def OnExit(self, event = None):
        # store unsaved notes
        for pad in self.edittingNotes.copy():
            pad.Close()
        self.noteManager.save()
        event.Skip()
    # end of callback methods

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MainFrame(parent = None, id = -1)
    app.MainLoop()
