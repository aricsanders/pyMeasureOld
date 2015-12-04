#-----------------------------------------------------------------------------
# Name:        Measurements.py
# Purpose:     Module that defines functions and classes to
#              hold and manipulate measured data
#
# Author:      Aric Sanders
#
# Created:     2009/09/22
# RCS-ID:      $Id: Measurements.py $
# Copyright:   --None--
# Licence:     --None--
#-----------------------------------------------------------------------------
""" Measurements is a module that defines functions and classes to hold and 
manipulate measured data."""

#-------------------------------------------------------------------------------
# Standard Imports
import os                                          # path functions etc. 
import sys                                         # System
import re                                          # For regular expressions
import urlparse                                    # To form proper URLs
import datetime                                    # For timestamping
import xml.dom                                     # Xml document handling
import xml.dom.minidom                             # For xml parsing
from xml.dom.minidom import getDOMImplementation   # Making blank XML documents 
#from xml.dom.ext import PrettyPrint               # Printing XML without spaces-Needs to be removed is not in 2.6
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
    print("The module pyMeasure.Code.Misc.Names was not found")
    pass
#-------------------------------------------------------------------------------
# Module Constants
INSTRUMENT_TYPES=['GPIB','COMM','OCEAN_OPTICS','MIGHTEX','LABJACK']
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))
MEASUREMENTS_DIRECTORY=os.path.join(PYMEASURE_ROOT,'Data','Measurements').replace('\\','/')
DEFAULT_STATE_XSL=os.path.join(PYMEASURE_ROOT,'Data/States',
'DEFAULT_STATE_STYLE.XSL').replace('\\','/')
DEFAULT_MEASUREMENT_XSL='DEFAULT_MEASUREMENT_STYLE.XSL'




#-------------------------------------------------------------------------------
# Class Definitions
class GeneralDataNode():
    """ This is a container for data with an XML translation"""
    pass
class DataTable():
    """ This is a XML data table class with an optional description"""
    def __init__(self,file_path=None,*data_table,**data_dictionary):
        """ Intializes the DataTable Class."""
        # the general idea is <Data_Description/><Data><Tuple i=''/></Data>
        
        self.specific_descriptor='Data'
        self.general_descriptor='Table'        
        if file_path is None:
            impl=getDOMImplementation()
            self.document=impl.createDocument(None,\
            '%s_%s'%(self.specific_descriptor,self.general_descriptor),None)
            new_node=self.document.createProcessingInstruction(\
            'xml-stylesheet',\
            u'type="text/xsl" href="%s"'%DEFAULT_MEASUREMENT_XSL)
            self.document.insertBefore(new_node,self.document.documentElement)
            self.name=pyMeasure.Code.Misc.Names.auto_name(
            self.specific_descriptor,self.general_descriptor,
            MEASUREMENTS_DIRECTORY)
            self.path=os.path.join(MEASUREMENTS_DIRECTORY,self.name).replace('\\','/')
        # Need a default name to save to 
        else:
            file_in=open(file_path,'r')
            self.document=xml.dom.minidom.parse(file_in)
            file_in.close()
            self.path=file_path 
            
 #
        try:
            if len(data_table)>0:
                data_node=self.list_to_XML(data_table)
                self.document.documentElement.appendChild(data_node)
        except: pass
        try:    
            if len(data_dictionary)>0:
                for key,value in data_dictionary.iteritems():
                    # This hanldes Tag:Text dictionaries
                    if re.search('Description',key):
                        new_entry=self.document.createElement(key)
                        for tag,element_text in value.iteritems():
                            new_tag=self.document.createElement(tag)
                            new_text=self.document.createTextNode(element_text)
                            new_tag.appendChild(new_text)
                            new_entry.appendChild(new_tag)
                        self.document.documentElement.appendChild(new_entry)
                    if re.search('Data',key) and not re.search('Description',key):
                        new_entry=self.list_to_XML(value)
                        self.document.documentElement.appendChild(new_entry)               
        except:
            raise
                    
             
    # Define Method Aliases if they are available
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)     
                
    # I think this would be better as a function, but you need a document.
    def list_to_XML(self,data_list):
        """ Converts a list to XML document"""
        data_node=self.document.createElement('Data')
        #self.document.documentElement.appendChild(data_node)
        for row in data_list:
            if type(row) in [ListType,TupleType]:   
                new_entry=self.document.createElement('Tuple')
                for j,datum in enumerate(row):
                    x_attribute=self.document.createAttribute('X%s'%j)
                    new_entry.setAttributeNode(x_attribute)
                    new_entry.setAttribute('X%s'%j,str(datum))
                data_node.appendChild(new_entry)
            elif type(row) is DictionaryType:
                new_entry=self.document.createElement('Tuple')
                for key,datum in row.iteritems():
                    x_attribute=self.document.createAttribute(key)
                    new_entry.setAttributeNode(x_attribute)
                    new_entry.setAttribute(key,str(datum))
                data_node.appendChild(new_entry)
                 
        return data_node
    def get_attribute_names(self):
        """ Returns the attribute names in the first tuple element in the 'data' element """ 
        attribute_names=[]
        data_nodes=self.document.getElementsByTagName('Data')
        first_tuple_node=data_nodes[0].childNodes[1]
        text=first_tuple_node.toprettyxml()
        text_list=text.split(' ')
        #print text_list
        for item in text_list:
            try:
                match=re.search('(?P<attribute_name>\w+)=',item)
                name=match.group('attribute_name')
                #print name
                attribute_names.append(name)
            except:pass 
        
        return attribute_names
        
    def save(self,path=None):
        """ Saves the state as an XML file"""
        if path is None:
            path=self.path
        file_out=open(path,'w')
        file_out.write(self.document.toprettyxml())
        file_out.close()
    def to_list(self,attribute_name):
        """ Outputs the data as a list given a data column (attribute) name"""
        try:
            node_list=self.document.getElementsByTagName('Tuple')
            data_list=[node.getAttribute(attribute_name) for node in node_list]
            return data_list
        except:
            return None
    def to_tuple_list(self,attribute_names):
        """ Returns a list of tuples for the specfied list of attribute names"""
        try:
            node_list=self.document.getElementsByTagName('Tuple')
            data_list=[tuple([node.getAttribute(attribute_name) for 
            attribute_name in attribute_names]) for node in node_list]
            return data_list
        except:
            return None            
    def get_header(self,style='txt'):
        """ Creates a header from the data description if there is one"""
        try:
            node_list=self.document.getElementsByTagName('Data_Description')
            data_description=node_list[0]
            out=''
            if style in ['txt','text','ascii']:
                for child in data_description.childNodes:
                    try:
                        out=out+'%s: %s'%(child.nodeName,child.firstChild.nodeValue)+'\n'
                    except:pass
                return out
            elif re.search('xml',style,flags=re.IGNORECASE):
                out=data_description.toprettyxml()
                return out
            print dir(data_description)
            PrettyPrint(node_list[0],sys.stdout)
        except:
            raise
    # if the XSLT engine loaded then define a transformation to HTML    
    if XSLT_CAPABLE:
        def to_HTML(self,XSLT=DEFAULT_MEASUREMENT_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml())) 
            return HTML   
    def __str__(self):
        """Controls the behavior of the State if a string function is called"""
        return self.document.toxml()
    
class SpectralData(DataTable):
    """Special data container for spectra"""
    def __init__(self,*data_table,**data_dictionary):
        """ Intializes the class for spectra data table should be in the format 
        [(wavelength,intensity),...]"""
        if len(data_table)>0:
            self.data_dictionary=[{'Wavelength':wavelength,'Intensity':intensity} 
            for wavelength,intensity in data_table]
            self.data_table_dictionary={'Data_Description':{'Wavelength':'Wavelength in nm',
            'Intensity':'Intensity in Arbitrary Units'},'Data':self.data_dictionary}
        else:
            self.data_table_dictionary=data_dictionary
        DataTable.__init__(self,**self.data_table_dictionary)
class IVData(DataTable):
    """ Specific Data Model for Current Voltage Data """
    def __init__(self):
        pass
        
#-------------------------------------------------------------------------------
# Module Scripts

def test_DataTable():
    """ Test's the DataTable Class"""
    test_data=[tuple([2*i+j for i in range(3)]) for j in range(5)]
    new_table=DataTable(None,*test_data)
    print new_table
    test_dictionary={'Data_Description':{'x':'X Distance in microns.',
    'y':'y Distance in microns.','Notes':'This data is fake'},'Data':[[1,2],[2,3]]}
    test_dictionary_2={'Data_Description':{'x':'x Distance in microns.',
    'y':'y Distance in microns.'},'Data':[{'x':1,'y':2},{'x':2,'y':3}]}
    new_table_2=DataTable(**test_dictionary)
    new_table_3=DataTable(**test_dictionary_2)
    print new_table_2
    print new_table_3
    print new_table_3.to_list('x')
    print new_table_3.to_tuple_list(['x','y'])
    print new_table_3.path
    new_table_3.get_header()
    #new_table_2.save()   
    
def test_get_header():
    """ Test of the get header function """
    test_dictionary={'Data_Description':{'x':'X Distance in microns.',
    'y':'y Distance in microns.','Notes':'This data is fake'},'Data':[[1,2],[2,3]]}
    new_table=DataTable(**test_dictionary)
    header=new_table.get_header()
    print header
    print new_table.get_header('xml')
def test_open_measurement(sheet_name='Data_Table_021711_22.xml'):
    """Tests opening a sheet"""
    path=os.path.join(MEASUREMENTS_DIRECTORY,sheet_name)
    measurement=DataTable(file_path=path)
    #print measurement
    print measurement.get_header()
def test_get_attribute_names(sheet_name='Data_Table_021711_22.xml'):
    path=os.path.join(MEASUREMENTS_DIRECTORY,sheet_name)
    measurement=DataTable(file_path=path)
    names=measurement.get_attribute_names()
    print 'the names list is:',names 
    print 'Using the names list to create a data table:'
    print '*'*80+'\n'+'%s   %s  %s'%(names[0], names[1], names[2])+'\n'+'*'*80
    for index,item in enumerate(measurement.to_list(names[0])):
        row=''
        for name in names:
            row=measurement.to_list(name)[index] +'\t'+row
        print row
    
#-------------------------------------------------------------------------------
# Module Runner

if __name__ == '__main__':
    #test_open_measurement()
    #Stest_get_attribute_names()
    test_DataTable()