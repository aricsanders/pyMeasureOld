#Boa:Dialog:Dialog1

import wx
from pyMeasure.Code.FrontEnds.ShellPanel import *
def create(parent):
    return Dialog1(parent)

[wxID_DIALOG1, wxID_DIALOG1PANEL1, 
] = [wx.NewId() for _init_ctrls in range(2)]

class Dialog1(wx.Dialog):
    _custom_classes = {'wx.Panel': ['ShellPanel']}
    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.panel1, 1, border=0, flag=wx.ALL | wx.EXPAND)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DIALOG1, name='', parent=prnt,
              pos=wx.Point(470, 226), size=wx.Size(729, 400),
              style=wx.DEFAULT_DIALOG_STYLE, title='Dialog1')
        self.SetClientSize(wx.Size(721, 366))

        self.panel1 = ShellPanel(id=wxID_DIALOG1PANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(721, 366),
              style=wx.TAB_TRAVERSAL)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = create(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
