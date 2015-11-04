#-----------------------------------------------------------------------------
# Name:        Instruments.py
# Purpose:     To Handle the Instrument Data type
#
# Author:      Aric Sanders
#
# Created:     2009/10/27
# RCS-ID:      $Id: Instruments.py $
#-----------------------------------------------------------------------------
""" Data types and functions to handle instrument xml data sheets """

#TODO: Change the name of this module to InstrumentInformation?
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
INSTRUMENT_TYPES=['GPIB','COMM','OCEAN_OPTICS','MIGHTEX','LABJACK']
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))
INSTRUMENT_SHEETS=fnmatch.filter(os.listdir(os.path.join(
PYMEASURE_ROOT,'Instruments')),'*.xml')
NODE_TYPE_DICTIONARY={'ELEMENT_NODE':1, 'ATTRIBUTE_NODE':2, 'TEXT_NODE':3, \
'CDATA_SECTION_NODE':4,'ENTITY_NODE':6, 'PROCESSING_INSTRUCTION_NODE':7, \
'COMMENT_NODE':8,'DOCUMENT_NODE':9,'DOCUMENT_TYPE_NODE':10,\
'NOTATION_NODE':12}
DEFAULT_INSTRUMENT_XSL=os.path.join(PYMEASURE_ROOT,'Instruments',
'DEFAULT_INSTRUMENT_STYLE.xsl').replace('\\','/')
#-------------------------------------------------------------------------------
# Module Functions
def get_XML_text(tag_name,path=None,text=None):
    """ Returns the text in the first tag found with tag name """
    if text is None:
        f=open(path,'r')
        text=f.read()
    tag_match=re.search(
    '<%s>(?P<XML_text>\w+)</%s>'%(tag_name,tag_name),
     text)
    return tag_match.group('XML_text')
      
def determine_instrument_type_from_string(string):
    """ Given a string returns the instrument type"""

    if type(string) in StringTypes:
         # Start with the easy ones
         for instrument_type in INSTRUMENT_TYPES:
            match= re.compile(instrument_type,re.IGNORECASE)
            if re.search(match,string):
                return instrument_type
         # Now read in all the Instrument sheets and look for a match
         # Returning the Name in the Instrument_Type Tag
         instrument_folder=os.path.join(PYMEASURE_ROOT,'Instruments')
         for instrument_sheet in os.listdir(instrument_folder):
             path=os.path.join(PYMEASURE_ROOT,'Instruments',instrument_sheet)
             if os.path.isfile(path):
                f=open(path,'r')
                text=f.read()
                if re.search(string,text):
                    tag_match=re.search(
                    '<Instrument_Type>(?P<instrument_type>\w+)</Instrument_Type>',
                    text)
                    try:
                        return tag_match.group('instrument_type')
                    except:pass
    else:
        return None

def determine_instrument_type(object):
    """Tries to return an instrument type given an address, name, serial #
     or class instance"""
    # attributes that normally have the type hidden in there
    # should be in the order of likelyhood 
    attritbute_names=['instrument_type','address','serial','Id'] 
    # Check to see if it is a string and then go through the possibilities
    if type(object) in StringTypes:
        return determine_instrument_type_from_string(object)
    # If it is a object or class look around in normal names looking for a string
    # to process
    elif type(object)==InstanceType or ClassType:
        for attribute in attritbute_names:
            try:
                if attribute in dir(object):
                    string=eval('object.%s'%attribute)
                    answer=determine_instrument_type_from_string(string)
                    if answer is None:pass
                    else: return answer 
            except AttributeError:        
                try:
                    string=object.__class__.__name__
                    return determine_instrument_type_from_string(string)
                except: pass     
#-------------------------------------------------------------------------------
# Class Definitions


class InstrumentSheet():
    """ Class that handles the xml instrument sheet"""
    def __init__(self,file_path=None,instrument_name=None):
        """ Intializes the InstrumentSheet Class"""
        #if the file path is not supplied create a new instrument sheet
        #using the supplied instrument_name
        if file_path is None:
            implementation=getDOMImplementation()
            self.document=implementation.createDocument(None,\
            'Log',None)
            new_node=self.document.createProcessingInstruction(\
            'xml-stylesheet',\
            u'type="text/xsl" href="%s"'%DEFAULT_INSTRUMENT_XSL)
            self.document.insertBefore(new_node,self.document.documentElement)
            self.path=os.path.join(PYMEASURE_ROOT,'Instruments',
            'instrument_name'+'.xml').replace('\\','/')
        else:
            file_in=open(file_path,'r')
            self.document=xml.dom.minidom.parse(file_in)
            file_in.close()
            self.path=file_path 
        self.document=xml.dom.minidom.parse(file_path)
        self.root=self.document.documentElement
        # Now use the xml to declare some attributes
        specific_description=self.document.getElementsByTagName('Specific_Information')
        for information_node in specific_description:
            if information_node.nodeType is NODE_TYPE_DICTIONARY['ELEMENT_NODE']:
                for node in information_node.childNodes:
                    if node.nodeType is NODE_TYPE_DICTIONARY['ELEMENT_NODE']:
                        if node.childNodes:
                            tag_name=node.tagName
                            text_value=node.childNodes[0].data
                            if not text_value in [None,'']:
                                string='self.%s="%s"'%(tag_name.lower(),text_value)
                                #print string
                                exec('%s'%string)
         #Commands
        self.commands=[]
        commands=self.document.getElementsByTagName('Commands')[0]
        for command in commands.childNodes:
            if command.nodeType is NODE_TYPE_DICTIONARY['ELEMENT_NODE']:
                self.commands.append(command.getAttribute('Command'))
        # Define Method Aliases if they are available
        if METHOD_ALIASES:
            #print 'True'
            for command in alias(self):
                exec(command)
        try:
            self.image=self.get_image_path()
        except:
            pass
        
    ##TODO: Add a edit entry method                            
    def add_entry(self,tag_name,text=None,description='Specific',**attribute_dictionary):
        """ Adds an entry to the instrument sheet."""
        specific_match=re.complie('Specific',re.IGNORECASE)
        general_match=re.complie('General',re.IGNORECASE)
        if re.search(specific_match,description):
            description_node=self.document.getElementsByTagName('Specific_Information')[0]
        elif re.search(general_match,description):
            description_node=self.document.getElementsByTagName('General_Information')[0]
        new_entry=self.document.createElement(tag_name)
        if not text is None:
            text_node=self.document.createTextNode(tag_name)
            new_entry.appendChild(text_node)
        for key,value in attribute_dictionary.iteritems():
            new_attribute=self.document.creatAttribute(key)
            new_entry.setAttributeNode(new_attribute)
            new_entry.setAttribute(key,str(value))  
        description_node.appendChild(new_entry)
        
    def get_query_dictionary(self):
        """ Returns a set:query dictionary if there is a State_Commands element"""
        try:
            state_commands=self.document.getElementsByTagName('State_Commands')[0]
            state_query_dictionary=dict([(str(node.getAttribute('Set')
            ),str(node.getAttribute('Query')))
            for node in state_commands.childNodes if node.nodeType is \
            NODE_TYPE_DICTIONARY['ELEMENT_NODE']])
            return state_query_dictionary
        except:
            raise
            #return None
    def get_image_path(self):
        """Tries to return the image path, requires image to be in
        <Image href="http://132.163.53.152:8080/home_media/img/Fischione_1040.jpg"/> format"""
        # Take the first thing called Image
        image_node=self.document.getElementsByTagName('Image')[0]
        image_path=image_node.getAttribute('href')
        return image_path
    
        
           
    def save(self,path=None):
        """" Saves the instrument sheet as an XML file."""
        if path is None:
            path=self.path
        file_out=open(path,'w')
        file_out.write(self.document.toprettyxml())
        file_out.close()
        
    if XSLT_CAPABLE:
        def to_HTML(self,XSLT=DEFAULT_INSTRUMENT_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml())) 
            return HTML                     
#-------------------------------------------------------------------------------
# Module Scripts
def test_InstrumentSheet():
    """ A test of the InstrumentSheet class"""
    instrument_sheet=InstrumentSheet(os.path.join(PYMEASURE_ROOT,'Instruments',INSTRUMENT_SHEETS[0]))
    tags=instrument_sheet.document.getElementsByTagName('Instrument_Type')
    value=[node.childNodes[0].data for node in tags]
    print value
    print dir(instrument_sheet)
    print instrument_sheet.get_image_path()
    print instrument_sheet.commands
    print str(instrument_sheet.to_HTML())
#-------------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    test_InstrumentSheet()
    
