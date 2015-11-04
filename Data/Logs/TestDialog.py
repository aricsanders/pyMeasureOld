#Boa:Dialog:Dialog1

import wx
import wx.html



#-------------------------------------------------------------------------------
# CONSTANTS

#-------------------------------------------------------------------------------

HTML_DOCUMENT_2="""<h1> This is a Test of a new dialog written by me!!!!</h1> 
<br/>"""
def create(parent):
    return Dialog1(parent)

[wxID_DIALOG1, wxID_DIALOG1HTMLWINDOW1, wxID_DIALOG1PANEL1, 
] = [wx.NewId() for _init_ctrls in range(3)]

class Dialog1(wx.Dialog):
    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.htmlWindow1, 1, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DIALOG1, name='', parent=prnt,
              pos=wx.Point(768, 211), size=wx.Size(400, 250),
              style=wx.DEFAULT_DIALOG_STYLE, title='Dialog1')
        self.SetClientSize(wx.Size(392, 216))

        self.panel1 = wx.Panel(id=wxID_DIALOG1PANEL1, name='panel1',
              parent=self, pos=wx.Point(112, 72), size=wx.Size(200, 100),
              style=wx.TAB_TRAVERSAL)

        self.htmlWindow1 = wx.html.HtmlWindow(id=wxID_DIALOG1HTMLWINDOW1,
              name='htmlWindow1', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(392, 216), style=wx.html.HW_SCROLLBAR_AUTO)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.htmlWindow1.SetPage(HTML_DOCUMENT_2)
