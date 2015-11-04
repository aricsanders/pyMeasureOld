#-----------------------------------------------------------------------------
# Name:        ProcessSheets.py
# Purpose:     To handle process sheets and travelers
#
# Author:      Aric Sanders
#
# Created:     2010/11/27
# RCS-ID:      $Id: ProcessSheets.py $
# Copyright:   (c) 2009
# Licence:     GPL
#-----------------------------------------------------------------------------
""" PrcoessSheets contains classes and functions for working with XML based
travelers and processing sheets"""

#-------------------------------------------------------------------------------
# Standard Imports
import os                                           # path functions etc. 
import fnmatch                                     # unix Style filename filter 
import sys                                         # System 
import re                                          # For regular expressions     
import urlparse                                    # To form proper URLs 
import datetime                                    # For timestamping     
import xml.dom                                     # Xml document handling 
import xml.dom.minidom                             # For xml parsing
from xml.dom.minidom import getDOMImplementation   # Making blank XML documents 
from types import *                                # to allow input testing
#-------------------------------------------------------------------------------
# Third Party Imports

# This determines PYMEASURE_ROOT below and checks if everything is installed properly 
try: 
    import pyMeasure
except:
    print("The topmost pyMeasure folder was not found please make sure that the directory directly above it is on sys.path") 
    raise
# For XLST transformations of the data
try:
    from lxml import etree
    XSLT_CAPABLE=1
except:
    print("Transformations using XSLT are not available please check the lxml module")
    XSLT_CAPABLE=0
    pass
# For auto generation of common method aliases
try:
    from pyMeasure.Code.Misc.Alias import *
    METHOD_ALIASES=1
except:
    print("The module pyMeasure.Code.Misc.Alias was not found")
    METHOD_ALIASES=0
    pass
#-------------------------------------------------------------------------------
# Module Constants

PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))
# I should change this to something a little more permanent
DEFAULT_PROCESS_XSL=os.path.join(PYMEASURE_ROOT,'Code/Development',
'WaferName_STYLE.xsl').replace('\\','/')
#-------------------------------------------------------------------------------
# Module Functions
# Need a function that reads in defined processes and allows one use them over



#-------------------------------------------------------------------------------
# Module Classes
class ProcessSheet():
    """ Class for the process sheet, i.e. the instructions for doing the fab"""
    def __init__(self,file_path=None,**options):
        """ Intializes the ProcessSheet Class"""
        
        # This is a general pattern for adding a lot of options
        # The next more advanced thing to do is retrieve defaults from a settings file
        defaults={'style_sheet':DEFAULT_PROCESS_XSL}
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
            
            
        #if the file path is not supplied create a new log
        if file_path is None:
            impl=getDOMImplementation()
            self.document=impl.createDocument(None,\
            'Process_Sheet',None)
            
            try:
                self.style_sheet=self.options['style_sheet']
            except KeyError:
                self.style_sheet=DEFAULT_PROCESS_XSL
                
            new_node=self.document.createProcessingInstruction(\
            'xml-stylesheet',\
            u'type="text/xsl" href="%s"'%self.style_sheet)
            self.document.insertBefore(new_node,self.document.documentElement)
            self.path=os.path.join(PYMEASURE_ROOT,'Code/Development',
            'New_Process_Sheet'+'.xml').replace('\\','/')
        else:
            file_in=open(file_path,'r')
            self.document=xml.dom.minidom.parse(file_in)
            file_in.close()
            self.path=file_path
            
     # Define Method Aliases if they are available
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)   
        # Create a number:node dictionary for process
        self.Index_Process_dictionary=dict([(str(node.getAttribute('Index')),
        node) for node in \
        self.document.getElementsByTagName('Process')]) 
        
        #print self.Index_Process_dictionary
        # Setup current state, there is a naming inconsitancy here          
        # Should these be index 0 or index 1 lists?
        self.Process_Step_dictionary={}
        for index,node in  self.Index_Process_dictionary.iteritems():
            step_dictionary={}
            for child in node.childNodes:
                if child.nodeType is child.ELEMENT_NODE and child.hasAttributes():
                    step_dictionary[str(child.getAttribute('Index'))]=child
            self.Process_Step_dictionary[index]=step_dictionary
        #print self.Process_Step_dictionary
        self.current_process_Index=1
        self.current_process=self.get_process(self.current_process_Index)
        self.current_step_Index=1
        self.current_step=self.get_step(self.current_step_Index)
        
        #print self.current_step
    def get_process(self,process_identifier):
        """ Returns a process node given an identifier"""
        try:
            return self.Index_Process_dictionary[process_identifier]
        except KeyError:
            index=str(process_identifier)
            return self.Index_Process_dictionary[index]
        
    def set_process(self,process_identifier):
        """ Sets the current process given the identifier"""
        try:
            self.current_process_Index=str(process_identifier)
            self.current_process=self.get_process(self.current_process_Index)
            step_indices=map(lambda x:int(x),self.Process_Step_dictionary[str(process_identifier)].keys())
            #print step_indices
            min_indice=str(min(step_indices))
            self.current_step_Index=min_indice
            self.current_step=self.get_step(self.current_step_Index)
        except:
            raise
        
    def next_process(self):
        """ Returns the process after the current one"""
        try:
            new_index=int(self.current_process_Index)+1
            self.set_process(new_index)
        except KeyError:
            process_indices=map(lambda x:int(x),self.Process_Step_dictionary.keys())

            max_index=max(process_indices)
            min_index=min(process_indices)
            if new_index>max_index:
                new_index=min_index
            elif new_index<min_index:
                new_index=max_index
            self.set_process(new_index)
        
    def previous_process(self):
        """ Sets the current process to the process before, 
        note: it resets the current step to the first one in the new process"""
        try:
            new_index=int(self.current_process_Index)-1
            self.set_process(new_index)
        except KeyError:
            process_indices=map(lambda x:int(x),self.Process_Step_dictionary.keys())
            #print step_indices
            #print process_indices
            max_index=max(process_indices)
            min_index=min(process_indices)
            if new_index>max_index:
                new_index=min_index
            elif new_index<min_index:
                new_index=max_index
            self.set_process(new_index)
    def add_process(self,new_process=None,position=None):
        """Adds a new process at the end"""
        root=self.document.documentElement
        process_indices=map(lambda x:int(x),self.Process_Step_dictionary.keys())
        #print step_indices
        #print process_indices
        max_index=max(process_indices)
        min_index=min(process_indices)
        if position is None:
            new_index=max_index+1
        try:
            if new_process is None:
                pass
            else:
                new_entry=new_process
        except:
            raise
        # Test the new process for the index attribute
        try:
            old_index=new_entry.getAttribute('Index')
            new_entry.setAttribute('Index',str(new_index))
            root.appendChild(new_entry)
        except:
            new_entry.setAttributeNode('Index')
            new_entry.setAttribute(str(new_index))
            root.appendChild(new_entry)
        
        self.Index_Process_dictionary=dict([(str(node.getAttribute('Index')),
        node) for node in \
        self.document.getElementsByTagName('Process')])        
        
        self.Process_Step_dictionary={}
        for index,node in  self.Index_Process_dictionary.iteritems():
            step_dictionary={}
            for child in node.childNodes:
                if child.nodeType is child.ELEMENT_NODE and child.hasAttributes():
                    step_dictionary[str(child.getAttribute('Index'))]=child
            self.Process_Step_dictionary[index]=step_dictionary
        
    def remove_process(self, process_identifier):
        pass
    def move_process(self,process_identifier,new_index):
        pass
    
    def next_step(self):
        """ Sets the step to the next one"""
        # Note this does not handle non-consective step indices correctly
        try:
            new_index=int(self.current_step_Index)+1
            self.set_step(new_index,self.current_process_Index)
        except KeyError:
            step_indices=map(lambda x:int(x),self.Process_Step_dictionary[self.current_process_Index].keys())
            #print step_indices
            
            max_index=max(step_indices)
            min_index=min(step_indices)
            if new_index>max_index:
                new_index=min_index
            elif new_index<min_index:
                new_index=max_index
            self.set_step(new_index,self.current_process_Index)
    def previous_step(self):
        """ Sets the step to the previous one"""
        try:
            new_index=int(self.current_step_Index)-1
            self.set_step(new_index,self.current_process_Index)
        except KeyError:
            step_indices=map(lambda x:int(x),self.Process_Step_dictionary[self.current_process_Index].keys())
            #print step_indices
            
            max_index=str(max(step_indices))
            min_index=str(min(step_indices))
            if new_index>max_index:
                new_index=min_index
            elif new_index<min_index:
                new_index=max_index
            self.set_step(new_index,self.current_process_Index)
    def get_step(self,step_identifier):
        """ Returns the step specified by identifier for the current process"""
        process_index=self.current_process.getAttribute('Index')
        step_identifier=str(step_identifier)
        try:
            return self.Process_Step_dictionary[process_index][step_identifier]
        except:
            raise
    def set_step(self,step_identifier,process_identifier):
        """Sets the current step given an Identifier"""
        try:
            self.set_process(process_identifier)
            self.current_step_Index=str(step_identifier)
            self.current_step=self.Process_Step_dictionary[process_identifier][self.current_step_Index]
        except:
            raise
            
    def add_step(self,process):
        """ Adds a step to the selected process"""
        pass
    def remove_step(self,step_identifier,process):
        pass
    def move_step(self,step_identifier,new_index):
        pass
    def edit_step(self,step_identifier,process):
        pass
    def analyze_step_data(self):
        pass
    def analyze_process_data(self):
        pass
    
                           
    def save(self,path=None):
        """" Saves the process sheet as an XML file."""
        if path is None:
            path=self.path
        # This has been changed to work in 2.6 and beyond...
        file_out=open(path,'w')
        file_out.write(self.document.toprettyxml())
        file_out.close()
    if XSLT_CAPABLE:
        def to_HTML(self,XSLT=DEFAULT_PROCESS_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml())) 
            return HTML
        def current_process_to_HTML(self,XSLT=DEFAULT_PROCESS_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.current_process.toxml())) 
            return HTML
        # Need to have a template for Step defined in XSLT
        def current_step_to_HTML(self,XSLT=DEFAULT_PROCESS_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.current_step.toxml())) 
            return HTML
    def show(self,mode='text'):
        """ Displays a Log either as formatted text in the command line or in a 
        window (using wx)"""
        def tag_to_tagName(tag):
            tagName=tag.replace('<','')
            tagName=tagName.replace('/','')
            tagName=tagName.replace('>','')
            return tagName
        # This is a little broken, it only prints the process index
        if mode in ['text','txt','cmd line','cmd']:
            for node in self.document.getElementsByTagName('Process'):
                print 'Process Index: %s '%(node.getAttribute('Index'))
                print node.firstChild.nodeValue
        #This is the same as print self
        elif re.search('xml',mode,re.IGNORECASE):
            for node in self.document.getElementsByTagName('Process'):
                print node.toprettyxml()
        # This works well        
        elif re.search('Window|wx',mode,re.IGNORECASE):
            try:
                import wx.html
            except:
                print 'Cannot locate wx, please add to sys.path'
            app = wx.PySimpleApp()
            frame=wx.Frame(None)
            html_window=wx.html.HtmlWindow(frame)
            html_window.SetPage(str(self.to_HTML()))
            frame.Show()

            app.MainLoop()
            
    def __str__(self):
        """Controls the behavior of the process sheet if a string function is called"""
        return self.document.toxml()      
class ProcessDevelopmentSheet(ProcessSheet):
    """ This should be essentailly the same thing except with multiple repeats of a given process"""
    pass        
class Traveler(ProcessSheet):
    """ This is a process sheet that has process data entered for a real wafer"""
    pass
class ProcessBook(ProcessSheet):
    """ This is a full explanation of the process with references and other things"""
    pass
#-------------------------------------------------------------------------------
# Script Definitions

def test_ProcessSheet():
    """ Tests the class Process Sheet"""
    test_sheet=ProcessSheet('WaferName.xml')
    print os.getcwd()
    #print 'The Test sheet is :/n'
    #print test_sheet
    print 'The new processes are'
    print test_sheet.Index_Process_dictionary.keys()
    print 'The current process in HTML is:'
    print test_sheet.current_process_to_HTML()
    print 'The Current Step is:'
    print test_sheet.current_step_to_HTML()
    test_sheet.show('xml')
    print 'The new process is 2'
    test_sheet.set_process(2)
    print test_sheet.current_process_to_HTML()
    print 'The New step is 1'
    print test_sheet.current_step_to_HTML()
    test_sheet.show('wx')
def test_next_and_previous():
    test_sheet=ProcessSheet('WaferName.xml')
    print 'The current process index is %s'%test_sheet.current_process_Index
    test_sheet.next_process()
    print 'The new process index is %s'%test_sheet.current_process_Index
    print 'The current process index is %s'%test_sheet.current_process_Index
    test_sheet.previous_process()
    print 'The new process index is %s'%test_sheet.current_process_Index
    test_sheet.previous_process()
    print 'The new process index is %s'%test_sheet.current_process_Index
        
    print 'The current step index is %s'%test_sheet.current_step_Index
    test_sheet.next_step()
    print 'The new step index is %s'%test_sheet.current_step_Index
    test_sheet.previous_step()
    print 'The new step index is %s'%test_sheet.current_step_Index
    test_sheet.previous_step()
    print 'The new step index is %s'%test_sheet.current_step_Index
def test_add_process():
    """Tests the add process method"""
    test_sheet=ProcessSheet('WaferName.xml')
    new_process=test_sheet.get_process(1)
    test_sheet.add_process(new_process)
    print test_sheet
    
#-------------------------------------------------------------------------------
# Module Runner



if __name__ == '__main__':
    test_ProcessSheet()
    #test_next_and_previous()
    #test_add_process()