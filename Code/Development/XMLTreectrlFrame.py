#Boa:Frame:Frame1

import wx
from xml.parsers import expat as parsermodule
import os
import xml.dom.minidom  
import xml
from types import *  


# This determines PYMEASURE_ROOT below and checks if everything is installed properly 
try: 
    import pyMeasure
except:
    print("The topmost pyMeasure folder was not found please make sure that the directory directly above it is on sys.path") 
    raise

ROOT_DIRECTORY=os.path.dirname(os.path.realpath(pyMeasure.__file__))
DEFAULT_LOG_XSL=os.path.join(ROOT_DIRECTORY,'Instruments',
'SRS810_Lockin2.xml').replace('\\','/')

def create(parent):
    return Frame1(parent)
class XMLTree(wx.TreeCtrl):
    def __init__(self, parent, id, pos, size, style, name):
        
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style,wx.DefaultValidator, name)
        test_file=DEFAULT_LOG_XSL
        self.LoadTree()
        
        

##        file_in=open(test_file,'r')
##        self.document=xml.dom.minidom.parse(test_file)
##        file_in.close()
##        self.path=test_file             
##        self.root_name=self.document.documentElement.nodeName
##        self.AddRoot(self.root_name)
    
    
    
    def Update(self,filename=DEFAULT_LOG_XSL):
        self.node_stack=[]
        print filename
        self.DeleteAllItems()
        file_in=open(filename,'r')
        self.document=xml.dom.minidom.parse(file_in)
        file_in.close()
        self.path=filename
        print  self.path           
            

        self.root_name=self.document.documentElement.tagName
        print self.root_name
        self.root_node=self.AddRoot(self.root_name)
        self.node_stack.append(self.root_node)
        for child in self.document.documentElement.childNodes:
            #print child.nodeType
            if child.nodeType in [1,'1']:
                new_node=self.AppendItem(self.root_node,child.tagName)
                self.node_stack.append(new_node)
                for grandchild in child.childNodes:
                    #print grandchild.nodeName
                    if grandchild.nodeType in [1,'1']:
                        granchild=self.AppendItem(new_node,grandchild.tagName)
                    elif grandchild.nodeType in [3,'3']:
                        granchild=self.AppendItem(new_node,grandchild.data)
                        #print "Ding"
                       
                    for greatgrandchild in grandchild.childNodes:
                        if greatgrandchild.nodeType in [1,'1']:
                            self.AppendItem(granchild,greatgrandchild.tagName)
                        elif greatgrandchild.nodeType in [3,'3']:
                            self.AppendItem(granchild,greatgrandchild.data)
                            #print "Ding"
                        self.ExpandAll()
        self.ExpandAll()
            
    
    def LoadTree(self, filename=DEFAULT_LOG_XSL):
        self.node_stack=[]
        
        
        if type(filename) is StringType:
            file_in=open(filename,'r')
            self.document=xml.dom.minidom.parse(file_in)
            file_in.close()
            self.path=filename             
            
            
        elif type(filename) is InstanceType:
            self.document=filename
        self.root_name=self.document.documentElement.tagName
        print self.root_name
        self.root_node=self.AddRoot(self.root_name)
        self.node_stack.append(self.root_node)
        for child in self.document.documentElement.childNodes:
            #print child.nodeType
            if child.nodeType in [1,'1']:
                new_node=self.AppendItem(self.root_node,child.tagName)
                self.node_stack.append(new_node)
                for grandchild in child.childNodes:
                    print grandchild.nodeName
                    if grandchild.nodeType in [1,'1']:
                        self.AppendItem(new_node,grandchild.tagName)
                
            

        self.ExpandAll()
        print "Ding"
        
        
        
        
[wxID_FRAME1, wxID_FRAME1PANEL1, wxID_FRAME1TREECTRL1, 
] = [wx.NewId() for _init_ctrls in range(3)]

[wxID_FRAME1MENU1ITEMS0] = [wx.NewId() for _init_coll_menu1_Items in range(1)]

class Frame1(wx.Frame):
    _custom_classes = {'wx.TreeCtrl': ['XMLTree']}
    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.treeCtrl1, 1, border=0, flag=wx.EXPAND)

    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.menu1, title=u'Open')

    def _init_coll_menu1_Items(self, parent):
        # generated method, don't edit

        parent.Append(help=u'Open a xml file', id=wxID_FRAME1MENU1ITEMS0,
              kind=wx.ITEM_NORMAL, text=u'Open XML')
        self.Bind(wx.EVT_MENU, self.OnMenu1Items0Menu,
              id=wxID_FRAME1MENU1ITEMS0)

    def _init_utils(self):
        # generated method, don't edit
        self.menu1 = wx.Menu(title=u'')

        self.menuBar1 = wx.MenuBar()

        self._init_coll_menu1_Items(self.menu1)
        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)

        self.panel1.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(447, 308), size=wx.Size(400, 250),
              style=wx.DEFAULT_FRAME_STYLE, title='Frame1')
        self._init_utils()
        self.SetClientSize(wx.Size(392, 216))
        self.SetMenuBar(self.menuBar1)

        self.panel1 = wx.Panel(id=wxID_FRAME1PANEL1, name='panel1', parent=self,
              pos=wx.Point(0, 0), size=wx.Size(392, 216),
              style=wx.TAB_TRAVERSAL)

        self.treeCtrl1 = XMLTree(id=wxID_FRAME1TREECTRL1, name='treeCtrl1',
              parent=self.panel1, pos=wx.Point(0, 0), size=wx.Size(392, 216),
              style=wx.TR_HAS_BUTTONS)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnMenu1Items0Menu(self, event):
        dlg = wx.FileDialog(self, 'Choose a file', '.', '', '*.*', wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                file = dlg.GetPath()
                self.treeCtrl1.Update(filename=file)

        finally:
            dlg.Destroy()
        event.Skip()


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    frame.Show()

    app.MainLoop()
