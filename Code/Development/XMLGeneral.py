#-----------------------------------------------------------------------------
# Name:        XMLGeneral.py
# Purpose:    To handle general XML tasks such as editing 
#
# Author:      Aric Sanders
#
# Created:     2011/12/31
# RCS-ID:      $Id: XMLGeneral.py $

#-----------------------------------------------------------------------------
"""XMLGeneral handles general XML document tasks and is meant to be a DataHandler for 
the General XML editing FrontEnds"""

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
import StringIO
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
    from pyMeasure.Code.Utils.Alias import *
    METHOD_ALIASES=1
except:
    print("The module pyMeasure.Code.Utils.Alias was not found")
    METHOD_ALIASES=0
    pass
#-------------------------------------------------------------------------------
# Constants
TESTS_DIRECTORY=os.path.join(os.path.dirname(os.path.realpath(__file__)),'Tests')

#-------------------------------------------------------------------------------
# Classes

class EtreeXML():
    """ Class that uses the lxml etree functions to parse xml data,it should 
    be noted not all html is well formed xml"""
    def __init__(self,xml_document=None):
        """ Intializes the EtreeXML Class can be called with a XML string or file name"""
        if os.path.isfile(xml_document):
            try:
                self.document=etree.parse(xml_document)
                self.path=xml_document.replace("\\","/")
            except:
                raise
        else:
            try:
                print("There is no path, set it to save file.")
                print("etree considers this a element")
                self.document=etree.parse(StringIO.StringIO(xml_document))
                self.path=''
            except:raise
        self.info=[]
        self.root=self.document.getroot()
        self.processing_instructions=map(lambda x:str(x),self.get_processing_instructions())
        # Try to load the XSL from the sheet itself
        for instruction in self.get_processing_instructions():
            try:
                self.xsl=instruction.parseXSL()
            except:
                pass
        self.create_node_dictionary()
    def create_node_dictionary(self):
        """Creates a node dictionary so you can find nodes later"""
        self.node_dictionary={}
        node_iterator=0
        for node in self.document.iter():
            self.node_dictionary[node_iterator]=node
            node_iterator+=1
        
    def get_processing_instructions(self):
        """ Returns material before the root element"""
        output=[]
        preamble=self.root
        while preamble is not None:
            if isinstance(preamble,etree._XSLTProcessingInstruction):
                output.append(preamble)
            preamble=preamble.getprevious()
        return output
    def to_HTML(self,XSLT=None):
        """ Returns HTML string by applying a XSL to the XML document"""
        if XSLT is not None:
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml())) 
        else:
            try:
                XSL_data=self.xsl
                XSL_transform=etree.XSLT(XSL_data)
                HTML=XSL_transform(self.document) 
                return HTML
            except:
                raise
    def to_editable_HTML(self):
        """ Creates a html sheet with links back to each node"""
        # my only problem is that the node dictionary is flat can we do this 
        # in a tree??
        pass
    def save(self,path=None):
        """ saves the file"""
        if path is None:
            path=self.path
        file_out=open(path,'w')
        file_out.write(str(self))
        file_out.close()
        
    def __str__(self):
        """ Defines how EtreeXML is displayed """
        return etree.tostring(self.document, pretty_print=True)
#-------------------------------------------------------------------------------
# Scripts
def test_EtreeXML():
    """ Tests the EtreeXML Class"""
    os.chdir(TESTS_DIRECTORY)
    new_xml=EtreeXML(open('SRS830_Lockin1.xml','r'))
    #print etree.tostring(new_xml.document)
    root_element=new_xml.document.getroot()
    
    #print new_xml.get_processing_instructions()
    #print etree.tostring(new_xml.xsl)
    #print new_xml.info
    #print root_element
    #print root_element.tag
    #print new_xml #Now that I have define __str__
    #print new_xml.node_dictionary
    for element in new_xml.document.iter():
        
        print("Element name: %s"%element.tag)
        if element.text:
            print("\tElement Text: %s"%element.text)
        if element.attrib:
            attribute_text="Attribues are "
            for key,value in element.attrib.iteritems():
                attribute_text=attribute_text+"%s = %s, "%(key,value)
            print attribute_text
    print("The path is %s"%new_xml.path)
    
#-------------------------------------------------------------------------------
# Module Runner



if __name__ == '__main__':
    test_EtreeXML()
