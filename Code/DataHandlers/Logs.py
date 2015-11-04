#-----------------------------------------------------------------------------
# Name:        Logs.py
# Purpose:     To Handle Log Data Types
#
# Author:      Aric Sanders
#
# Created:     2009/09/17
# RCS-ID:      $Id: Logs.py $
# Copyright:   --None--
# Licence:     --None--
#-----------------------------------------------------------------------------
""" Logs is a module to handle general Log data types """
#-------------------------------------------------------------------------------
# Standard Imports-- All in the python standard library


import os                                          # path functions etc. 
import sys                                         # System 
import re                                          # For regular expressions     
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

#TODO: Change to PYMEASURE_ROOT
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))
DEFAULT_LOG_XSL=os.path.join(PYMEASURE_ROOT,'Data/Logs',
'DEFAULT_LOG_STYLE.XSL').replace('\\','/')
DEFAULT_END_OF_DAY_LOG_XSL=os.path.join(PYMEASURE_ROOT,'Data/Logs',
'DEFAULT_END_OF_DAY_LOG_STYLE.xsl').replace('\\','/')

#-------------------------------------------------------------------------------
# Class Definitions
    
class Log():
    """ Data container for a general Log"""
    def __init__(self,file_path=None,**options):
        """ Intializes the Log"""
        
        
        # This is a general pattern for adding a lot of options
        # The next more advanced thing to do is retrieve defaults from a settings file
        defaults={'style_sheet':DEFAULT_LOG_XSL}
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
            
            
            
        #if the file path is not supplied create a new log
        

        if file_path is None:
            impl=getDOMImplementation()
            self.document=impl.createDocument(None,\
            'Log',None)
            
            new_node=self.document.createProcessingInstruction(\
            'xml-stylesheet',\
            u'type="text/xsl" href="%s"'%self.options['style_sheet'])
            self.document.insertBefore(new_node,self.document.documentElement)
            self.path=os.path.join(PYMEASURE_ROOT,'Data/Logs',
            'New_Log'+'.xml').replace('\\','/')
        else:
            file_in=open(file_path,'r')
            self.document=xml.dom.minidom.parse(file_in)
            file_in.close()
            self.path=file_path 
            
        # Define Method Aliases if they are available
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)
                        
        self.general_descriptor='Log'
        # TODO: Check how scalable a dictionary of nodes is
        self.Id_node_dictionary=dict([(str(node.getAttribute('Id')),
        node) for node in \
        self.document.getElementsByTagName('Entry')])   
        self.current_entry={}
                   
    def save(self,path=None):
        """" Saves the Log as an XML file"""
        if path is None:
            path=self.path
        file_out=open(path,'w')
        file_out.write(self.document.toprettyxml())
        file_out.close()
    def add_entry(self,entry=None):
        """ Adds an entry element to the current log"""
        root=self.document.documentElement
        if entry is None:
            new_entry=self.document.createElement('Entry')
            value=''
        elif type(entry) is StringType:
            if re.search('<Entry>(.)+</Entry>',entry):
                new_document=xml.dom.minidom.parseString(new_entry)
                new_entry=new_document.documentElement
            else:
                new_document=xml.dom.minidom.parseString('<Entry>'
                +entry+'</Entry>')
                new_entry=new_document.documentElement
        else:
            new_entry=entry
        # Find the max of Id's and add 1 to make a new Id
        if len(self.Id_node_dictionary)==0:
            new_Id='1'
        else:
            max_Id=max([int(Id) for Id in self.Id_node_dictionary.keys()])
            new_Id=str(max_Id+1)
        # Add the Id attribute to the new entry
        Id_attribute=self.document.createAttribute('Id')
        new_entry.setAttributeNode(Id_attribute)
        new_entry.setAttribute('Id',str(new_Id))
        if new_entry.getAttribute('Date'):
            pass
        else:
            # Add the Date attribute, this is the time when the entry was logged
            date=datetime.datetime.utcnow().isoformat()
            Date_attribute=self.document.createAttribute('Date')
            new_entry.setAttributeNode(Date_attribute)
            new_entry.setAttribute('Date',str(date))
        # Now append the new Child        
        root.appendChild(new_entry)
        self.update_Id_node_dictionary()
        
        try:
            value=new_entry.childNodes[0].data
        except:
            value=''
             
        self.current_entry={'Tag':'Entry','Value':value,'Id':new_entry.getAttribute('Id'),
        'Date':new_entry.getAttribute('Date')} 
        
    def edit_entry(self,old_Id,new_value=None,new_Id=None,new_Date=None):
        """Edits and existing entry by replacing the existing values with new ones"""
        node=self.get_entry(str(old_Id))
        if not new_value is None:
            new_text_node=self.document.createTextNode(new_value)
            try:
                old_text_node=node.childNodes[0]
                node.removeChild(old_text_node)
            except: pass
            node.appendChild(new_text_node)
            
        elif not new_Id is None:
            node.setAttribute('Id',new_Id)
        elif not new_Date is None:
            node.setAttribute('Date',new_Date)
        self.current_entry={'Tag':'Entry','Value':node.childNodes[0].data,'Id':node.getAttribute('Id'),
        'Date':node.getAttribute('Date')}    
                
    def get_entry(self,Id):
        """ Returns the entry selcted by Id"""
        return self.Id_node_dictionary[str(Id)]
    
    def set_current_entry(self,Id=-1):
        """Sets self.current_entry """
        entry=self.Id_node_dictionary[str(Id)]
        try:
            value=entry.childNodes[0].data
        except:
            value=''
        self.current_entry={'Tag':'Entry','Value':value,'Id':entry.getAttribute('Id'),
        'Date':entry.getAttribute('Date')}            
    def remove_entry(self,Id):
        """ Removes the entry using the Id attribute"""
        root=self.document.documentElement
        root.removeChild(self.Id_node_dictionary[Id])
        self.update_Id_node_dictionary()
        
    def add_description(self,description=None):
        """ Adds an entry with Id='-1' which holds data about the log itself"""
        root=self.document.documentElement
        new_entry=self.document.createElement('Entry')
        if not description is None:
            text_node=self.document.createTextNode(description)
            new_entry.appendChild(text_node)
        # Add the Id attribute to the new entry
        Id_attribute=self.document.createAttribute('Id')
        new_entry.setAttributeNode(Id_attribute)
        new_entry.setAttribute('Id',str(-1))
        # Add the Date attribute, this is the time when the entry was logged
        date=datetime.datetime.utcnow().isoformat()
        Date_attribute=self.document.createAttribute('Date')
        new_entry.setAttributeNode(Date_attribute)
        new_entry.setAttribute('Date',str(date))
        # Now append the new Child        
        root.appendChild(new_entry)
        self.update_Id_node_dictionary()
            
    def update_Id_node_dictionary(self):
        """ Re-creates the attribute self.Id_node_dictionary, using the current
        definition of self.document"""
        self.Id_node_dictionary=dict([(str(node.getAttribute('Id')),
        node) for node in \
        self.document.getElementsByTagName('Entry')])
    # if the XSLT engine loaded then define a transformation to HTML    
    if XSLT_CAPABLE:
        def to_HTML(self,XSLT=DEFAULT_LOG_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml())) 
            return HTML
        def current_entry_to_HTML(self,XSLT=DEFAULT_LOG_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            
            current_entry_XML=self.Id_node_dictionary[self.current_entry['Id']]
            HTML=XSL_transform(etree.XML(current_entry_XML.toxml())) 
            return HTML         
    
    # TODO: Make show and display function work well
    def previous_entry(self):
        """Sets current entry to the one before"""
        if len(self.current_entry)>0:
            Id=int(self.current_entry['Id'])
        else:
            return
        new_Id=Id-1
        try:
            self.set_current_entry(new_Id)
        except KeyError:
            Ids=map(lambda x:int(x),self.Id_node_dictionary.keys()) 
            if min(Ids)<Id:
               Ids.sort()
               new_Id=Ids[Ids.index(Id)-1]
            else:
                Ids.remove(Id)
                if len(Ids)>0:
                    new_Id=max(Ids)
                else:
                    new_Id=Id
        self.set_current_entry(new_Id)
   
    def next_entry(self):
        """Sets current entry to the one after"""
        if len(self.current_entry)>0:
            Id=int(self.current_entry['Id'])
        else:
            return
        new_Id=Id+1
        try:
            self.set_current_entry(new_Id)
        except KeyError:
            Ids=map(lambda x:int(x),self.Id_node_dictionary.keys()) 
            if max(Ids)>Id:
               Ids.sort()
               new_Id=Ids[Ids.index(Id)+1]
            else:
                Ids.remove(Id)
                new_Id=min(Ids)
        self.set_current_entry(new_Id)
        
               
    def show(self,mode='text'):
        """ Displays a Log either as formatted text in the command line or in a 
        window (using wx)"""
        def tag_to_tagName(tag):
            tagName=tag.replace('<','')
            tagName=tagName.replace('/','')
            tagName=tagName.replace('>','')
            return tagName
        if mode in ['text','txt','cmd line','cmd']:
            for node in self.document.getElementsByTagName('Entry'):
                print 'Entry Id: %s \tDate: %s'%(node.getAttribute('Id'),
                node.getAttribute('Date'))
                print node.firstChild.nodeValue
        elif re.search('xml',mode,re.IGNORECASE):
            for node in self.document.getElementsByTagName('Entry'):
                print node.toprettyxml()
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
        """Controls the behavior of the Log if a string function is called"""
        return self.document.toxml()
    def __add__(object,right):
        """Controls Behavior of two Logs added using the + operator"""
        new_log=object
        for entry in right.document.getElementsByTagName('Entry'):
            if entry.getAttribute('Id')=='-1':
                pass    
            else:
                new_log.add_entry(entry)
        return new_log
    
class ChangeLog(Log):
    """ A Log for storing changes to a program"""
    def __init__(self,path=None,program_name=None):
        Log.__init__(self,path)
        # set the description element if it is a new log
        if path is None:
            self.add_ChangeLog_description(program_name)
            
    def add_ChangeLog_description(self,program_name=None):
        """ Adds a description of the change log as element Id=-1"""
        if program_name is None:
            program_name='a program'
        description="""This is a change log for %s. It consists of entries with
        a date attribute, an Id attribute that is a simple integer, and text 
        describing the changes made to %s."""%(program_name,program_name)
        self.add_description(description)
        
        
#TODO: add aditional functions to the subclasses                         
class EndOfDayLog(Log):
    """ A Log for storing notes about daily activities"""
    def __init__(self,path=None):
        Log.__init__(self,path,**{'style_sheet':DEFAULT_END_OF_DAY_LOG_XSL})
        if path is None:
            self.add_EndOfDayLog_description()
        self.information_tags=['Actions','Who_Did','Who_Suggested','Why','Conclusion','Data_Location']
    def add_entry_information(self,Id=None,**entry):
        """ Adds a log specific entry takes a dicitionary in the form 
        {'tag':value,..} this does not add atributes"""
        if Id is None:
            self.add_entry()
            Id=self.current_entry['Id']
            
        try:
            node=self.get_entry(Id)
        except:
            raise
        for tag,value in entry.iteritems():
            new_element=self.document.createElement(tag)
            new_text=self.document.createTextNode(str(value))
            new_element.appendChild(new_text)
            node.appendChild(new_element)
    def add_EndOfDayLog_description(self,program_name=None):
        """ Adds a description of the log as element Id=-1"""
        description="""This is a End of day log. It consists of entries with
        a date attribute, an Id attribute that is a simple integer, and xml tags 
        describing daily activities""" 
        self.add_description(description)
    
class ErrorLog(Log):
    """ A Log for storring errors generated by a program """
    def __init__(self,path=None):
        Log.__init__(self,path) 
        
class ServiceLog(Log):
    """ A Log for servicing an instrument or experiment """
    def __init__(self,path=None,instrument_name=None):
        Log.__init__(self,path)     

#-------------------------------------------------------------------------------
# Module Scripts
def test_module():
    print('Creating New Log..\n')
    new_log=Log()
    print('Log Contents Upon Creation: using print new_log')
    print(new_log)
    print('\n')
    print('The New Log\'s path is %s'%new_log.path)
    print('Add an entry using new_log.add_entry("This is a test")')
    new_log.add_entry("This is a test")
    print('Log Contents: using print new_log')
    new_log.save()
    print(new_log)

def test_log_addition():
    """ Script to develop test the __add__ attribute for the class Log"""
    # First we want to know how a copy works
    import time
    log_1=Log()
    log_1.add_entry("I am Log Number One")
    time.sleep(.3)
    log_2=Log()
    log_2.add_entry("I am Log Number 2")
    print('Log_1 Contents: using print')
    print log_1
    print('Log_2 Contents: using print')
    print log_2
    print('Log_1+Log_2 Contents: using print')
    print log_1+log_2   
def test_EndOfDayLog():
    """ Script to test that daily logs work properly"""
    print('Creating New Log..\n')
    new_log=EndOfDayLog()
    print('Log Contents Upon Creation: using print new_log')
    print(new_log)
    print('\n')
    print('The New Log\'s path is %s'%new_log.path)
    print('Add an entry using new_log.add_entry("This is a test")')
    new_log.add_entry("This is a test")
    print('Add an entry using new_log.add_entry_information(1,dictionary)')
    dictionary={'Actions':'I tested EndofDayLog()','Who_Did':'Aric Sanders'
    ,'Who_Suggested':'Small Green Man','Why':'To make sure it works!',
    'Conclusion':'It Does!','Data_Location':'In front of your face'}
    new_log.add_entry_information(0,**dictionary)
    print('Log Contents: using print new_log')
    new_log.save()
    print(new_log)    
    #new_log.show('wx')
def test_show():
    new_log=Log()
    print 'New Log Created...'
    print 'The Result of Show() is:'
    print '*'*80
    entries=['1','2','Now I see!', 'Today was a good day']
    for entry in entries:
        new_log.add_entry(entry)
    print new_log.show()    
    print '\n'*4
    print 'The Result of Log.show(xml) is:'
    print '*'*80 
    print new_log.show('xml')
    
    #the window version
    new_log.show('wx')
    
    
    
def help(format='txt'):
    structure_info=""" Logs are an XML file with the root element of
    <Log>. The first child elements of Log are always 
    <Entry Date='DATE_OF_ENTRY' Id='NUMBER_OF_ENTRY'>. The entry element can 
    contain anything and this is where classes inherting from Log differ."""
def test_to_HTML():
    new_log=Log()
    print 'New Log Created...'
    print 'The Result of Show() is:'
    print '*'*80
    entries=['1','2','Now I see!', 'Today was a good day']
    for entry in entries:
        new_log.add_entry(entry)
    print new_log.show()    
    print '\n'*4
    print 'The Result of Log.to_HTML(xml) is:'
    print '*'*80 
    print new_log.to_HTML()
#-------------------------------------------------------------------------------
# Module Runner

if __name__ == '__main__':
    #test_EndOfDayLog()
    #test_show()
    test_to_HTML()