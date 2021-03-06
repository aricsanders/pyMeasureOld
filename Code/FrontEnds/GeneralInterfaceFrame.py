#-----------------------------------------------------------------------------
# Name:        GeneralInterfaceFrame.py
# Purpose:     An advanced frame design that includes control and interface areas
# and all of the standard menu,tool and status bars.
#
# Author:      Aric Sanders
#
# Created:     2010/04/20
# RCS-ID:      $Id: GeneralInterfaceFrame.py $
#-----------------------------------------------------------------------------
#Boa:Frame:GeneralInterfaceFrame
""" Advanced wx.Frame with standard containers for interface and control this
is meant as a template for GUI design"""
import sys
import os
import wx
from types import *

try:
    from pyMeasure.Code.FrontEnds.IEPanel import *
    from pyMeasure.Code.FrontEnds.ShellPanel import *
except:
    print """Cannot load Shell Panel or IEPanel add The folder above pyMeaure to sys.path
            Also check that the Boa Constructor Source is on sys.path --C:\Python25\Lib\site-packages"""
    raise
#-------------------------------------------------------------------------------
#Functions

def get_top_parent(window):
    """Returns the topmost parent window"""
    try:
        parent=window.Parent
        print parent
        if parent in [None,''] or not type(parent) is InstanceType:
            raise
        get_top_parent(parent)
    except:
        return window
#-------------------------------------------------------------------------------
# Boa Code

def create(parent):
    return GeneralInterfaceFrame(parent)

[wxID_GENERALINTERFACEFRAME, wxID_GENERALINTERFACEFRAMEDISPLAY, 
 wxID_GENERALINTERFACEFRAMEINTERFACESTATUSBAR, 
 wxID_GENERALINTERFACEFRAMEINTERFACETOOLBAR, 
 wxID_GENERALINTERFACEFRAMELEFTINTERFACEPANEL, 
 wxID_GENERALINTERFACEFRAMELOWERCONTROLPANEL, 
 wxID_GENERALINTERFACEFRAMELOWERINTERFACE, 
 wxID_GENERALINTERFACEFRAMELOWERINTERFACEPANEL, 
 wxID_GENERALINTERFACEFRAMEMAINPANEL, 
 wxID_GENERALINTERFACEFRAMERIGHTCONTROLPANEL, wxID_GENERALINTERFACEFRAMESHELL, 
 wxID_GENERALINTERFACEFRAMEUPPERINTERFACE, 
 wxID_GENERALINTERFACEFRAMEUPPERINTERFACEPANEL, 
] = [wx.NewId() for _init_ctrls in range(13)]

[wxID_GENERALINTERFACEFRAMEFILEMENUOPEN] = [wx.NewId() for _init_coll_FileMenu_Items in range(1)]

class GeneralInterfaceFrame(wx.Frame):
    _custom_classes = {'wx.Panel': ['ShellPanel','IEPanel']}
    def _init_coll_boxSizer5_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.LowerInterface, 1, border=2,
              flag=wx.ALL | wx.EXPAND)

    def _init_coll_boxSizer3_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.UpperInterfacePanel, 8, border=2,
              flag=wx.ALL | wx.EXPAND)
        parent.AddWindow(self.LowerInterfacePanel, 2, border=2,
              flag=wx.ALL | wx.EXPAND)
        parent.AddWindow(self.LowerControlPanel, 0, border=2,
              flag=wx.ALL | wx.EXPAND)

    def _init_coll_boxSizer4_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.UpperInterface, 1, border=2,
              flag=wx.EXPAND | wx.ALL)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.MainPanel, 1, border=1, flag=wx.ALL | wx.EXPAND)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.LeftInterfacePanel, 1, border=2,
              flag=wx.EXPAND | wx.ALL)
        parent.AddWindow(self.RightControlPanel, 0, border=2,
              flag=wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND)

    def _init_coll_FileMenu_Items(self, parent):
        # generated method, don't edit

        parent.Append(help=u'Open a file',
              id=wxID_GENERALINTERFACEFRAMEFILEMENUOPEN, kind=wx.ITEM_NORMAL,
              text=u'Open')
        self.Bind(wx.EVT_MENU, self.OnFileMenuOpenMenu,
              id=wxID_GENERALINTERFACEFRAMEFILEMENUOPEN)

    def _init_coll_InterfaceMenuBar_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.FileMenu, title=u'File')
        parent.Append(menu=self.HelpMenu, title=u'Help')
        parent.Append(menu=self.ToolMenu, title=u'Tools')

    def _init_coll_UpperInterface_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.Display, select=True,
              text=u'Display')

    def _init_coll_LowerInterface_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.Shell, select=True, text=u'Shell')

    def _init_coll_InterfaceStatusBar_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(number=0, text=u'Status')

        parent.SetStatusWidths([-1])

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer3 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer4 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer5 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)
        self._init_coll_boxSizer3_Items(self.boxSizer3)
        self._init_coll_boxSizer4_Items(self.boxSizer4)
        self._init_coll_boxSizer5_Items(self.boxSizer5)

        self.SetSizer(self.boxSizer1)
        self.LowerInterfacePanel.SetSizer(self.boxSizer5)
        self.LeftInterfacePanel.SetSizer(self.boxSizer3)
        self.MainPanel.SetSizer(self.boxSizer2)
        self.UpperInterfacePanel.SetSizer(self.boxSizer4)

    def _init_utils(self):
        # generated method, don't edit
        self.FileMenu = wx.Menu(title='')

        self.HelpMenu = wx.Menu(title='')

        self.InterfaceMenuBar = wx.MenuBar()

        self.ToolMenu = wx.Menu(title=u'Tools')

        self._init_coll_FileMenu_Items(self.FileMenu)
        self._init_coll_InterfaceMenuBar_Menus(self.InterfaceMenuBar)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_GENERALINTERFACEFRAME,
              name=u'GeneralInterfaceFrame', parent=prnt, pos=wx.Point(504, 67),
              size=wx.Size(847, 721), style=wx.DEFAULT_FRAME_STYLE,
              title=u'General Interface')
        self._init_utils()
        self.SetClientSize(wx.Size(839, 687))
        self.SetMenuBar(self.InterfaceMenuBar)

        self.InterfaceStatusBar = wx.StatusBar(id=wxID_GENERALINTERFACEFRAMEINTERFACESTATUSBAR,
              name=u'InterfaceStatusBar', parent=self, style=0)
        self.InterfaceStatusBar.SetHelpText(u'Status')
        self.InterfaceStatusBar.SetLabel(u'')
        self._init_coll_InterfaceStatusBar_Fields(self.InterfaceStatusBar)
        self.SetStatusBar(self.InterfaceStatusBar)

        self.InterfaceToolBar = wx.ToolBar(id=wxID_GENERALINTERFACEFRAMEINTERFACETOOLBAR,
              name=u'InterfaceToolBar', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(839, 28), style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        self.SetToolBar(self.InterfaceToolBar)

        self.MainPanel = wx.Panel(id=wxID_GENERALINTERFACEFRAMEMAINPANEL,
              name=u'MainPanel', parent=self, pos=wx.Point(1, 1),
              size=wx.Size(837, 685), style=wx.TAB_TRAVERSAL)

        self.LeftInterfacePanel = wx.Panel(id=wxID_GENERALINTERFACEFRAMELEFTINTERFACEPANEL,
              name=u'LeftInterfacePanel', parent=self.MainPanel, pos=wx.Point(2,
              2), size=wx.Size(688, 681), style=wx.TAB_TRAVERSAL)

        self.RightControlPanel = wx.Panel(id=wxID_GENERALINTERFACEFRAMERIGHTCONTROLPANEL,
              name=u'RightControlPanel', parent=self.MainPanel,
              pos=wx.Point(694, 2), size=wx.Size(141, 681),
              style=wx.TAB_TRAVERSAL)
        self.RightControlPanel.SetBackgroundColour(wx.Colour(255, 128, 128))

        self.LowerControlPanel = wx.Panel(id=wxID_GENERALINTERFACEFRAMELOWERCONTROLPANEL,
              name=u'LowerControlPanel', parent=self.LeftInterfacePanel,
              pos=wx.Point(2, 652), size=wx.Size(684, 27),
              style=wx.TAB_TRAVERSAL)
        self.LowerControlPanel.SetBackgroundColour(wx.Colour(0, 255, 128))

        self.UpperInterfacePanel = wx.Panel(id=wxID_GENERALINTERFACEFRAMEUPPERINTERFACEPANEL,
              name=u'UpperInterfacePanel', parent=self.LeftInterfacePanel,
              pos=wx.Point(2, 2), size=wx.Size(684, 516),
              style=wx.TAB_TRAVERSAL)
        self.UpperInterfacePanel.SetBackgroundColour(wx.Colour(128, 128, 128))
        self.UpperInterfacePanel.SetHelpText(u'UpperInterfacePanel')

        self.LowerInterfacePanel = wx.Panel(id=wxID_GENERALINTERFACEFRAMELOWERINTERFACEPANEL,
              name=u'LowerInterfacePanel', parent=self.LeftInterfacePanel,
              pos=wx.Point(2, 522), size=wx.Size(684, 126),
              style=wx.TAB_TRAVERSAL)
        self.LowerInterfacePanel.SetBackgroundColour(wx.Colour(192, 192, 192))

        self.UpperInterface = wx.Notebook(id=wxID_GENERALINTERFACEFRAMEUPPERINTERFACE,
              name=u'UpperInterface', parent=self.UpperInterfacePanel,
              pos=wx.Point(2, 2), size=wx.Size(680, 512), style=0)

        self.LowerInterface = wx.Treebook(id=wxID_GENERALINTERFACEFRAMELOWERINTERFACE,
              name=u'LowerInterface', parent=self.LowerInterfacePanel,
              pos=wx.Point(2, 2), size=wx.Size(680, 122), style=0)

        self.Display = IEPanel(id=wxID_GENERALINTERFACEFRAMEDISPLAY,
              name=u'Display', parent=self.UpperInterface, pos=wx.Point(0, 0),
              size=wx.Size(672, 486), style=wx.TAB_TRAVERSAL)

        self.Shell = ShellPanel(id=wxID_GENERALINTERFACEFRAMESHELL,
              name=u'Shell', parent=self.LowerInterface, pos=wx.Point(0, 0),
              size=wx.Size(622, 122), style=wx.TAB_TRAVERSAL)

        self._init_coll_UpperInterface_Pages(self.UpperInterface)
        self._init_coll_LowerInterface_Pages(self.LowerInterface)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)
        #make the shell self aware--requires that ShellEditor.interp.locals=locals()
        self.Shell.ShellEditor.pushLine("shell=locals()['self']")
        #This assumes the main frame is exactly 6 levels above
        self.Shell.ShellEditor.pushLine("frame=shell.Parent.Parent.Parent.Parent.Parent.Parent")
        #self.Shell.ShellEditor.pushLine("shell=locals()['self']",'\n')
    def OnFileMenuOpenMenu(self, event):
        event.Skip()


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    sys.stdout=frame.Shell.ShellEditor.stdout
    sys.stdin=frame.Shell.ShellEditor.stdin
    frame.Show()

    app.MainLoop()
