#-----------------------------------------------------------------------------
# Name:        States.py
# Purpose:     To handle state data for experiments and instruments
#
# Author:      Aric Sanders
#
# Created:     2009/09/22
# RCS-ID:      $Id: States.py $
# Copyright:   --None--
# Licence:     --None--
#-----------------------------------------------------------------------------
""" The module States defines classes and functions for manipulating State data 
from instruments and experiments """

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
try:
    
    import pyMeasure.Code.Misc.Names 
except:
    print 'The import of pyMeasure.Code.Misc.Names failed in the module States.'
    pass
#-------------------------------------------------------------------------------
# Module Constants
INSTRUMENT_TYPES=['GPIB','COMM','OCEAN_OPTICS','MIGHTEX','LABJACK']
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))
DEFAULT_STATE_XSL=os.path.join(PYMEASURE_ROOT,'Data/States',
'DEFAULT_STATE_STYLE.XSL').replace('\\','/')
#-------------------------------------------------------------------------------
# Class Definitions
class State():
    """ A State is a XML file with experimental setting information"""
    def __init__(self,file_path=None,specific_descriptor=None):
        """Initalizes the State class"""
        #if the file path is not supplied create a new State
        self.general_descriptor='State'
        
        if not specific_descriptor is None:
            self.specific_descriptor=specific_descriptor
        else:
            self.specific_descriptor='New'
        if file_path is None:
            impl=getDOMImplementation()
            self.document=impl.createDocument(None,\
            '%s_%s'%(self.specific_descriptor,self.general_descriptor),None)
            new_node=self.document.createProcessingInstruction(\
            'xml-stylesheet',\
            u'type="text/xsl" href="%s"'%DEFAULT_STATE_XSL)
            self.document.insertBefore(new_node,self.document.documentElement)
            
            state_directory=os.path.join(PYMEASURE_ROOT,'Data','States').replace('\\','/')
           
            self.name=pyMeasure.Code.Misc.names.auto_name(
            self.specific_descriptor,self.general_descriptor,state_directory)
            
            self.path=os.path.join(state_directory,self.name).replace('\\','/')

        else:
            file_in=open(file_path,'r')
            self.document=xml.dom.minidom.parse(file_in)
            file_in.close()
            self.path=file_path
            

            
        # Define Method Aliases if they are available
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)     

        
    def save(self,path=None):
        """ Saves the state as an XML file"""
        if path is None:
            path=self.path
        file_out=open(path,'w')
        file_out.write(self.document.toprettyxml())
        file_out.close()
    # if the XSLT engine loaded then define a transformation to HTML    
    if XSLT_CAPABLE:
        def to_HTML(self,XSLT=DEFAULT_STATE_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml())) 
            return HTML  
    def __str__(self):
        """Controls the behavior of the State if a string function is called"""
        return self.document.toxml()
            
class InstrumentState(State):
    """ An instrument state is an XML file with instrument setting information"""
    def __init__(self,file_path=None,date='now',**state_dictionary):
        """ Intialize the InstrumentState class"""
        
        State.__init__(self,file_path,specific_descriptor='Instrument')
        state_node=self.document.createElement('State')
        self.document.documentElement.appendChild(state_node)
        if date in ['now']:
            # Add the Date attribute, this is the time when the state was created
            date=datetime.datetime.utcnow().isoformat()
            Date_attribute=self.document.createAttribute('Date')
            state_node.setAttributeNode(Date_attribute)
            state_node.setAttribute('Date',str(date))
            
        for key,value in state_dictionary.iteritems():
            new_entry=self.document.createElement('Tuple')
            set_attribute=self.document.createAttribute('Set')
            value_attribute=self.document.createAttribute('Value')
            new_entry.setAttributeNode(set_attribute)
            new_entry.setAttributeNode(value_attribute)
            new_entry.setAttribute('Set',key)
            new_entry.setAttribute('Value',str(value))
            state_node.appendChild(new_entry)
        # this is not the most direct way to define it but it is the most robust I think
        self.state_node=self.document.getElementsByTagName('State')[0]
        self.state_dictionary=dict([(str(node.getAttribute('Set')),
        node.getAttribute('Value')) for node in \
        self.state_node.getElementsByTagName('Tuple')])
    
    def add_state_description(self,description):
        """Adds the tag named State_Description and its information"""
        try:    
            new_element=''
            if type(description) is DictionaryType:
                for key,value in description.iteritems():
                    # This hanldes Tag:Text dictionaries
                    if re.search('Description',key):
                        new_element=self.document.createElement(key)
                        for tag,element_text in value.iteritems(): 
                            new_tag=self.document.createElement(tag)
                            new_text=self.document.createTextNode(element_text)
                            new_tag.appendChild(new_text)
                            new_element.appendChild(new_tag)
            elif type(description) is StringType:
                new_element=self.document.createElement('State_Description')
                new_text=self.document.createTextNode(str(description))
                new_element.appendChild(new_text)
            elif type(description) is InstanceType:
                new_element=description
            #first_child=self.document.documentElement.firstChild
            
            self.document.documentElement.insertBefore(new_element,self.document.documentElement.childNodes[0])                                  
        except:
            raise
class ExperimentState(State):
    """ An ExperimentState is a xml file with experiment setting information"""
    def __init__(self):
        """ Intialize the state class"""
        pass



#-------------------------------------------------------------------------------
# Module Scripts
def test_State():
    """ Tests the State Class"""
    new_state=State(specific_descriptor='TEST')
    print 'The new states path is %s'%new_state.path
    print new_state
    new_state.save()
    print '1'
def test_InstrumentState():
    """ Tests the InstrumentState Class"""
    new_state=InstrumentState(**{'test_command':1,'test_command2':2})
    print 'The new states path is %s'%new_state.path
    print new_state
    print '2'
    new_state.save()
def test_add_state_description():
    """ Tests adding instrument state descriptions in different ways"""
    print '3'
    
    pass

#-------------------------------------------------------------------------------
# Module Runner

if __name__ == '__main__':
    #test_State()
    test_InstrumentState()