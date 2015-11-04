#-----------------------------------------------------------------------------
# Name:        names.py
# Purpose:   A helper module that determines automatic
#               file names for data saving  
#
# Author:      Aric Sanders
#
# Created:     2009/09/17
# RCS-ID:      $Id: names.py $
# Copyright:   --None--
# Licence:     --None--
#-----------------------------------------------------------------------------
""" The module names contains the functions for automatically 
generating file names """
#-------------------------------------------------------------------------------
# Standard Package Imports

import os
import re
import datetime
#-------------------------------------------------------------------------------
# Third part imports
try: 
    import pyMeasure
except:
    print("The topmost pyMeasure folder was not found please make sure that the directory directly above it is on sys.path") 
    raise

#-------------------------------------------------------------------------------
# Module Constants
GENERAL_DESCRIPTORS=['Log','Measurement','State','Settings']
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))


#-------------------------------------------------------------------------------
# Module Functions
def get_date():
    """Returns todays date in 'ddmmyyyy' format"""
    today=datetime.date.today()
    return today.strftime('%m%d%y')
    
def get_filename_iterator(base_name=None,directory=None):
    """ Returns the number of files in directory with base_name +1"""
    iterator=0
    if base_name is None:
        return '1'
    elif directory is None:
        path=os.getcwd()
        file_names=os.listdir(path)
        for name in file_names:
            if re.match(base_name,name):
                iterator+=1
        return str(iterator+1)
        
    else:
        file_names=os.listdir(directory)
        for name in file_names:
            if re.match(base_name,name):
                iterator+=1
        return str(iterator+1) 
def auto_name(specific_descriptor=None,general_descriptor=None,directory=None):
    """ Returns an automatically generated name for a file in a directory"""
    if not specific_descriptor is None:
        name=specific_descriptor
        if not general_descriptor is None:
            name=name+'_'+general_descriptor
        name=name+'_'+get_date()+'_'
        name=name+get_filename_iterator(name,directory)+'.xml'
        return name
    else:
        return None
    
    
    
            
#-------------------------------------------------------------------------------
# Module Scripts

def test_module():
    """ Tests the module by writing files in the current working directory """
    base_name='Test_File'
    number_files=20
    print 'The result of get_filename_iterator() is %s'%get_filename_iterator()
    print '-'*80
    print '\n'
    print 'The current working diretory is %s \n'%os.getcwd()
    for i in range(number_files):
        try:
            new_name=base_name+'_'+get_filename_iterator(base_name,os.getcwd())+'.txt'
            f=open(new_name,'w')
            f.write(str(i))
            f.close()
            print "Wrote New File %s"%new_name
        except:
            raise
            print 'failed'
            
def clean_up_test_module():
    """ Deletes the files writen by test_module() """
    base_name='Test_File'
    number_files=int(get_filename_iterator(base_name,os.getcwd()))-1
    print '\n\nThe result of get_filename_iterator(base_name,os.getcwd()) is %s'%get_filename_iterator("Test_File",os.getcwd())
    print '-'*80
    print 'The current working diretory is %s \n'%os.getcwd()
    for i in range(number_files):
        try:
            new_name=base_name+'_'+str(i+1)+'.txt'
            os.remove(new_name)
            print "Removed File %s"%new_name
            
        except:
            raise
            print 'failed'
def test_auto_name():
    """Tests the auto name function"""
    states_directory=os.path.join(PYMEASURE_ROOT,'Data','States').replace('\\','/')
    print "The Automatic name for a state is %s"%auto_name('Test','State',states_directory)
#-------------------------------------------------------------------------------
# Module Runner

if __name__ == '__main__':
    test_module()
    clean_up_test_module()
    #test_auto_name()    
        