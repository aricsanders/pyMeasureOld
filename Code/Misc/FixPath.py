#-----------------------------------------------------------------------------
# Name:        FixPath.py
# Purpose:  To fix data files to have relative paths   
#
# Author:      Aric sanders
#
# Created:     2012/01/16
# RCS-ID:      $Id: FixPath.py $
#-----------------------------------------------------------------------------


"""This a stupid fix-it script that changes all those long file names that don't work 
for xsl, etc into relative paths."""

# Standard Imports-- All in the python standard library


import os                                          # path functions etc. 

#-------------------------------------------------------------------------------
# Third Party Imports
try: 
    import pyMeasure
except:
    print("The topmost pyMeasure folder was not found please make sure that the directory directly above it is on sys.path") 
    raise

#-------------------------------------------------------------------------------
# Constants
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))


#-------------------------------------------------------------------------------
#Scripts

def fix_path_win7(directory=os.path.join(PYMEASURE_ROOT,'Data/States'),text_to_replace='',replacement=''):
    """ Fixes the path crap I had to deal with when I upgraded to Win7"""
    files=os.listdir(directory)
    for file in files:
        try:
            filename=os.path.join(directory,file)
            infile=open(filename,'r')
            indata=infile.read()
            infile.close()
            outdata=indata.replace(text_to_replace,replacement)
            outfile=open(filename,'w')
            outfile.write(outdata)
            outfile.close()
        except:
            #raise
            print("An error occured on file: %s"%file)
            pass
        

    
    

if __name__ == '__main__':
   #fix_path_win7(text_to_replace='C:/Documents and Settings/sandersa/My Documents/Share/pyMeasure/Data/States/',replacement='')
    fix_path_win7(directory=os.path.join(PYMEASURE_ROOT,'Data/Measurements'),text_to_replace='C:/Users/sandersa/Desktop/My Documents/Share/pyMeasure/Data/Measurements/',replacement='')
    #fix_path_win7(directory=r'C:\Users\sandersa\Desktop\My Documents\Share\PIF\Website\pif\equipment',text_to_replace='132.163.53.152',replacement='132.163.81.184')
    #fix_path_win7(directory=r'C:\Users\sandersa\Desktop\My Documents\Share\PIF\Website\pif\home\templates',text_to_replace='132.163.81.98',replacement='132.163.81.184')
    #fix_path_win7(directory=os.path.join(PYMEASURE_ROOT,'Settings/Test') ,text_to_replace='C:/Documents and Settings/sandersa/My Documents/Share/pyMeasure',replacement=PYMEASURE_ROOT)