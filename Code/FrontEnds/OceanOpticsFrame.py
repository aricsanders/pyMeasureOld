#Boa:Frame:Frame1
#-------------------------------------------------------------------------------
# Standard Imports
import re

#-------------------------------------------------------------------------------
# Third Party
import wx
import wx.html
import pyMeasure.Code.BackEnds.OceanOptics as OceanOptics
from USB2000Panel import USB2000Panel
from QE65000Panel import QE65000Panel


def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1BUTTON2, wxID_FRAME1GET_SPECTROMETERS, 
 wxID_FRAME1HTMLWINDOW1, wxID_FRAME1NOTEBOOK1, wxID_FRAME1PANEL1, 
 wxID_FRAME1PANEL2, wxID_FRAME1PANEL3, wxID_FRAME1STATUSBAR1, 
] = [wx.NewId() for _init_ctrls in range(9)]

[wxID_FRAME1FILE_MENUCLOSE, wxID_FRAME1FILE_MENUOPEN, 
 wxID_FRAME1FILE_MENUPRINT, 
] = [wx.NewId() for _init_coll_file_menu_Items in range(3)]

class MyHTML(wx.html.HtmlWindow):
    """ speciallized Html window """
    def OnLinkClicked(self,link_info):
        if re.search('USB',link_info.GetHref()):
            new_page=USB2000Panel(self.GetParent().GetParent().GetParent(),-1, wx.Point(0, 280), wx.Size(615, 56), wx.TAB_TRAVERSAL, 'Spectrometer')
        elif re.search('QE',link_info.GetHref()):
            new_page=QE65000Panel(self.GetParent().GetParent().GetParent(),-1, wx.Point(0, 280), wx.Size(615, 56), wx.TAB_TRAVERSAL, 'Spectrometer')
        self.GetParent().GetParent().GetParent().AddPage(imageId=-1, page=new_page, select=True,
              text=link_info.GetHref())
        
              
       
        
[wxID_FRAME1HELP_MENUBROWSER] = [wx.NewId() for _init_coll_help_menu_Items in range(1)]

class Frame1(wx.Frame):
    _custom_classes={'wx.Panel':['USB2000Panel','QE65000Panel'],'wx.html.HtmlWindow':['MyHTML']}
    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.panel3, 5, border=2, flag=wx.ALL | wx.EXPAND)
        parent.AddWindow(self.panel2, 1, border=0, flag=wx.EXPAND)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.htmlWindow1, 1, border=2, flag=wx.ALL | wx.EXPAND)

    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.file_menu, title=u'File')
        parent.Append(menu=self.help_menu, title=u'Help')

    def _init_coll_file_menu_Items(self, parent):
        # generated method, don't edit

        parent.Append(help=u'Open a device', id=wxID_FRAME1FILE_MENUOPEN,
              kind=wx.ITEM_NORMAL, text=u'Open')
        parent.Append(help=u'Close', id=wxID_FRAME1FILE_MENUCLOSE,
              kind=wx.ITEM_NORMAL, text=u'Close')
        parent.Append(help=u'Print ', id=wxID_FRAME1FILE_MENUPRINT,
              kind=wx.ITEM_NORMAL, text=u'Print')

    def _init_coll_help_menu_Items(self, parent):
        # generated method, don't edit

        parent.Append(help=u'Help Browser', id=wxID_FRAME1HELP_MENUBROWSER,
              kind=wx.ITEM_NORMAL, text=u'Help Browser')
        self.Bind(wx.EVT_MENU, self.OnHelp_menuItems0Menu,
              id=wxID_FRAME1HELP_MENUBROWSER)

    def _init_coll_notebook1_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.panel1, select=True,
              text=u'Ocean Optics Devices')

    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(number=0, text='Fields0')

        parent.SetStatusWidths([-1])

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)

        self.panel1.SetSizer(self.boxSizer1)
        self.panel3.SetSizer(self.boxSizer2)

    def _init_utils(self):
        # generated method, don't edit
        self.file_menu = wx.Menu(title=u'File')

        self.help_menu = wx.Menu(title=u'Help')

        self.menuBar1 = wx.MenuBar()

        self._init_coll_file_menu_Items(self.file_menu)
        self._init_coll_help_menu_Items(self.help_menu)
        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(450, 202), size=wx.Size(631, 436),
              style=wx.DEFAULT_FRAME_STYLE,
              title=u'Ocean Optics Spectrometers')
        self._init_utils()
        self.SetClientSize(wx.Size(623, 402))
        self.SetMenuBar(self.menuBar1)
        self.Bind(wx.EVT_IDLE, self.OnFrame1Idle)

        self.statusBar1 = wx.StatusBar(id=wxID_FRAME1STATUSBAR1,
              name='statusBar1', parent=self, style=0)
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.notebook1 = wx.Notebook(id=wxID_FRAME1NOTEBOOK1, name='notebook1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(623, 362), style=0)

        self.panel1 = wx.Panel(id=wxID_FRAME1PANEL1, name='panel1',
              parent=self.notebook1, pos=wx.Point(0, 0), size=wx.Size(615, 336),
              style=wx.TAB_TRAVERSAL)

        self.panel2 = wx.Panel(id=wxID_FRAME1PANEL2, name='panel2',
              parent=self.panel1, pos=wx.Point(0, 280), size=wx.Size(615, 56),
              style=wx.TAB_TRAVERSAL)

        self.panel3 = wx.Panel(id=wxID_FRAME1PANEL3, name='panel3',
              parent=self.panel1, pos=wx.Point(2, 2), size=wx.Size(611, 276),
              style=wx.TAB_TRAVERSAL)

        self.htmlWindow1 = MyHTML(id=wxID_FRAME1HTMLWINDOW1, name='htmlWindow1',
              parent=self.panel3, pos=wx.Point(2, 2), size=wx.Size(607, 272),
              style=wx.html.HW_SCROLLBAR_AUTO)

        self.get_spectrometers = wx.Button(id=wxID_FRAME1GET_SPECTROMETERS,
              label=u'Get Spectrometers', name=u'get_spectrometers',
              parent=self.panel2, pos=wx.Point(0, 0), size=wx.Size(104, 32),
              style=0)
        self.get_spectrometers.Bind(wx.EVT_BUTTON,
              self.OnGet_spectrometersButton, id=wxID_FRAME1GET_SPECTROMETERS)

        self.button2 = wx.Button(id=wxID_FRAME1BUTTON2, label=u'Information',
              name='button2', parent=self.panel2, pos=wx.Point(0, 32),
              size=wx.Size(104, 23), style=0)
        self.button2.Bind(wx.EVT_BUTTON, self.OnButton2Button,
              id=wxID_FRAME1BUTTON2)

        self._init_coll_notebook1_Pages(self.notebook1)

        self._init_sizers()

    def __init__(self, parent):
        self.wrapper=OceanOptics.Wrapper()
        self._init_ctrls(parent)
        icon=wx.Icon(name=r'C:\Documents and Settings\sandersa\My Documents\Share\pyMeasure\Settings\Images\OceanOpticsLogo.bmp', type=wx.BITMAP_TYPE_ICO)

        self.SetIcon(icon)
  

    def OnHelp_menuItems0Menu(self, event):
        event.Skip()

    def OnButton1Button(self, event):
        event.Skip()


    def OnGet_spectrometersButton(self, event):
        self.wrapper.openAllSpectrometers()
        self.number_of_spectrometers=self.wrapper.getNumberOfSpectrometersFound()
        self.spectrometers_info=[]
        info={}
        self.HTML_text=''
        for i in range(self.number_of_spectrometers):
            name=self.wrapper.getName(i)
            info['name']=name
            serial=self.wrapper.getSerialNumber(i)
            info['serial']=serial
            for key,value in info.iteritems():
                self.HTML_text=self.HTML_text+'<BR><b><i>%s</i></b> :<a href=%s>%s</a> '%(key,value,value)
            self.HTML_text=self.HTML_text+'<BR><HR>'    
        self.htmlWindow1.SetPage(self.HTML_text)
        self.Update()

    def OnButton2Button(self, event):
        #TODO: use a DataHandler to get and transform the xml info sheets
        event.Skip()

    def OnFrame1Idle(self, event):
        # this is the render loop for active spectrometers:
        # TODO: make something that can scale
        number_pages=self.notebook1.GetPageCount()
        if number_pages>1:
            try: 
                for i in range(number_pages):
                    try:
                        on_off=self.notebook1.GetCurrentPage().genBitmapTextToggleButton1.GetToggle()
                        if on_off:
                            try:
                                self.notebook1.GetCurrentPage().update_plot()
                            except:pass
                    except: pass
            except:pass
        event.Skip()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    frame.Show()

    app.MainLoop()
