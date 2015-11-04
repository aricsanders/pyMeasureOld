#-----------------------------------------------------------------------------
# Name:        OceanOptics.py
# Purpose:     To Control Ocean Optics USB spectrometers
#
# Author:      Aric Sanders
#
# Created:     2009/09/25
# RCS-ID:      $Id: OceanOptics.py $
#-----------------------------------------------------------------------------
""" Module contains the functions and classes for using the Ocean Optics USB 
Spectrometers"""

#-------------------------------------------------------------------------------
# Standard Imports

import os
#from ctypes import * 

#-------------------------------------------------------------------------------
# Third Party Imports

try:
    from jpype import * 
except:
    print ' This requires the package jpype'
    print ' Please Download it from http://jpype.sourceforge.net/'
    print ' or add it to the Python Path. '

#-------------------------------------------------------------------------------
# Constants

OMNIDRIVER_CLASS_PATH="C:/Program Files/Ocean Optics/OmniDriverSPAM/OOI_HOME/\
OmniDriver.jar"

WRAPPER_PACKAGE='com.oceanoptics.omnidriver.api.wrapper'

startJVM(r"C:\Program Files\Java\j2re1.4.2_03\bin\client\jvm.dll", 
'-Djava.class.path=%s'%OMNIDRIVER_CLASS_PATH
)
#-------------------------------------------------------------------------------
# Class Definitions

# Note you have to shut down JVM after you are done with the wrapper 
Wrapper=JPackage(WRAPPER_PACKAGE).Wrapper


def random_test():
    """ just some first tests to get the Omni Driver working"""
    
    # it took me awhile to get this one right, but reference the jar file in 
    #'-Djava.class.path=C:/Program Files/Ocean Optics/OmniDriverSPAM/OOI_HOME\
    #/OmniDriver.jar' 
    startJVM(r"C:\Program Files\Java\j2re1.4.2_03\bin\client\jvm.dll", 
    '-Djava.class.path=%s'%OMNIDRIVER_CLASS_PATH
    ) 
 
    package=JPackage('com.oceanoptics.omnidriver.api.wrapper')
    jclass=package.Wrapper
    wrapper=jclass()

    wrapper.openAllSpectrometers()
    number_of_spectrometers=wrapper.getNumberOfSpectrometersFound()
    name=wrapper.getName(0)
    serial=wrapper.getSerialNumber(0)
    wrapper.setIntegrationTime(0,100000)
    data=wrapper.getSpectrum(0)
    wavelengths=wrapper.getWavelengths(0)

    print 'There are %s Spectrometers'%number_of_spectrometers
    print 'It is a %s'%name
    print "it's serial # is %s"%serial
##    print data
##    print wavelengths
    print dir(wrapper)
    wrapper.closeAllSpectrometers()
    shutdownJVM()
     
def test_Wrapper():
    """ Tests the class Wrapper"""
    new=Wrapper()
    print new
    print dir(new) 
    shutdownJVM()     
#-------------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    test_Wrapper()
