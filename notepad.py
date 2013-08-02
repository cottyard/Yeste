import wx

class NotePad(wx.Frame):
    def __init__(self, parent, title, tab = '', content = ''):
        wx.Frame.__init__(self, parent, title = title)
        
        self.panel = wx.Panel(self)
        
        textArea1 = wx.TextCtrl(self.panel)
        textArea1.SetValue(tab)
        textArea2 = wx.TextCtrl(self.panel, style = wx.TE_MULTILINE |
                                                    wx.TE_PROCESS_TAB)
        textArea2.SetValue(content)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(textArea1, flag = wx.EXPAND)
        vbox.Add(textArea2, proportion = 1, flag = wx.EXPAND)
        
        self.panel.SetSizer(vbox)

        def OnExit(event):
            parent.updateNote(self, textArea1.GetValue(),
                              textArea2.GetValue())
            event.Skip()

        self.Bind(wx.EVT_CLOSE, OnExit)

        def OnEscape(event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.Close()
            event.Skip()
        
        self.Bind(wx.EVT_CHAR_HOOK, OnEscape)
        self.Show(True)

        parent.regEdittingNote(self)

        
