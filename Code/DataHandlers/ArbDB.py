#-----------------------------------------------------------------------------
# Name:        arbDB.py
# Purpose:     Base Classes For The  
#              Arbitrary Database 
#
# Author:      Aric Sanders
#
# Created:     2009/09/01
# RCS-ID:      $Id: FileRegister.py $
#-----------------------------------------------------------------------------
""" Arbitrary Database are tools for working with a XML database of URLs """

#-------------------------------------------------------------------------------
# Standard Imports-- All in the python standard library


import os                                          # path functions etc. 
import sys                                         # System 
import re                                          # For regular expressions     
import urlparse                                    # To form proper URLs 
import socket                                      # To determine IPs and Hosts 
import datetime                                    # For timestamping     
import xml.dom                                     # Xml document handling 
import xml.dom.minidom                             # For xml parsing
from xml.dom.minidom import getDOMImplementation   # Making blank XML documents
from types import *                                # to allow input testing
#-------------------------------------------------------------------------------
# Third Party Imports
try: 
    import pyMeasure
except:
    print("The topmost pyMeasure folder was not found please make sure that the directory directly above it is on sys.path") 
    raise
try:
    from lxml import etree
    XSLT_CAPABLE=1
except:
    print("Transformations using XSLT are not available please check the lxml module")
    XSLT_CAPABLE=0
    pass
try:
    from pyMeasure.Code.Misc.GetMetadata import *
except:
    print "Can not find the module GetMetadata, please add it to sys.path" 
    print "Anything that uses the functions from GetMetadata will be broken"
    pass
try:
    from pyMeasure.Code.Misc.Alias import *
    METHOD_ALIASES=1
except:
    METHOD_ALIASES=0
    print("Method Aliases will not be available, please check pyMeasure.Code.Misc.Alias")
    pass
#-------------------------------------------------------------------------------
# Module Constants
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))
DEFAULT_FILEREGISTER_XSL='FR_STYLE.xsl'
DEFAULT_METADATA_XSL='METADATA_STYLE.xsl'
DRIVER_FILE_EXTENSIONS=['sys','SYS','drv','DRV']
NODE_TYPE_DICTIONARY={'1':'ELEMENT_NODE', '2':'ATTRIBUTE_NODE', '3':'TEXT_NODE', \
'4':'CDATA_SECTION_NODE', '6':'ENTITY_NODE', '7':'PROCESSING_INSTRUCTION_NODE', \
'8':'COMMENT_NODE','9':'DOCUMENT_NODE','10':'DOCUMENT_TYPE_NODE',\
'12':'NOTATION_NODE'}
#-------------------------------------------------------------------------------
# Module Functions
def URL_to_path(URL,form='string'):
    """Takes an URL and returns a path as form.
    Argument form may be 'string' or 'list'"""
    path=urlparse.urlparse(URL)[2]
    if form in ['string', 'str', 's']:
        return path
    elif form in ['list','ls','li']:
        path_list=path.split('/')
        return path_list
def condition_URL(URL):
    """ Function that makes sure URL's have a / format and assigns host as
    local host if there is not one. Also gives paths a file protocol."""
    parsed_URL=urlparse.urlparse(URL.replace('\\','/'))
    if not (parsed_URL[0] in ['file','http','ftp']):
        parsed_URL=urlparse.urlparse('file:'+URL.replace('\\','/'))
    return str(urlparse.urlunparse(parsed_URL).replace('///','')) 



#-------------------------------------------------------------------------------
# Class Definitions
class FileRegister():
    """ The base class for arbitrary database, which processes the 
    File Register XML File."""

      
    def __init__(self,file_path=None):   
        """ Initializes the File Register Class."""
        
        #Check to see if a file name was supplied
        # if not then open a new blank Document.
        if file_path is None:
            impl=getDOMImplementation()
            self.document=impl.createDocument(None,\
            'File_Registry',None)
            new_node=self.document.createProcessingInstruction(\
            'xml-stylesheet',\
            u'type="text/xsl" href="%s"'%DEFAULT_FILEREGISTER_XSL)
            self.document.insertBefore(new_node,self.document.documentElement)
            self.path='FileRegister'+'.xml'#+str(datetime.datetime.utcnow())
        else:
            file_in=open(file_path,'r')
            self.document=xml.dom.minidom.parse(file_in)
            file_in.close()
            self.path=file_path
            
        self.Id_dictionary=dict([(str(node.getAttribute('URL')),
        str(node.getAttribute('Id'))) for node in \
        self.document.getElementsByTagName('File')])
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)



    def save(self):
        """ Saves the current File Register as XML with no extra whitespaces."""
        file_out=open(self.path,'w')
        file_out.write(self.document.toprettyxml())
        file_out.close()
        
    def create_Id(self,URL):
        """ Creates or returns the existing Id element of a URL"""
        
        
        parsed_URL=urlparse.urlparse(condition_URL(URL))
                
        try: # Look in self.Id_dictionary, if it is not there catch
             # the exception KeyError and generate an Id.
            return self.Id_dictionary[URL.replace('///','')]
            
        except KeyError: 
            # The Id is not in the existing list so start buliding Id.
            # Determine the IP Address of the host in the URL
            if parsed_URL[1] in ['',u'']: #if it is empty assume local host
                IP_address=socket.gethostbyaddr(socket.gethostname())[2][0]
            else:
                IP_address= socket.gethostbyaddr(parsed_URL[1])[2][0]
            
            Id_cache={}
            # We begin with all the entries with the same IP address
            for (key,value) in self.Id_dictionary.iteritems():
                if value.startswith(IP_address):
                        Id_cache[key]=value
            # If the Id_cache is empty then we just assign the number
            temp_Id=IP_address
            path_list=parsed_URL[2].split('/')
            file_extension=path_list[-1].split('.')[-1]
            if len(Id_cache) is 0:
                for index,part in enumerate(path_list):
                    if index<len(path_list)-1:
                        temp_Id=temp_Id+'.'+'11'
                    elif index==len(path_list)-1:
                        if (file_extension in DRIVER_FILE_EXTENSIONS):
                            temp_Id=temp_Id+'.'+'31'
                        elif os.path.isdir(parsed_URL[2]):
                            temp_Id=temp_Id+'.'+'11'
                        else:
                            temp_Id=temp_Id+'.'+'21'
                return temp_Id
            # if it is not empty we have to a little work
            # remove the information about IP address
            place=0
            #print path_list
            while place<=len(path_list):
                
                # If the Id_cache is empty assign the rest of the Id.
               if len(Id_cache) is 0:
                    for index,part in enumerate(path_list[place:]):
                        if index<len(path_list[place:])-1:
                            temp_Id=temp_Id+'.'+'11'
                        elif index==len(path_list[place:])-1:
                            if (file_extension in DRIVER_FILE_EXTENSIONS):
                                temp_Id=temp_Id+'.'+'31'
                            elif os.path.isdir(parsed_URL[2]):
                                temp_Id=temp_Id+'.'+'11'
                            else:
                                temp_Id=temp_Id+'.'+'21'
                    return temp_Id
                     
                # If the Id_cache is not empty
               else:
                    path_cache=dict([(URL,URL_to_path(URL,form='list'))\
                    for URL in Id_cache.keys()])
                    
                    print Id_cache
                    part_cache=dict([(URL,[path_cache[URL][place],
                    Id_cache[URL].split('.')[place+4]])\
                    for URL in Id_cache.keys()])

    
                    
                    parts_list=[part_cache[URL][0]for URL in Id_cache.keys()]
                    
                    node_number=max([int(Id_cache[URL].split('.')[place+4][1:])\
                    for URL in Id_cache.keys()])               
                # If it is the last place
                    if place==len(path_list)-1:
                        new_node_number=node_number+1                       
                        if (file_extension in DRIVER_FILE_EXTENSIONS):
                            new_node_type='3'
                        elif os.path.isdir(parsed_URL[2]):
                            new_node_type='1'
                        else:
                            new_node_type='2'
                        temp_Id=temp_Id+'.'+new_node_type+str(new_node_number)
                        return temp_Id
                # If it is not the last place assume it is a directory
                    else:
                        new_node_type='1'
                        # Check to see if it is already in the FR
                        if path_list[place] in parts_list:
                            for URL in Id_cache.keys():
                                if part_cache[URL][0]==path_list[place]:
                                    new_node=part_cache[URL][1]
                                    
                        # If not add one to node 
                        else:
                            new_node_number=node_number+1                       
                            new_node=new_node_type+str(new_node_number)            
                  
                        temp_Id=temp_Id+'.'+new_node
                        # Update the Id_cache for the next round, and the place 
                        for URL in Id_cache.keys():
                            try:
                                if not part_cache[URL][0]==path_list[place]:
                                    del(Id_cache[URL])
                                
                                Id_cache[URL].split('.')[place+5]
                            except KeyError:
                                pass
                            except IndexError:
                                #print Id_cache,URL
                                del(Id_cache[URL])
                        place=place+1
 
            
        
    def add_entry(self,URL):
        """ Adds an entry to the current File Register """
        URL=condition_URL(URL)
        if URL in self.Id_dictionary.keys():
            print 'Already there'
            return 
            
        # the xml entry is <File Date="" Host="" Type="" Id="" URL=""/>
        File_Registry=self.document.documentElement
        new_entry=self.document.createElement('File')
        # Make all the new attributes
        attributes=['Id','Host','Date','URL','Type']
        new_attributes=dict([(attribute, 
        self.document.createAttribute(attribute)) for attribute in \
        attributes])
        
        # Add the new attributes to the new entry
        for attribute in attributes:
            new_entry.setAttributeNode(new_attributes[attribute])
        
        # Now assign the values
        attribute_values={}
        attribute_values['URL']=URL
        attribute_values['Id']=self.create_Id(URL)
        attribute_values['Date']=datetime.datetime.utcnow().isoformat()
        type_code=attribute_values['Id'].split('.')[-1][0]
        if type_code in ['1',u'1']:
            attribute_values['Type']="Directory"
        elif type_code in ['2',u'2']:
            attribute_values['Type']="Ordinary"
        elif type_code in ['3',u'3']:
            attribute_values['Type']="Driver"
        else:
            attribute_values['Type']="Other"
            
        parsed_URL=urlparse.urlparse(condition_URL(URL))
        if parsed_URL[1] in ['',u'']: #if it is empty assume local host
            attribute_values['Host']=\
            socket.gethostbyaddr(socket.gethostname())[0]
        else:
            attribute_values['Host']= \
            parsed_URL[1]    
        
        # Now set them all in the actual attribute
        for (key,value) in attribute_values.iteritems():
            new_entry.setAttribute(key,value)
        File_Registry.appendChild(new_entry)
        # Finally update the self.Id_dictionary
        # Added boolean switch to speed up adding a lot of entries
        
        self.Id_dictionary=dict([(str(node.getAttribute('URL')),
        str(node.getAttribute('Id'))) for node in \
        self.document.getElementsByTagName('File')])      
    # TODO : Add an input filter that guesses at what you inputed
    
    def add_tree(self,root,**options):
        """ Adds a directory and all sub folders and sub directories, **options
        provides a way to {'ignore','.pyc|etc'} or {'only','.png|.bmp'}"""
        
        # Deal with the optional parameters, these tend to make life easier
        default_options={'ignore':None,'only':None,'print_ignored_files':True,
        'directories_only':False,'files_only':False}
        tree_options=default_options
        for option,value in options.iteritems():
            tree_options[option]=value
        print tree_options
        #condition the URL
        root_URL=condition_URL(root)
        path=URL_to_path(root_URL)
        # now we add the files and directories that jive with the options
        try:
            
            for (home,directories,files) in os.walk(path):
                #print (home,directories,files)
                for directory in directories:# had to change this 12/2012, used to be first element in list
                    try:
                        if tree_options['files_only']:
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it is not a file"%file                            
                            raise
                        if tree_options['ignore'] is not None and re.search(tree_options['ignore'],directory):
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it does not match the only option"%directory
                            raise
                        elif tree_options['only'] is not None and not re.search(tree_options['only'],directory):
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it does not match the only option"%directory
                            raise
                        else:
                            self.add_entry(condition_URL(os.path.join(home,directory)))
                            self.save()
                    except:pass
                for file in files: # had to change this 12/2012, used to be Second element in list
                    try:
                        if tree_options['directories_only']:
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it is not a directory"%file
                            raise
                        if tree_options['ignore'] is not None and re.search(tree_options['ignore'],file):
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it matches the ignore option"%file
                            raise
                        elif tree_options['only'] is not None and not re.search(tree_options['only'],file):
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it does not match the only option"%file
                            raise
                        else:
                            print (home,file)
                            self.add_entry(condition_URL(os.path.join(home,file)))
                            self.save()
                    except:raise                  
        except:
            raise
                
               
        #After all the files are added update the Id_dictionary
        self.Id_dictionary=dict([(str(node.getAttribute('URL')),
        str(node.getAttribute('Id'))) for node in \
        self.document.getElementsByTagName('File')])              
        
        
    def remove_entry(self,URL=None,Id=None):
        """ Removes an entry in the current File Register """
        File_Registry=self.document.documentElement
        if not URL is None:
            URL=condition_URL(URL)
            URL_FileNode_dictionary=dict([(node.getAttribute('URL'),
            node) for node in self.document.getElementsByTagName('File')])
            File_Registry.removeChild(URL_FileNode_dictionary[URL])
        else:
            Id_FileNode_dictionary=dict([(node.getAttribute('Id'),
            node) for node in self.document.getElementsByTagName('File')])
            File_Registry.removeChild(Id_FileNode_dictionary[Id])
        # Finally update the self.Id_dictionary
        self.Id_dictionary=dict([(str(node.getAttribute('URL')),
        str(node.getAttribute('Id'))) for node in \
        self.document.getElementsByTagName('File')])                  
    if XSLT_CAPABLE:
        def to_HTML(self,XSLT=DEFAULT_FILEREGISTER_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml())) 
            return HTML  
              
    def help(self,style='txt'):
        """ Displays help for the class. """
        help_txt=" The Class FileRegister is a tool for working with the xml\
        File_Registry. "               
        return help_txt
    
    def __str__(self):
        """ Defines the behavior of File Register when string functions are\n
        called"""
        return self.document.toxml()
    
    
class Metadata():
    """ Metadata holds the metadata tags for a FileRegistry, If it already exists
    and the parser gives an error check the xml file for special characters like &#30;"""
    
    def __init__(self,FileRegistry,Metadata_File=None):
        """ Intializes the class Metadata"""
        # Process the file register
        if type(FileRegistry) is InstanceType:
            self.FileRegister=FileRegistry
        elif type(FileRegistry) in StringTypes:
            self.FileRegister=FileRegister(FileRegistry)
        # Process or create the Metdata File
        if Metadata_File is None:
            FileReigster_path=self.FileRegister.path.replace('\\','/')
            FileRegister_name=FileReigster_path.split('/')[-1]
            FileRegister_ext=FileRegister_name.split('.')[-1]
            Metadata_name=FileRegister_name.replace('.'+FileRegister_ext,
            '_Metadata.'+FileRegister_ext)
            self.path=FileReigster_path.replace(FileRegister_name,Metadata_name)
            self.document=self.FileRegister.document
            # delete old processing instructions
            for node in self.document.childNodes:
                if node.nodeType is 7:
                    self.document.removeChild(node)
                    node.unlink()
            # add in the default xsl
            new_node=self.document.createProcessingInstruction(\
            'xml-stylesheet',\
            u'type="text/xsl" href="%s"'%DEFAULT_METADATA_XSL)
            self.document.insertBefore(new_node,self.document.documentElement) 
            # make sure there is a fileregister reference
            FR_Path=self.FileRegister.path
            new_node=self.document.createProcessingInstruction(\
            'xml-FileRegistry',\
            'href=\"%s\"'%(self.FileRegister.path))
            self.document.insertBefore(new_node,self.document.documentElement)  
            
        else:
            if type(Metadata_File) is InstanceType:
                self.document=Metadata_File.document
                self.path=Metadata_File.path
            elif type(Metadata_File) in StringTypes:
                conditioned_URL=condition_URL(Metadata_File)
                file_path=URL_to_path(conditioned_URL)
                file_in=open(file_path,'r')
                try:
                    self.document=xml.dom.minidom.parse(file_in)
                    file_in.close()
                    self.path=file_path
                except xml.parsers.expat.ExpatError:
                    # This occurs because of the chr(30) or RS
                    data=file_in.read()
                    file_in.close()
                    file_out=open(file_path,'w')
                    data.replace(chr(30),'')
                    file_out.write(data)
                    file_out.close()
                    file_in=open(file_path,'r') 
                    self.document=xml.dom.minidom.parse(file_in)
                    file_in.close()
                    self.path=file_path
                                           
          
        # TODO: This dictionary of nodes worries me-- it may not scale well
        self.node_dictionary=dict([(str(node.getAttribute('URL')),
        node) for node in \
        self.document.getElementsByTagName('File')])
        
        self.URL_dictionary=dict([(str(node.getAttribute('Id')),
        str(node.getAttribute('URL'))) for node in \
        self.document.getElementsByTagName('File')])
        
        self.name_dictionary=dict([(Id,os.path.split(self.URL_dictionary[Id])[1])\
        for Id in self.URL_dictionary.keys()])
        
        self.current_node=self.node_dictionary.values()[0]
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)
       
    def save(self):
        """ Saves the current MetaData as XML with no extra whitespaces."""
        file_out=open(self.path,'w')
        file_out.write(self.document.toprettyxml())
        file_out.close()
    def search_name(self,name=None,re_flags=re.IGNORECASE):
        """ Returns a list of URL's that have an element matching name"""
        try:
            if re_flags in [None,'']:
                urls=filter(lambda x: re.search(name,x),
                self.URL_dictionary.values())
                return urls
            else:
                urls=filter(lambda x: re.search(name,x,flags=re_flags),
                self.URL_dictionary.values())
                return urls
               
        except:
            raise    
        
  
    if XSLT_CAPABLE:
        def to_HTML(self,XSLT=DEFAULT_METADATA_XSL):
            """ Returns HTML string by applying a XSL to the XML document"""
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml())) 
            return HTML  
        
    def get_file_node(self,URL=None,Id=None):
        """ Returns the file node specified by URL or Id"""
        if not URL is None:
            URL=condition_URL(URL)
            self.current_node=self.node_dictionary[URL]
            return self.current_node
        elif not Id is None:
            self.current_node=self.node_dictionary[self.URL_dictionary[Id]]
            return self.current_node
    def set_current_node(self,URL=None,Id=None):
        """ Sets the current file node to the one specified by URL or Id"""
        if not URL is None:
            URL=condition_URL(URL)
            self.current_node=self.node_dictionary[URL]  
        elif not Id is None:
            self.current_node=self.node_dictionary[self.URL_dictionary[Id]]
            
    def add_element_to_current_node(self,XML_tag=None,value=None,node=None,**Atributes):
        """Adds a metadata element to the current file node"""
        if node is None:
            new_element=self.document.createElement(XML_tag)
        else:
            new_element=node 
        if not value is None:
            new_text=self.document.createTextNode(str(value))
            new_element.appendChild(new_text)
         
        attributes=[key for key in Atributes.keys()]
        new_attributes=dict([(attribute, 
        self.document.createAttribute(attribute)) for attribute in \
        attributes])
        
        for (key,value) in Atributes.iteritems():
            new_element.setAttribute(key,str(value))
        self.current_node.appendChild(new_element) 
    def remove_element_in_current_node(self,element_name):
        """Removes all metadata elements with the same tagname
         in the current file node"""
        nodes_to_remove=self.current_node.getElementsByTagName(element_name)
        try:
            for node in nodes_to_remove:
                self.current_node.removeChild(node)     
        except:pass
        
    if XSLT_CAPABLE:   
        def current_node_to_HTML(self,XSLT=DEFAULT_METADATA_XSL):
            """Returns a HTML document from the current node"""  
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.current_node.toxml())) 
            return HTML   
        
    def print_current_node(self):
        """ Prints the current node """
        print self.current_node.toxml()
    def __str__(self):
        """ Defines the behavior of File Register when string functions are\n
        called"""
        return self.document.toxml()
#-------------------------------------------------------------------------------
# Script definitions    
def Metadata_robot(file_registry,metadata=None):
    """ This robot checks for system metadata for the files in file_register
    and adds them to metadata without repeats (first removes old data with the 
    same tagname). If no metadata file is given it just writes them to a file in
     the same folder as file_register"""
    
    file_register=FileRegister(file_registry)
    if metadata is None:
        metadata_file=Metadata(file_register,metadata)
    else:
        metadata_file=Metadata(file_register,metadata)
    
    for URL in metadata_file.FileRegister.Id_dictionary.keys():
        try:
            system_metadata=get_system_metadata(URL_to_path(URL))
            metadata_file.get_file_node(URL)
            metadata_file.remove_element_in_current_node('System_Metadata')
            metadata_file.add_element_to_current_node(XML_tag='System_Metadata',**system_metadata)
        except:
            print 'No system metadata for %s'%URL
            pass
        try:
            file_metadata=get_file_metadata(URL_to_path(URL))
        
        
            new_file_info_node=metadata_file.document.createElement('File_Metadata')
            for key,value in file_metadata.iteritems():
                new_node=metadata_file.document.createElement(key)
                new_text=metadata_file.document.createTextNode(str(value))
                new_node.appendChild(new_text)
                new_file_info_node.appendChild(new_node)
            metadata_file.remove_element_in_current_node('File_Metadata')
            metadata_file.add_element_to_current_node(node=new_file_info_node)
            
        except:
            print 'no file data for %s'%URL
            pass
        try: 
            image_metadata=get_image_metadata(URL_to_path(URL))           
            if not image_metadata is None:
                new_image_info_node=metadata_file.document.createElement('Image_Metadata')
                for key,value in image_metadata.iteritems():
                    new_node=metadata_file.document.createElement(key)
                    print key,str(value)
                    print str(value) in ['','&#30;',chr(30)]
                    new_text=metadata_file.document.createTextNode(str(value).replace(chr(30),''))
                    new_node.appendChild(new_text)
                    new_image_info_node.appendChild(new_node)
                metadata_file.remove_element_in_current_node('Image_Metadata')
                metadata_file.add_element_to_current_node(node=new_image_info_node)
                print ' Image data'
        except:
            print 'no image metadata for %s'%URL
            
            pass
        try: 
            python_metadata=get_python_metadata(URL_to_path(URL))
            print python_metadata
            metadata_file.get_file_node(URL)
            metadata_file.remove_element_in_current_node('Python_Docstring')
            metadata_file.add_element_to_current_node(XML_tag='Python_Docstring',
            value=str(python_metadata['Python_Docstring']))
        except:pass
    metadata_file.save()   



def test_to_HTML():
    """ Tests the method FileRegister().to_HTML """
    test_path=\
    os.path.join(PYMEASURE_ROOT,'Settings/Test/test.xml')
    new=FileRegister(test_path)
    print new.to_HTML()
    
def test_Metadata(File_Registry=None,Metadata_File=None):
    #os.chdir(r'C:\Documents and Settings\sandersa\My Documents\Share\ArbDB')
    
    if File_Registry is None:
        File_Registry=os.path.join(PYMEASURE_ROOT,'Settings/Test/test.xml')
    if Metadata_File is None:
        meta_path=os.path.join(PYMEASURE_ROOT,'Settings/Test/test_Metadata.xml')
    new_Metadata=Metadata(File_Registry,meta_path)
    print new_Metadata.current_node
    test_URL,test_Id=new_Metadata.FileRegister.Id_dictionary.items()[1]
    
    print new_Metadata.path
    print new_Metadata.get_file_node(Id=test_Id)
    
    test_get_metadata(new_Metadata.path)
    new_Metadata.print_current_node()
    system_metadata=get_system_metadata(URL_to_path(test_URL))
    try:
        file_metadata=get_file_metadata(URL_to_path(test_URL))
        
        new_file_info_node=new_Metadata.document.createElement('File_Metadata')
        for key,value in file_metadata.iteritems():
            new_node=new_Metadata.document.createElement(key)
            new_text=new_Metadata.document.createTextNode(value)
            new_node.appendChild(new_text)
            new_file_info_node.appendChild(new_node)
        new_Metadata.add_element_to_current_node(node=new_file_info_node)
    except:
        pass
    try:
        image_metadata=get_image_metadata(URL_to_path(test_URL))
        for key,value in image_metadata.iteritems():
            new_Metadata.add_element_to_current_node(key,value)
    except:
        pass
    new_Metadata.add_element_to_current_node(name='System_Metadata',**system_metadata)
    
    new_Metadata.save()
    
def test_adding_metadata_to_all(file_registry=os.path.join(PYMEASURE_ROOT,'Settings/Test/test.xml'),
metadata=os.path.join(PYMEASURE_ROOT,'Settings/Test/test_Metadata.xml') ):
    #File_Registry=r'C:\Documents and Settings\sandersa\My Documents\Share\ArbDB\test.xml'
   #meta_path=r'C:\Documents and Settings\sandersa\My Documents\Share\ArbDB\test_Metadata.xml' 
    #os.chdir(os.path.split(file_registry)[0])
##    FR=FileRegister(File_Registry)
##    FR.add_entry(r'C:\Documents and Settings\sandersa\My Documents\Share\ArbDB\all_spectra.PNG')
##    FR.save()
    FR=FileRegister(file_registry)
    new_Metadata=Metadata(FR,metadata)
    
    for URL in new_Metadata.FileRegister.Id_dictionary.keys():
        try:
            system_metadata=get_system_metadata(URL_to_path(URL))
            new_Metadata.get_file_node(URL)
            new_Metadata.add_element_to_current_node(name='System_Metadata',**system_metadata)
        except:
            print 'No system_metadata'
            pass
        try:
            file_metadata=get_file_metadata(URL_to_path(URL))
        
        
            new_file_info_node=new_Metadata.document.createElement('File_Metadata')
            for key,value in file_metadata.iteritems():
                new_node=new_Metadata.document.createElement(key)
                new_text=new_Metadata.document.createTextNode(str(value))
                new_node.appendChild(new_text)
                new_file_info_node.appendChild(new_node)
            new_Metadata.add_element_to_current_node(node=new_file_info_node)
            print ' file data'
        except:
            raise#print 'no file data'
            #pass
        try: 
            image_metadata=get_image_metadata(URL_to_path(URL))           
            if not image_metadata is None:
                new_image_info_node=new_Metadata.document.createElement('Image_Metadata')
                for key,value in image_metadata.iteritems():
                    new_node=new_Metadata.document.createElement(key)
                    new_text=new_Metadata.document.createTextNode(str(value))
                    new_node.appendChild(new_text)
                    new_image_info_node.appendChild(new_node)
                new_Metadata.add_element_to_current_node(node=new_image_info_node)
                print ' Image data'
        except:
            raise
            
            pass
        try: 
            python_metadata=get_python_metadata(URL_to_path(URL))
            #print python_metadata
            new_Metadata.get_file_node(URL)
            
            new_Metadata.add_element_to_current_node(XML_tag='Python_Docstring',
            value=str(python_metadata['Python_Docstring']))
        except:pass
    new_Metadata.save()
    
def test_alias():
    print " Before making the instance the attributes defined are:"
    for attribute in dir(FileRegister):
        print 'Attribute Name: %s'%(attribute)
    new=FileRegister()
 
    print " After making the instance the attributes defined are:"
    for attribute in dir(new):
        print 'Attribute Name: %s'%(attribute)

def test_current_node_to_HTML():
    """ test for Metadata.current_node_to_HTML """
    
    File_Registry=os.path.join(PYMEASURE_ROOT,'Settings/Test/test.xml')
    #Note: if meta_path leads to an empty file this gives: xml.parsers.expat.ExpatError: no element found: line 1, column 0
    meta_path=os.path.join(PYMEASURE_ROOT,'Settings/Test/test_Metadata.xml')       
    new_Metadata=Metadata(File_Registry,meta_path)
    print new_Metadata.print_current_node()
    print new_Metadata.current_node_to_HTML()
    
def test_name_search(name='test',flags=None):
    """"tests the name search method"""
    
    File_Registry=os.path.join(PYMEASURE_ROOT,'Settings/Test/test.xml')
    meta_path=os.path.join(PYMEASURE_ROOT,'Settings/Test/test_Metadata.xml')     
    new_Metadata=Metadata(File_Registry,meta_path)
    print "The Current URLS are :\n"
    print new_Metadata.URL_dictionary.values()   
    print "\n The URL's with the word %s in them are:\n"%name
    print new_Metadata.search_name(name,flags)
def test_add_tree(path=os.path.join(PYMEASURE_ROOT,'Instruments')):
    """Tests adding full tree to a file register, path is the root of the tree"""
    new=FileRegister()
    #new.path=URL_to_path(condition_URL(os.path.join(PYMEASURE_ROOT,'Settings/Test/Instrument_Files.xml')))
    #new.add_tree(path,**{'only':'.xml', 'print_ignored_files': True})
    #new.add_tree(path,**{'ignore':'.xml', 'print_ignored_files': True})
    new.add_tree(path)
    #new.add_tree(path)
    #new.save()
    new.path=URL_to_path(r'Files_On_Storage_2.xml')
    new.save()
def test_save_HTML(input_path=os.path.join(PYMEASURE_ROOT,'Settings/Test/test.xml'),
    output_path=os.path.join(PYMEASURE_ROOT,'Documentation\Raw Documentation\html book 01_28_11','ArbDB.html')):
    "Test to see if output of to_HTML can be used in a help book"
    test=FileRegister(input_path)
    out_data=test.to_HTML()
    out_file=open(output_path,'w')
    out_file.write(str(out_data))
    out_file.close()
    print out_data
    #print output_path
        
            
    
#-------------------------------------------------------------------------------
# Module Runner --- Script to be executed from the command line 
# as python arbDB.py. or upon double clicking the file    

if __name__ == '__main__':
    #test_name_search('share',re.IGNORECASE)
    #test_name_search('Test',flags=re.IGNORECASE)
    #test_adding_metadata_to_all()
    #test_add_tree(r'Z:\FIB User Folders\aric')
    #test_current_node_to_HTML()
    #test_Metadata()
    Metadata_robot(r'F:\Share\pyMeasure\Files_On_Storage_2.xml')
    #test_save_HTML()
##    print 'Nothing today'