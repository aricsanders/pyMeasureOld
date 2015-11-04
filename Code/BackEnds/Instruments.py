#-----------------------------------------------------------------------------
# Name:        Instruments.py
# Purpose:     To deal with controling instruments
#
# Author:      Aric Sanders
#
# Created:     2009/10/01
# RCS-ID:      $Id: Instruments.py $
#-----------------------------------------------------------------------------
""" The Module Instruments Contains Classes and functions to control 
instruments; GPIB,RS232,Mightex USB Cameras,Ocean Optics Spectrometers,and LabJack
USB DAQ's. """

# TODO:Fix Save State, and importing from DataHandlers
#-------------------------------------------------------------------------------
# Standard Imports-- All in the python standard library
import os
import re
from types import *
from ctypes import *
import datetime,time


#-------------------------------------------------------------------------------
# Third Party Imports
try: 
    from PIL import Image
    PIL_AVAILABLE=1
except:
    print 'PIL is required for some camera operations'
    PIL_AVAILABLE=0
try:
    import visa
except:
    print "To control comm and gpib instruments this module requires the package PyVisa"
    print " Please download it at  http://pyvisa.sourceforge.net/ "
    print " Or add it to the Python Path"
    pass 
try:
    #raise
    import pyMeasure.Code.DataHandlers.Instruments
    import pyMeasure.Code.DataHandlers.States
    InstrumentSheet=pyMeasure.Code.DataHandlers.Instruments.InstrumentSheet
    InstrumentState=pyMeasure.Code.DataHandlers.States.InstrumentState
    DATA_SHEETS=1
    #print dir(pyMeasure)
except:
    # If the import of DataHandlers Does not work 
    class  InstrumentSheet():pass
    DATA_SHEETS=0
    print "Can't Find MySelf"
    pass
try:
    from jpype import *
except:
    print 'To Control Ocean Optics Spectrometers jpype is required'
    print ' Please Download it from http://jpype.sourceforge.net/'
    print ' or add it to the Python Path. '
    pass

try: 
    import Mightex
except:
    print 'To control Mightex Cameras the wrapper in the module Mightex is required '
    pass
try: 
    import LabJackPython 
    import u3
except:
    print 'To control Labjack instruments the wrapper in the module LabJackPython is required '
    print 'Please download it from http://github.com/labjack/LabJackPython'
    print ' or add it to the Python Path. '
    pass
try:
    from pyMeasure.Code.Misc.Alias import *
    METHOD_ALIASES=1
except:
    METHOD_ALIASES=0
    pass 

#-------------------------------------------------------------------------------
# Module Constants
ACTIVE_COMPONENTS=[PIL_AVAILABLE,DATA_SHEETS,METHOD_ALIASES]
INSTRUMENT_TYPES=['GPIB','COMM','OCEAN_OPTICS','MIGHTEX','LABJACK']
INSTRUMENTS_DEFINED=[]
#TODO Make PYMEASURE_ROOT be read from the settings folder
PYMEASURE_ROOT=r'C:\Documents and Settings\sandersa\My Documents\Share\pyMeasure'
# The directions  to the ocean optics drivers
OMNIDRIVER_CLASS_PATH="C:/Program Files/Ocean Optics/OmniDriverSPAM/OOI_HOME/\
OmniDriver.jar"
OCEAN_OPTICS_WRAPPER_PACKAGE='com.oceanoptics.omnidriver.api.wrapper'

# RESOLUTION_LIST[TImageControl.Resolution] gives the resolution in pixels
MIGHTEX_RESOLUTION_LIST=[[32,32],[64,64],[160,120],[320,240],[640,480],[800,600],[1024,768],[1280,1024]]
#-------------------------------------------------------------------------------
# Module Functions

#TODO: Move these functions to DataHandlers.Instruments instead

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
                
def find_description(identifier,output='path'):
    """ Finds an instrument description in pyMeasure/Instruments given an identifier, 
    outputs a path or the file."""
    if type(identifier) in StringTypes:
        # Now read in all the Instrument sheets and look for a match
        instrument_folder=os.path.join(PYMEASURE_ROOT,'Instruments')
        for instrument_sheet in os.listdir(instrument_folder):
            path=os.path.join(PYMEASURE_ROOT,'Instruments',instrument_sheet)
            if os.path.isfile(path):
                f=open(path,'r')
                text=f.read()
                if re.search(identifier,text):
                    path_out=re.compile('name|path',re.IGNORECASE)
                    file_contents=re.compile('file|xml|node|contents',re.IGNORECASE)
                    if re.search(path_out,output):
                        return path
                    elif re.search(file_contents,output):
                        return text
    else:
        return None       
#-------------------------------------------------------------------------------
# Class Definitions

class VisaInstrumentError(Exception):
    def __init__(self,*args):
        Exception.__init__(self,*args)

class OceanOpticsInstrumentError(Exception):
    def __init__(self,*args):
        Exception.__init__(self,*args)
        
class LabJackInstrumentError(Exception):
    def __init__(self,*args):
        Exception.__init__(self,*args)
        
class MightexInstrumentError(Exception):
    def __init__(self,*args):
        Exception.__init__(self,*args)
        
class VisaInstrument(visa.Instrument,InstrumentSheet):
    """ General Class to communicate with COMM and GPIB instruments"""
    def __init__(self,resource_name=None,**key_word_arguments):
        """ Intializes the VisaInstrument Class"""
        # First we try to look up the description and get info from it
        if DATA_SHEETS:
            try: 
                self.info_path=find_description(resource_name)
                InstrumentSheet.__init__(self,self.info_path)
                self.info_found=True
                self.DEFAULT_STATE_QUERY_DICTIONARY=self.get_query_dictionary()
            except:
                print 'The information sheet was not found defaulting to address' 
                self.DEFAULT_STATE_QUERY_DICTIONARY={}
                self.info_found=False
                self.instrument_address=resource_name
                pass
        else:
            self.info_found=False
            self.DEFAULT_STATE_QUERY_DICTIONARY={}
            self.instrument_address=resource_name
        
        # Create a description for state saving
        if self.info_found:
            self.description={'State_Description':{'Instrument_Description':self.path}}
        else:
            self.description={'State_Description':{'Instrument_Description':self.instrument_address}}
        
        self.state_buffer=[]
        self.STATE_BUFFER_MAX_LENGTH=10
        
        
        # Call the visa instrument class-- this gives ask,write,read
        visa.Instrument.__init__(self,self.instrument_address,**key_word_arguments)
        self.current_state=self.get_state()
        
        if METHOD_ALIASES and not self.info_found :
            for command in Alias(self):
                exec(command)
        
    def set_state(self,**state_dictionary):
        """ Sets the instrument to the state specified by Command:Value pairs"""
        if len(self.state_buffer)+1<self.STATE_BUFFER_MAX_LENGTH:
            self.state_buffer.append(self.get_state())
        else:
            self.state_buffer.pop(1)
            self.state_buffer.insert(-1,self.get_state())         
        for state_command,value in state_dictionary.iteritems():
            self.write(state_command+' '+str(value))
        self.current_state=self.get_state()
            
    def get_state(self,**state_query_dictionary):
        """ Gets the current state of the instrument """
        if len(state_query_dictionary)==0:
            state_query_dictionary=self.DEFAULT_STATE_QUERY_DICTIONARY
        state=dict([(state_command,self.ask(str(query))) for state_command,query 
        in state_query_dictionary.iteritems()])
        return state
    
    def update_current_state(self):
        self.current_state=self.get_state()
   
    def save_current_state(self):
        """ Saves the state in self.current_state attribute """
        self.current_state=self.get_state()
        self.save_state(**self.current_state)
        
    def save_state(self,state_path=None,**state_dictionary):
        """ Saves any state dictionary to an xml file, with state_name """
        new_state=InstrumentState(**state_dictionary)
        try:
            new_state.add_state_description(self.description)
        except: raise #pass
        new_state.save(state_path)

#-------------------------------------------------------------------------------
    
class OceanOpticsInstrument():
    """ General Class to communicate with Ocean Optics spectrometers"""
    def __init__(self,resource_name=None,**key_word_arguments):
        """ Intializes the OceanOpticsInstrument Class requires java and jpype"""
        #Start with intializing the Java Wrapper
        #os.chdir('C:')
        print isJVMStarted()
        
        # this way you can have two in theory
        if not isJVMStarted():
            startJVM(r"C:\Program Files\Java\j2re1.4.2_03\bin\client\jvm.dll", 
            '-Djava.class.path=%s'%OMNIDRIVER_CLASS_PATH)
        try:
            self.wrapper=JPackage(OCEAN_OPTICS_WRAPPER_PACKAGE).Wrapper()
            self.wrapper.openAllSpectrometers()
            
        except:
            raise OceanOpticsInstrumentError('Java Wrapper Failed')
        # If the resource name is none assume the first spectrometer in the list
        if resource_name is None:
            resource_name=0
        elif type(resource_name) in StringTypes:
            try:
                resource_name=int(resource_name)
            except ValueError:
                # try to figure it out
                number_of_spectrometers=self.wrapper.getNumberOfSpectrometersFound()
                name_list=[self.wrapper.getName(index) for index in 
                range(number_of_spectrometers)]
                
                serial_list=[self.wrapper.getSerialNumber(index) for index in 
                range(number_of_spectrometers)]
                try:
                    resource_name=name_list.index(resource_name)
                except ValueError:
                    resource_name=serial_list.index(resource_name)
                except:
                    pass

                        

        # kill the call if it has not been asigned an index here           
        if not type(resource_name) is IntType:
            print "The resource name provided is not valid, it must be either"
            print " a number, a serial number, or a name. It also must be connected."
            raise OceanOpticsInstrumentError('Instrument Not Found')
        # Start setting the attributes
        self.address=resource_name
        self.name=self.wrapper.getName(self.address)
        self.serial=self.wrapper.getSerialNumber(self.address)
        
        self.instrument_type='OCEAN_OPTICS'
        
        # add the commands using the wrapper's dir, leaving out builtins
        self.commands=[]
        for attribute in dir(self.wrapper):
            if not re.match('__',attribute):
                self.commands.append(attribute)
                            
        self.DEFAULT_STATE_QUERY_DICTIONARY={
        'setIntegrationTime':'getIntegrationTime',
        'setScansToAverage':'getScansToAverage',
        'setBoxcarWidth':'getBoxcarWidth'}    
        self.current_state=self.get_state()
        
        self.state_buffer=[]
        # TODO: Grab this from a preferences file
        self.STATE_BUFFER_MAX_LENGTH=10
        
        if METHOD_ALIASES:
            for command in Alias(self):
                exec(command)

        
    def write(self,command):
        """ Writes a command to the Spectrometer"""
        eval('self.wrapper.%s'%command)
        
    def ask(self,command):
        """ Writes a command to the Spectrometer and then reads the answer"""
        value=eval('self.wrapper.%s'%command)
        return value
    def read(self,command):
        """ Writes a command to the Spectrometer and then reads the answer"""
        value=eval('self.wrapper.%s'%command)
        return value
    
    def get_spectrum(self):
        """ Returns a list of (wavlength,amplitude) points for the current spectrum"""
        amplitude_list=self.wrapper.getSpectrum(self.address) 
        wavelength_list=self.wrapper.getWavelengths(self.address)
        data=[(wavelength_list[index],amplitude) for index,amplitude in 
        enumerate(amplitude_list)]
        return data
    def set_integration_time(self,integration_time):
        """ Sets the integration time in seconds. note: state command is in us"""
        time_in_microseconds=int(round(integration_time*10**6))
        self.wrapper.setIntegrationTime(self.address,time_in_microseconds)
    def get_integration_time(self):
        """ Gets the integration time in seconds note: state command is in us"""
        time_in_microseconds=self.wrapper.getIntegrationTime(self.address)
        return float(time_in_microseconds)/10**6
    
    def set_state(self,**state_dictionary):
        """ Sets the instrument to the state specified by Command:Value pairs"""
        # first add the current state to the state buffer
        if len(self.state_buffer)+1<self.STATE_BUFFER_MAX_LENGTH:
            self.state_buffer.append(self.get_state())
        else:
            self.state_buffer.pop(1)
            self.state_buffer.insert(-1,self.get_state())
            
        for state_command,value in state_dictionary.iteritems():
            self.write(state_command+'('+str(self.address)+','+str(value)+')')
                        
    def get_state(self,**state_query_dictionary):
        """ Gets the current state of the instrument """
        if len(state_query_dictionary)==0:
            state_query_dictionary=self.DEFAULT_STATE_QUERY_DICTIONARY
        state=dict([(state_command,self.ask(query+'('+str(self.address)+')')) 
        for state_command,query in state_query_dictionary.iteritems()])
        return state
    
            
    def save_current_state(self):
        """ Saves the state in self.current_state attribute """
        self.current_state=self.get_state()
        self.save_state(**self.current_state)
        
    def save_state(self,state_path=None,**state_dictionary):
        """ Saves any state dictionary to an xml file, with state_name """
        new_state=InstrumentState(**state_dictionary)
        new_state.add_state_description(self.description)
        new_state.save(state_path)

      
    def __del__(self):
        """ Builtin method called when the garabage collector is cleaning up"""
        self.wrapper.closeAllSpectrometers()
        # the JVM is not shuting down 
        #shutdownJVM()
        
        
    
#-------------------------------------------------------------------------------
     
class LabJackInstrument():
    """ General Class to communicate with LabJack instruments"""
    def __init__(self,resource_name=None,**key_word_arguments):
        """ Intializes the LabJackInstrument Class, supports U3 all others are
        untested, but may work."""
        
        # if the name is not given assume it is a U3
        if resource_name is None:
            # if there are multiple ones connected choose the first
            connected_devices=LabJackPython.listAll(LabJackPython.LJ_dtU3)
            self.LabJack_info=connected_devices.values()[0]
        # now we can parse the possibilities:
        elif resource_name in [3,'U3','LJ_dtU3']:
            # if there are multiple ones connected choose the first
            connected_devices=LabJackPython.listAll(LabJackPython.LJ_dtU3)
            self.LabJack_info=connected_devices.values()[0]  
        elif resource_name in [9,'UE9','LJ_dtUE9']:
            # if there are multiple ones connected choose the first
            connected_devices=LabJackPython.listAll(LabJackPython.LJ_dtUE9)
            self.LabJack_info=connected_devices.values()[0]
        elif resource_name in [6,'U6','LJ_dtU6']:
            # if there are multiple ones connected choose the first
            connected_devices=LabJackPython.listAll(LabJackPython.LJ_dtU6)
            self.LabJack_info=connected_devices.values()[0]
        else:
            try:
                for device_type in [LabJackPython.LJ_dtU3,LabJackPython.LJ_dtUE9,
                LabJackPython.LJ_dtU6]:
                    if resource_name in LabJackPython.listAll(device_type).keys():
                        connected_devices=LabJackPython.listAll(LabJackPython.LJ_dtU6)
                        self.LabJack_info=connected_devices[resource_name]                      
                        break
            except:
                print 'Resource Name is Not valid Must be a Labjack type, or '
                print ' a vaild serial number'
                raise LabJackInstrumentError('No Device Found')
        #self.wrapper=LabJackPython -- since labjack  has a module not a single
        # class this does not make since, I will just call things directly from
        # the module       
        self.LabJack_type=self.LabJack_info['devType']
        self.serial=self.LabJack_info['serialNumber']
        self.address=self.LabJack_info['localID']
        self.instrument_type='LABJACK'
        self.LabJack_connection_type=LabJackPython.LJ_ctUSB        
        self.handle=LabJackPython.openLabJack(self.LabJack_type,
        self.LabJack_connection_type,handleOnly =True)
        
        self.commands=[]
        # if the attribute does not have __ in the name and it has GET or PUT
        # then it is a command
        for attribute in dir(LabJackPython):
            if not re.match('__',attribute) and (re.search('GET',attribute) or
            re.search('PUT',attribute)) :
                self.commands.append(attribute)
                    
        self.channel_configuration={}
        self.mode_list=['analog','digital','timer','counter']
        
        self.DEFAULT_STATE_QUERY_DICTIONARY={}
        self.state_buffer=[]
        self.STATE_BUFFER_MAX_LENGTH=10
        if self.LabJack_type == 3:
            self.channel_locations={1:'SGND',2:'SPC',3:'SGND',4:'VS',5:'FIO7',
            6:'FIO6',7:'GND',8:'VS',9:'FIO5',10:'FIO4',11:'GND',12:'VS',13:'VS',
            14:'GND',15:'DAC0',16:'DAC1',17:'VS',18:'GND',19:'AIN2',20:'AIN3',
            21:'VS',22:'GND',23:'AIN0',24:'AIN1','DB15':{1:'VS',2:'CIO1',3:'CIO3',4:'EIO0',
            5:'EIO2',6:'EIO4',7:'EIO6',8:'GND',9:'CIO0',10:'CIO2',11:'GND',
            12:'EIO1',13:'EIO3',14:'EIO5',15:'EIO7'}}
            self.write(LabJackPython.LJ_ioPUT_DAC_ENABLE,1)       
            self.configuration={}
            self.channel_numbers={}
            self.channel_names=self.channel_locations.values()
            self.channel_names.remove(self.channel_locations['DB15'])
            self.channel_names.extend(self.channel_locations['DB15'].values())
            for channel_name in self.channel_names:
                if channel_name in ['GND','SGND','VS']:
                    self.configuration[channel_name]=channel_name
                elif re.match('FIO|AIN|EIO|CIO|DAC',channel_name):
                    match=re.match('\w\w\w(?P<number>\d)',channel_name)
                    number=int(match.group('number'))
                    if re.match('EIO',channel_name):
                        number=number+8
                    elif re.match('CIO',channel_name):
                        number=number+16
                    self.channel_numbers[channel_name]=number
                    #self.configuration[channel_name]=self.get_configuration(channel_name)
        self.current_state=self.get_state()            
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)
    def channel_name(self,input):
        """ Returns the channel name given a location, name or alias"""
        if input in self.channel_names:
            return input
        elif type(input) in StringTypes:
            try:
                output=self.channel_locations[int(input)]
                return output
            except:
                if re.match('DB15',input):
                    DB15_pin=int(input.split('DB15')[1])
                    return self.channel_locations['DB15'][DB15_pin]
                else:
                    raise LabJackInstrumentError('Could not determine channel name.')
        elif type(input)==IntType:
            try:
                output=self.channel_locations[input]
                return output
            except:
                pass
        else:
            raise LabJackInstrumentError('Could not determine channel name.')
            
    def get_configuration(self,channel_name=None):
        """ Gets the current configuration and returns a configuration dictionary"""
        try:
            channel_name=self.channel_name(channel_name)
            if re.match('FIO|EIO',channel_name):pass             
        except:
            raise
        
        
    def configure_channel(self,channel_name,channel_mode,**optional_configuration):
        """ Configures a channel to digital, analog , counter or timer"""
        not_configurable=['GND','SGND','VS']
        try:
            channel_name=self.channel_name(channel_name)      
        except:
            raise            
        
        if channel_mode == 'analog':
            self.write(LabJackPython.LJ_ioPUT_ANALOG_ENABLE_BIT,
            self.channel_numbers[channel_name],1)
        elif channel_mode =='digital':
            self.write(LabJackPython.LJ_ioPUT_ANALOG_ENABLE_BIT,
            self.channel_numbers[channel_name],0)  
        elif channel_mode =='counter':
            #TODO: Enable Counter to write pin given channel_name
            #TODO: Count to make sure there are at most 2
            pass
            self.write(LabJackPython.LJ_ioPUT_COUNTER_ENABLE,
            self.channel_numbers[channel_name],0)  
        elif channel_mode == 'timer':
            #the timer is a little wierd, first set the pin offset >4
            #then determine how many 1 or 2
            #then configure each, which will now appear at channel_number=
            # pin offset+timer number for things that can be digitalIO
            pass
      
        else:
            raise LabJackInstrumentError('Invalid channel mode for configure_channel.')
                
    def set_value(self,channel_name,value):
        """ Sets the value of channel"""
        try:
            channel_name=self.channel_name(channel_name)      
        except:
            raise   
        if re.match('DAC',channel_name):
            try:   
                if value is None:raise
                LabJackPython.AddRequest(self.handle,LabJackPython.LJ_ioPUT_DAC, 
                self.channel_numbers[channel_name], value, 0, 0)            
                LabJackPython.Go()
                
                exec('self.%s=float("%s")'%(channel_name,value))
            except : # TODO catch the error for passing None Specifically
                pass
        elif re.match('FIO|EIO|CIO',channel_name):
            LabJackPython.AddRequest(self.handle,LabJackPython.LJ_ioPUT_DIGITAL_BIT, 
            self.channel_numbers[channel_name], value, 0, 0)            
            LabJackPython.Go()   
        elif re.match('GND|SGND|VS|SPC',channel_name) or channel_name is None:
            pass        
        else:
            raise LabJackInstrumentError('Invalid channel name for set_value.')
        self.current_state=self.get_state()
            
    def get_value(self,channel_name,channel_name_2=None):
         """ Gets the value of the channel_name if channel_name_2 has a value get a differential
         reading  """
         try:
            channel_name=self.channel_name(channel_name)      
         except:
            raise   
         if not channel_name_2 is None:
            value=self.ask(LabJackPython.LJ_ioGET_AIN_DIFF, 
            self.channel_numbers[channel_name],optional_parameter=self.channel_numbers[channel_name_2])
         if re.match('DAC',channel_name):
            try:
                value=eval('self.%s'%channel_name)
            except:
                value=None
            return value  
            
         elif re.match('AIN',channel_name):
            value=self.ask(LabJackPython.LJ_ioGET_AIN, 
            self.channel_numbers[channel_name])
            return value
               
         elif re.match('FIO|EIO|CIO',channel_name):
            value=self.ask(LabJackPython.LJ_ioGET_DIGITAL_BIT_STATE, 
            self.channel_numbers[channel_name])            
            return value
         elif re.match('GND|SGND',channel_name):
            value=0
            return value     
         elif re.match('VS',channel_name):
            value=5
            return value
         elif re.match('SPC',channel_name):
            value=None
            return value        
         else:
            raise LabJackInstrumentError('Invalid channel name for get_value.')
        
    def write(self,command,channel,value=0,optional_parameter=0,user_buffer=0):
        """ Writes a command to the LabJack device """
        LabJackPython.AddRequest(self.handle, command, 
        channel, value, optional_parameter, user_buffer)
        LabJackPython.Go()
        
    def ask(self,command,channel,value=0,optional_parameter=0,user_buffer=0):
        """ Writes a command to the labjack and returns a value """
        LabJackPython.AddRequest(self.handle, command, 
        channel, value, optional_parameter, user_buffer)
        
        LabJackPython.Go()
        
        answer=LabJackPython.GetResult(self.handle, command, channel)
        return answer
        
    def read(self,command,channel):
        """ Reads the result of giving command to channel """
        value=LabJackPython.GetResult(self.handle, command, channel)
        return value
    def set_state(self,**state_dictionary):
        """ Sets the instrument to the state specified by Command:Value pairs"""
        for channel,value in state_dictionary.iteritems():
            if not re.search('AIN',channel):
                self.set_value(channel,value)
            else:
                pass
        self.current_state=self.get_state()
            
    def get_state(self,**state_query_dictionary):
        """ Gets the current state of the instrument """
        if len(state_query_dictionary)==0:
            state_query_dictionary=self.channel_names
        state=dict([(channel,self.get_value(channel)) for channel 
        in state_query_dictionary])
        self.current_state=state
        return state
    
            
    def save_current_state(self):
        """ Saves the state in self.current_state attribute """
        self.current_state=self.get_state()
        self.save_state(**self.current_state)
        
    def save_state(self,state_path=None,**state_dictionary):
        """ Saves any state dictionary to an xml file, with state_name """
        new_state=InstrumentState(**state_dictionary)
        new_state.save(state_path)

#-------------------------------------------------------------------------------
    
class MightexInstrument():
    """ General Class to communicate with Mightex USB cameras"""
    def __init__(self,resource_name=None,**key_word_arguments):
        """ Intializes the MightexInstrument Class requires Mightex.Wrapper
        COMPATIBILTY ISSUES MUST BE A CAMERA ONLY APPLICATION"""
        print 'Warning:COMPATIBILTY ISSUES MUST BE A CAMERA ONLY APPLICATION'
        # it does not play well with the ocean optics for some reason,
        # however Mightex.Exe can work simultaneosly. 
        # I think the mightex problems result from the StartCameraEngine and 
        # Start Frame Grab commands; In order for everything to work it needs
        # to be embedded in a loop. I have had issues if the Video window is 
        # not shown
        
        #Start with intializing the Wrapper
        try:
            self.wrapper=Mightex.Wrapper()
        except:
            print "Wrapper failed"
            raise MightexInstrumentError('Mightex.Wrapper() failed')
        number_of_cameras=self.wrapper.MTUSB_InitDevice()
        # If the resource name is none assume the first camera in the list
        if resource_name is None:
            resource_name=self.wrapper.MTUSB_OpenDevice(0)
            if resource_name==-1:
                raise MightexInstrumentError('Could Not Open Device: Check Connection')
       
        elif type(resource_name) in StringTypes:
            try:
                resource_name=self.wrapper.MTUSB_OpenDevice(int(resource_name))
            except ValueError:
                # try to figure it out
                device_handles=[self.wrapper.MTUSB_OpenDevice(index) for index in
                range(number_of_cameras)]
                
                pointer_char_list=[c_char_p(''*20) for i in range(number_of_cameras)]
                success_list=[self.wrapper.MTUSB_GetModuleNo(device_handle,
                pointer_char_list[index]) for 
                index,device_handle in enumerate(device_handles)]
                module_list=[element.value for element in pointer_char_list]
                
                success_list=[self.wrapper.MTUSB_GetSerialNo(device_handle,
                pointer_char_list[index]) for 
                index,device_handle in enumerate(device_handles)]
                
                serial_list=[element.value for element in pointer_char_list]
                
                for i in range(number_of_cameras):
                    if resource_name in module_list:
                        resource_name=device_handles[i]
                    elif resource_name in serial_list:
                        resource_name=device_handles[i]
        # kill the call if it has not been asigned an device handle here           
        if not type(resource_name) is IntType:
            print "The resource name provided is not valid, it must be either"
            print " a number, a serial number, or a Module Number. It also must be connected."
            raise MightexInstrumentError
        # Start setting the attributes
        self.address=resource_name
        buffer1=c_char_p(''*20)
        self.wrapper.MTUSB_GetModuleNo(self.address,buffer1)
        self.module_number=buffer1.value
        buffer2=c_char_p(''*20)
        self.wrapper.MTUSB_GetSerialNo(self.address,buffer2)
        self.serial=buffer2.value
        self.wrapper.MTUSB_StartCameraEngine(self.address)
        self.c_state=Mightex.TImageControl()
        self.wrapper.MTUSB_GetFrameSetting(self.address,byref(self.c_state))
        self.instrument_type='MIGHTEX'
        
        # add the commands using the wrapper's dir, leaving out builtins
        self.commands=[]
        for attribute in dir(self.wrapper):
            if not re.match('__',attribute):
                self.commands.append(attribute)
##                            
##        self.DEFAULT_STATE_QUERY_DICTIONARY={'MTUSB_SetFrameSetting':'MTUSB_GetFrameSetting'}    
##        self.current_state=self.get_state()
##        
        self.state_buffer=[]
        # TODO: Grab this from a preferences file
        self.STATE_BUFFER_MAX_LENGTH=10
        # Method aliases seems to break this class it seems to be a conflict with
        # the StartCameraEngine command?--I can't figure out what is up with the
        # SDK.
##        if METHOD_ALIASES:
##            for command in alias(self):
##                exec(command)

    def start_frame_grab(self):
        "Starts the frame grabing process"
        self.write('MTUSB_StartFrameGrab(self.address,0x8888)')
        
    def stop_frame_grab(self):
        "Stops the frame grabing process"
        self.write('MTUSB_StopFrameGrab(self.address)')
        
    def show_video_window(self,size=None):
        """ Shows the mightex video window provided in the SDK, use start_frame_grab
        after showing the video window to see an image"""
        if size is None:
            self.write('MTUSB_ShowVideoWindow(self.address,0,0,640,480)')
        elif type(size) == ListType:
            self.write(
            'MTUSB_ShowVideoWindow(self.address,%s,%s,%s,%s)'%(size[0],size[1],
            size[2],size[3]))
                   
    def write(self,command):
        """ Writes a command to the camera"""
        print'self.wrapper.%s'%command
        exec('self.wrapper.%s'%command)
        
    def ask(self,command):
        """ Writes a command to the camera and then reads the answer"""
        value=eval('self.wrapper.%s'%command)
        return value
    def read(self,command):
        """ Writes a command to the camera and then reads the answer"""
        value=eval('self.wrapper.%s'%command)
        return value
    if PIL_AVAILABLE:
        def get_frame(self):
            """ Returns a matrix of 8bit intensity values frame grabing Must be started"""
            # This requires PIL to work
            number_x_pixels=MIGHTEX_RESOLUTION_LIST[self.c_state.Resolution][0]
            number_y_pixels=MIGHTEX_RESOLUTION_LIST[self.c_state.Resolution][1]
            frame_buffer=create_string_buffer("", number_x_pixels*number_y_pixels) 
            self.wrapper.MTUSB_GetCurrentFrame(self.address,0,byref(frame_buffer))
            image=Image.fromstring("L",(number_x_pixels,number_y_pixels),
            frame_buffer)
            return image
        
    def set_exposure_time(self,integration_time):
        """ Sets the integration time in seconds. note: state command is in us"""
        time_in_microseconds=int(round(integration_time*10**6))
        self.wrapper.setIntegrationTime(self.address,time_in_microseconds)
        
    def get_exposure_time(self):
        """ Gets the integration time in seconds note: state command is in us"""
        time_in_microseconds=self.wrapper.getIntegrationTime(self.address)
        return float(time_in_microseconds)/10**6
    
    def set_state(self,**state_dictionary):
        """ Sets the instrument to the state specified by Command:Value pairs"""
        # first add the current state to the state buffer
        if len(self.state_buffer)+1<self.STATE_BUFFER_MAX_LENGTH:
            self.state_buffer.append(self.get_state())
        else:
            self.state_buffer.pop(1)
            self.state_buffer.insert(-1,self.get_state())         
        for state_command,value in state_dictionary.iteritems():
            self.write(state_command+'('+str(self.address)+','+str(byref(value))+')')
                        
    def get_state(self,**state_query_dictionary):
        """ Gets the current state of the instrument """
        if len(state_query_dictionary)==0:
            state_query_dictionary=self.DEFAULT_STATE_QUERY_DICTIONARY
        state=dict([(state_command,self.ask(query+'('+str(self.address)+')')) 
        for state_command,query in state_query_dictionary.iteritems()])
        return state
            
    def save_current_state(self):
        """ Saves the state in self.current_state attribute """
        self.current_state=self.get_state()
        self.save_state(**self.current_state)
        
    def save_state(self,state_path=None,**state_dictionary):
        """ Saves any state dictionary to an xml file, with state_name """
        new_state=InstrumentState(**state_dictionary)
        new_state.save(state_path)

      
    def __del__(self):
        """ Builtin method called when the garabage collector is cleaning up"""
        self.wrapper.MTUSB_StopCameraEngine(self.address)
        self.wrapper.MTUSB_UnInitDevice()
        



#-------------------------------------------------------------------------------
# Module Scripts

def test_determine_instrument_type():
    print 'Type is %s'%determine_instrument_type('GPIB::22')
    print 'Type is %s'%determine_instrument_type('COMM::1')
    print 'Type is %s'%determine_instrument_type('CoMm::1') 
    print 'Type is %s'%determine_instrument_type('SRS830') 
    print 'Type is %s'%determine_instrument_type('36111') 
    class blank():pass
    new=blank()
    print type(new)
    print 'Type is %s'%determine_instrument_type(new)
    new.instrument_type='Ocean_Optics'
    print new.instrument_type
    print 'Type is %s'%determine_instrument_type(new)
    TF=(type(new)==InstanceType or ClassType)
    print TF
    print dir(new)
    print 'instrument_type' in dir(new)
        
def test_OceanOpticsInstrument():
    spectrometer=OceanOpticsInstrument('USB2000') #for only one hooked up it works
    print spectrometer.write.__doc__
    print dir(spectrometer)
    print spectrometer.commands
    print 'It is a %s'%spectrometer.name
    print "it's serial # is %s"%spectrometer.serial
    print spectrometer.get_state()
    spectrometer.set_state(**spectrometer.get_state())
    print spectrometer.address
    #print spectrometer.get_spectrum()
    print spectrometer.get_integration_time()
    
         
def test_MightexInstrument():
    camera=MightexInstrument()
    print camera.write.__doc__
    print dir(camera)
    print camera.commands
    print 'It has module number %s'%camera.module_number
    print "it's serial # is %s"%camera.serial
    #image=camera.get_frame()
    #print image
    #dir(camera)
    #print camera.get_state()
    #camera.set_state(**camera.get_state())
def test_IV():
    """ a simple IV with a labjack u3 with a spectrum in between"""
    spectrometer=OceanOpticsInstrument('USB2000')
    u3=LabJackInstrument()
    #camera=MightexInstrument()
    from scipy import linspace
    start=0
    stop=1
    num_points=20
    values=linspace(start,stop,num_points).tolist()
    IV=[]
    s=[]
    #images=[]
    for value in values:
        u3.set_value('DAC1',value)
        time.sleep(.1)
        IV.append((u3.get_value('AIN0'),u3.get_value('DAC1')))
        s.append(spectrometer.get_spectrum())
        #images.append(camera.get_frame())
    print IV
    print len(s),len(s[0])
    #print len(images),len(images[0])
                   
def test_LabJackInstrument():
    u3=LabJackInstrument()
    print u3.write.__doc__
    print dir(u3)
##    for command in u3.commands:
##        print command
    print 'It has address %s'%u3.address
    print "it's serial # is %s"%u3.serial
    print "it's handle is %s"%u3.handle
    voltage=0
    print " Seting DAC1 to %s Volts"%voltage
    u3.set_value('DAC1',voltage)
    print "DAC1 Voltage is %s"%u3.get_value('DAC1')
    ON_OFF=0
    print " Seting FIO4 to %s"%ON_OFF
    u3.set_value('FIO4',ON_OFF)
    print u3.get_value('FIO4')
    print u3.configuration
    print u3.channel_names
    print u3.channel_numbers
    try:
        print u3.channel_name('1')
        print u3.channel_name(1)
        print u3.channel_name('AIN1')
        print u3.channel_name('DB15 1')
    except LabJackInstrumentError:
        print 'Caught an Error'
def test_find_description():
    """Tests the function find description"""
    print "The path of the description of %s is %s"%('Lockin2',find_description('Lockin2'))
    print "The File Contents are:"
    print find_description('Lockin2','file')
     
def test_VisaInstrument():
    """ Simple test of the VisaInstrument class"""
    srs810=VisaInstrument('GPIB::2')
    print srs810.ask('*IDN?')
    print dir(srs810)
    print srs810.idn
    print srs810.DEFAULT_STATE_QUERY_DICTIONARY
    print srs810.current_state
    print 'Writing 0 volts to AUX4'
    srs810.set_state(**{'AUXV 4,':0})
    print srs810.current_state
    print srs810.state_buffer
    print srs810.commands
def test_labjack_fast():
    # This seems to indicate that the response time is 15 ms
    # I am not sure why it is so slow.--> Just a clock resolution thing
    # If you use time.clock() it is better, the resolution is a OS dependent thing
    # Reading from the labjack appears to take ~4ms (250HZ)
    u3=LabJackInstrument()
    for i in range(250):
        y=u3.get_value('AIN0')
        t=time.clock()
        #t=time.time()
        #t=datetime.datetime.utcnow().isoformat()
        print y,t
#-------------------------------------------------------------------------------
# Module Runner       

if __name__ == '__main__':
    
    test_labjack_fast()
    #test_MightexInstrument()
    #test_OceanOpticsInstrument()
    
    #test_IV()
    #test_find_description()
    #test_VisaInstrument()
    #user_terminate=raw_input("Please Press Any key To Finish:")
    
