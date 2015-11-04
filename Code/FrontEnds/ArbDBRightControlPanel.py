#-----------------------------------------------------------------------------
# Name:        ArbDBRightControlPanel.py
# Purpose:     Control Panel for File Management
#
# Author:      Aric Sanders
#
# Created:     2010/07/20
# RCS-ID:      $Id: ArbDBRightControlPanel.py $
#-----------------------------------------------------------------------------
#Boa:FramePanel:ArbDBRightControlPanel
""" A control panel that plugs into the Interface Frame"""

import wx

[wxID_ARBDBRIGHTCONTROLPANEL, wxID_ARBDBRIGHTCONTROLPANELBUTTON1, 
 wxID_ARBDBRIGHTCONTROLPANELBUTTON2, wxID_ARBDBRIGHTCONTROLPANELBUTTON3, 
] = [wx.NewId() for _init_ctrls in range(4)]

class ArbDBRightControlPanel(wx.Panel):
    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.button1, 0, border=0, flag=0)
        parent.AddWindow(self.button3, 0, border=0, flag=0)
        parent.AddWindow(self.button2, 0, border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_ARBDBRIGHTCONTROLPANEL,
              name=u'ArbDBRightControlPanel', parent=prnt, pos=wx.Point(1038,
              174), size=wx.Size(153, 750), style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(145, 716))

        self.button1 = wx.Button(id=wxID_ARBDBRIGHTCONTROLPANELBUTTON1,
              label='button1', name='button1', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(75, 23), style=0)

        self.button2 = wx.Button(id=wxID_ARBDBRIGHTCONTROLPANELBUTTON2,
              label='button2', name='button2', parent=self, pos=wx.Point(0, 46),
              size=wx.Size(75, 23), style=0)

        self.button3 = wx.Button(id=wxID_ARBDBRIGHTCONTROLPANELBUTTON3,
              label='button3', name='button3', parent=self, pos=wx.Point(0, 23),
              size=wx.Size(75, 23), style=0)

        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)
