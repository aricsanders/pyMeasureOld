#-----------------------------------------------------------------------------
# Name:        XMLEditPanel.py
# Purpose:     A panel to edit general XML files
#
# Author:      Aric Sanders
#
# Created:     2011/12/31
# RCS-ID:      $Id: XMLEditPanel.py $
# Copyright:   (c) 2006
# Licence:     <your licence>
#-----------------------------------------------------------------------------
#Boa:FramePanel:XMLEditPanel
""" This module defines a simple xml editor that shows the xsl if available"""
import wx
import wx.html
import wx.stc
# This determines PYMEASURE_ROOT below and checks if everything is installed properly 
try: 
    import pyMeasure
except:
    print("The topmost pyMeasure folder was not found please make sure that the directory directly above it is on sys.path") 
    raise

try:
    from pyMeasure.Code.Development.XMLGeneral import *
    from pyMeasure.Code.Development.StyledTextCtrlPanel import *
    
except:
    print("Could not import XMLGeneral")
    raise





#-------------------------------------------------------------------------------
# Constants
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))


[wxID_XMLEDITPANEL, wxID_XMLEDITPANELEDITDISPLAYPANEL, 
 wxID_XMLEDITPANELEDITPANEL, wxID_XMLEDITPANELFILECONTROLPANEL, 
 wxID_XMLEDITPANELFILEOPENBUTTON, wxID_XMLEDITPANELFILESAVEBUTTON, 
 wxID_XMLEDITPANELNOTEBOOK1, wxID_XMLEDITPANELSOURCEVIEW, 
 wxID_XMLEDITPANELTRANSFORMEDXML, wxID_XMLEDITPANELVIEWSOURCE, 
 wxID_XMLEDITPANELXSLVIEW, 
] = [wx.NewId() for _init_ctrls in range(11)]

class XMLEditPanel(wx.Panel):
    _custom_classes = {'wx.stc.StyledTextCtrl': ['XMLSTC']}
    def _init_coll_EditSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.notebook1, 1, border=1, flag=wx.ALL | wx.EXPAND)

    def _init_coll_FileControlSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.FileOpenButton, 0, border=0, flag=0)
        parent.AddWindow(self.FileSaveButton, 0, border=0, flag=0)
        parent.AddWindow(self.ViewSource, 0, border=0, flag=0)

    def _init_coll_MainPanelSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.FileControlPanel, 1, border=1, flag=wx.EXPAND)
        parent.AddWindow(self.EditDisplayPanel, 9, border=1, flag=wx.EXPAND)

    def _init_coll_notebook1_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.EditPanel, select=True,
              text=u'Edit')
        parent.AddPage(imageId=-1, page=self.SourceView, select=False,
              text=u'Source')
        parent.AddPage(imageId=-1, page=self.XSLView, select=False, text=u'XSL')
        parent.AddPage(imageId=-1, page=self.TransformedXML, select=False,
              text=u'HTML')

    def _init_sizers(self):
        # generated method, don't edit
        self.MainPanelSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.FileControlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.EditSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.EditControlSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_MainPanelSizer_Items(self.MainPanelSizer)
        self._init_coll_FileControlSizer_Items(self.FileControlSizer)
        self._init_coll_EditSizer_Items(self.EditSizer)

        self.SetSizer(self.MainPanelSizer)
        self.FileControlPanel.SetSizer(self.FileControlSizer)
        self.EditDisplayPanel.SetSizer(self.EditSizer)
        self.EditPanel.SetSizer(self.EditControlSizer)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_XMLEDITPANEL, name=u'XMLEditPanel',
              parent=prnt, pos=wx.Point(358, 257), size=wx.Size(722, 545),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(706, 507))

        self.FileControlPanel = wx.Panel(id=wxID_XMLEDITPANELFILECONTROLPANEL,
              name=u'FileControlPanel', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(706, 50), style=wx.TAB_TRAVERSAL)
        self.FileControlPanel.SetBackgroundColour(wx.Colour(192, 192, 192))

        self.EditDisplayPanel = wx.Panel(id=wxID_XMLEDITPANELEDITDISPLAYPANEL,
              name=u'EditDisplayPanel', parent=self, pos=wx.Point(0, 50),
              size=wx.Size(706, 457), style=wx.TAB_TRAVERSAL)

        self.FileOpenButton = wx.Button(id=wxID_XMLEDITPANELFILEOPENBUTTON,
              label=u'Open', name=u'FileOpenButton',
              parent=self.FileControlPanel, pos=wx.Point(0, 0), size=wx.Size(75,
              23), style=0)
        self.FileOpenButton.Bind(wx.EVT_BUTTON, self.OnFileOpenButtonButton,
              id=wxID_XMLEDITPANELFILEOPENBUTTON)

        self.FileSaveButton = wx.Button(id=wxID_XMLEDITPANELFILESAVEBUTTON,
              label=u'Save', name=u'FileSaveButton',
              parent=self.FileControlPanel, pos=wx.Point(75, 0),
              size=wx.Size(75, 23), style=0)
        self.FileSaveButton.Bind(wx.EVT_BUTTON, self.OnFileSaveButtonButton,
              id=wxID_XMLEDITPANELFILESAVEBUTTON)

        self.ViewSource = wx.Button(id=wxID_XMLEDITPANELVIEWSOURCE,
              label=u'View Source', name=u'ViewSource',
              parent=self.FileControlPanel, pos=wx.Point(150, 0),
              size=wx.Size(75, 23), style=0)

        self.notebook1 = wx.Notebook(id=wxID_XMLEDITPANELNOTEBOOK1,
              name='notebook1', parent=self.EditDisplayPanel, pos=wx.Point(1,
              1), size=wx.Size(704, 455), style=0)

        self.EditPanel = wx.Panel(id=wxID_XMLEDITPANELEDITPANEL,
              name=u'EditPanel', parent=self.notebook1, pos=wx.Point(0, 0),
              size=wx.Size(696, 429), style=wx.TAB_TRAVERSAL)

        self.SourceView = XMLSTC(id=wxID_XMLEDITPANELSOURCEVIEW,
              name=u'SourceView', parent=self.notebook1, pos=wx.Point(0, 0),
              size=wx.Size(696, 429), style=0)
        self.SourceView.SetLexer(wx.stc.STC_LEX_XML)
        self.SourceView.SetHighlightGuide(0)
        self.SourceView.SetTargetEnd(100)

        self.XSLView = XMLSTC(id=wxID_XMLEDITPANELXSLVIEW, name=u'XSLView',
              parent=self.notebook1, pos=wx.Point(0, 0), size=wx.Size(696, 429),
              style=0)

        self.TransformedXML = wx.html.HtmlWindow(id=wxID_XMLEDITPANELTRANSFORMEDXML,
              name=u'TransformedXML', parent=self.notebook1, pos=wx.Point(0, 0),
              size=wx.Size(696, 429), style=wx.html.HW_SCROLLBAR_AUTO)

        self._init_coll_notebook1_Pages(self.notebook1)

        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)

    def OnFileOpenButtonButton(self, event):
        dlg = wx.FileDialog(self, 'Choose an XML file to open', '.', '', '*.*', wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.open_file(filename)
                            
        finally:
            dlg.Destroy()

    def OnFileSaveButtonButton(self, event):
        try:
            path=self.current_xml.path.split('/')[-1]
        except:
            path=''
        #print path
        dlg = wx.FileDialog(self, 'Save the file', '.', path, '', wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                try:
                    self.new_xml=EtreeXML(self.SourceView.GetText())
                    self.new_xml.save(filename)
                    self.open_file(filename)
                except:
                    raise
        finally:
            dlg.Destroy()
        event.Skip()
    def  open_file(self,filename):   
                os.chdir(os.path.dirname(filename))
                try:
                    self.current_xml=EtreeXML(filename)
                    text=str(self.current_xml)
                    lenText = len(text.encode('utf8'))
                    self.SourceView.SetStyling(lenText, 0)
                    self.SourceView.SetText(text)
                    self.SourceView.EnsureCaretVisible()
                    self.notebook1.ChangeSelection(1)
                    try:
                        
                        #print filename.split('.')[-1]
                        if re.search('htm|html',filename.split('.')[-1]):
                            self.TransformedXML.SetPage(str(self.current_xml))
                        else:
                            self.TransformedXML.SetPage(str(self.current_xml.to_HTML()))
                    except:
                        self.TransformedXML.SetPage("<strong> No html available</strong>")
                    try:
                        self.XSLView.SetText(etree.tostring(self.current_xml.xsl, pretty_print=True))
                    except:
                        self.XSLView.SetText("Sorry no xsl available")
                        

                except:
                    raise
##    def build_edit_control(self):
##        """This method builds the edit control given a XMLEtree class"""
##        self.edit_controls=[]
##        for index,node in self.current_xml.node_dictionary.iteritems():
##            new_control_tag=wx.TextCtrl(id=wx.NewId(), name='textCtrl1',
##              parent=self.EditPanel, pos=wx.Point(64, 32), size=wx.Size(100, 21), style=0,
##              value=node.tag)
##            new_control_text=wx.TextCtrl(id=wx.NewId(), name='textCtrl1',
##              parent=self.EditPanel, pos=wx.Point(64, 32), size=wx.Size(100, 21), style=0,
##              value=node.text)
##            for attribute,attribute_value in node.attrib.iteritems():
##                new_control_attribute=wx.TextCtrl(id=wx.NewId(), name='textCtrl1',
##                parent=self.EditPanel, pos=wx.Point(64, 32), size=wx.Size(100, 21), style=0,
##                value=attribute)
##                new_control_attribute.Bind(wx.EVT_BUTTON, lambda self.current_xml.node_dicitionary[index].,
##                id=wxID_XMLEDITPANELFILESAVEBUTTON)
##                new_control_value=wx.TextCtrl(id=wx.NewId(), name='textCtrl1',
##                parent=self.EditPanel, pos=wx.Point(64, 32), size=wx.Size(100, 21), style=0,
##                value=attribute_value)                    
##                
##        #self.current_xml
##        pass
def test_XMLEditPanel():
    app = wx.PySimpleApp()
    frame = wx.Frame(None,size=wx.Size(900, 800))
    panel=XMLEditPanel(id=1, name=u'IV Panel',
              parent=frame, pos=wx.Point(350, 204), size=wx.Size(200, 800),
              style=wx.TAB_TRAVERSAL)
    sizer=wx.BoxSizer()
    sizer.Add(panel,1,wx.EXPAND,2)
    frame.SetSizerAndFit(sizer)
    frame.SetSize(wx.Size(800, 600))
    frame.Show()

    app.MainLoop()    
    
    
    
if __name__ == '__main__':
    test_XMLEditPanel()

