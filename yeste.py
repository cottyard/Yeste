import wx
import data
import notepad

class MainFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Yeste 1.0',
                          style = wx.DEFAULT_FRAME_STYLE)
        # GUI
        
        # panel
        self.panel = wx.Panel(self)

        # tool bar
        self.newButton = wx.Button(self.panel, label = 'New')
        self.Bind(wx.EVT_BUTTON, self.OnNew, self.newButton)

        self.delButton = wx.Button(self.panel, label = 'Del')
        self.Bind(wx.EVT_BUTTON, self.OnDel, self.delButton)

        searchLabel = wx.StaticText(self.panel, label = 'search:',
                                    style = wx.ALIGN_RIGHT)
        
        self.searchBox = wx.TextCtrl(self.panel)
        self.Bind(wx.EVT_TEXT, self.OnSearch, self.searchBox)
        
        hbox = wx.FlexGridSizer(0, 5, 0, 0)
        hbox.AddMany([(self.newButton, 0, wx.EXPAND),
                      (self.delButton, 0, wx.EXPAND),
                      ((50,1), 0, wx.EXPAND),
                      (searchLabel, 0, wx.EXPAND),
                      (self.searchBox, 0, wx.EXPAND)])
        hbox.AddGrowableCol(4,1)
        # end of tool bar

        # list
        self.listBox = wx.ListBox(self.panel, style = wx.LB_SINGLE)
        self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.OnOpenNote)
        self.listBox.Bind(wx.EVT_LISTBOX, self.OnSelect)
        # end of list

        # preview text area
        self.previewText = wx.TextCtrl(self.panel, style = wx.TE_MULTILINE |
                                       wx.TE_READONLY)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, flag = wx.EXPAND)
        vbox.Add(self.listBox, proportion = 2, flag = wx.EXPAND)
        vbox.Add(self.previewText, proportion = 1, flag = wx.EXPAND)
        
        self.panel.SetSizer(vbox)
        
        self.Show()
        # end of GUI

        # data management
        self.noteManager = data.NoteManager()
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.showNoteList()

        print "initialization finished"
        
    def updateNote(self, tab, content):
        if tab == '':
            return
        # update data
        self.noteManager.newNote(tab, content)
        # update list
        self.showNoteList()
        
    def showNoteList(self):
        self.listBox.Clear()
        self.listBox.Set(list(self.noteManager.getTabIter()))
        
    # callback methods
    def OnNew(self, event):
        notepad.NotePad(parent = self, title = 'New Note')

    def OnDel(self, event):
        tabString = self.listBox.GetStringSelection()
        if tabString != '':
            self.noteManager.delNote(tabString)
            self.showNoteList()

    def OnSearch(self, event):
        search = self.searchBox.GetValue()
        tabs = self.noteManager.getTabIter()
        self.listBox.Clear()
        self.listBox.Set([x for x in tabs if search in x])

    def OnOpenNote(self, event):
        tabString = event.GetString()
        notepad.NotePad(parent = self, title = tabString,
                        tab = tabString,
                        content = self.noteManager.getContent(tabString))
        self.noteManager.delNote(tabString)

    def OnSelect(self, event):
        tabString = event.GetString()
        self.previewText.SetValue(self.noteManager.getContent(tabString))

    def OnExit(self, event):
        self.noteManager.save()
        event.Skip()
        

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = MainFrame(parent = None, id = -1)
    app.MainLoop()
