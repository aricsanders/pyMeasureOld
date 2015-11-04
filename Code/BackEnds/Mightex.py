#-----------------------------------------------------------------------------
# Name:        Mightex.py
# Purpose:     To demonstrate the use of a Mightex USB camera using thier dll.
#
# Author:      Aric Sanders
#
# Created:     2009/10/07
# RCS-ID:      $Id: Mightex.py $
#-----------------------------------------------------------------------------
""" Module for controling the mightex usb camera, using the Mightex
dll and SDK. I took it verbatim, and have tried to slowly edit the grammar.
Important: For proper operatioin of the camera, the application
 should have the following sequence:
wrapper=Mightex.Wrapper()     
wrapper.MTUSB_InitDevice(); // Get the devices
wrapper.MTUSB_OpenDevice(); // Using the device index returned by the previous MTUSB_InitDevice() call.
wrapper.MTUSB_GetModuleNo();
wrapper.MTUSB_GetSerialNo();
wrapper.MTUSB_StartCameraEngine(); // Using the device handle returned by MTUSB_OpenDevice()
.. Operations ..
wrapper.MTUSB_StopCameraEngine();
wrapper.MTUSB_UnInitDevice()
Note that we don't need to explicitly close the opened device, because:
1) If user wants to open another device, open device will automatically 
close the previously opened device,
2) MTUSB_UnInitDevice() will close the opened device, and release all other
 resources."""
#-------------------------------------------------------------------------------
# Standard Library Imports
from ctypes import *
import time
import os
#-------------------------------------------------------------------------------
# Module Constants

#TODO Make PYMEASURE_ROOT be read from the settings folder
PYMEASURE_ROOT=r'C:\Documents and Settings\sandersa\My Documents\Share\pyMeasure'
C_HEADER_FUNCTIONS="""SDK_API MTUSB_InitDevice( void );
SDK_API MTUSB_UnInitDevice( void );
SDK_HANDLE_API MTUSB_OpenDevice( int deviceID );
SDK_HANDLE_API MTUSB_ShowOpenDeviceDialog( void );
SDK_API MTUSB_GetModuleNo( DEV_HANDLE DevHandle, char *ModuleNo );
SDK_API MTUSB_GetSerialNo( DEV_HANDLE DevHandle, char *SerialNo );
SDK_API MTUSB_StartCameraEngine( HWND ParentHandle, DEV_HANDLE DevHandle );
SDK_API MTUSB_StopCameraEngine( DEV_HANDLE DevHandle );
SDK_API MTUSB_SetCameraWorkMode( DEV_HANDLE DevHandle, int WorkMode );
SDK_API MTUSB_SetExternalParameters( DEV_HANDLE DevHandle, int AutoLoop, int IsRawGraph,
                                     int IsJPEG, char *FilePath, char *FileName);
SDK_API MTUSB_WaitingExternalTrigger( DEV_HANDLE DevHandle, int StartWait, CallBackFunc Aproc );
SDK_API MTUSB_ShowFrameControlPanel( DEV_HANDLE DevHandle, int IsTriggerModeAllow, int CloseParent, 
                     char *Title, int Left, int Top);
SDK_API MTUSB_HideFrameControlPanel( DEV_HANDLE DevHandle );
SDK_API MTUSB_ShowVideoWindow( DEV_HANDLE DevHandle, int Top, int Left,
                   int Width, int Height );
SDK_API MTUSB_DisplayVideoWindow( int IsDisplayVideoWindow );
SDK_API MTUSB_StartFrameGrab( DEV_HANDLE DevHandle, int TotalFrames );
SDK_API MTUSB_StopFrameGrab( DEV_HANDLE DevHandle );
SDK_API MTUSB_GetFrameSetting( DEV_HANDLE DevHandle, PImageCtl SettingPtr);
SDK_API MTUSB_SetFrameSetting( DEV_HANDLE DevHandle, PImageCtl SettingPtr);
SDK_API MTUSB_SetResolution( DEV_HANDLE DevHandle, PImageCtl SettingPtr);
SDK_API MTUSB_SetStartPosition( DEV_HANDLE DevHandle, PImageCtl SettingPtr);
SDK_API MTUSB_SetGain( DEV_HANDLE DevHandle, PImageCtl SettingPtr);
SDK_API MTUSB_SetExposureTime( DEV_HANDLE DevHandle, PImageCtl SettingPtr);
SDK_API MTUSB_SetGammaValue( DEV_HANDLE DevHandle, PImageCtl SettingPtr);
SDK_API MTUSB_SetGammaTable( DEV_HANDLE DevHandle, unsigned char *GammaTable );
SDK_API MTUSB_SetShowMode( DEV_HANDLE DevHandle, PImageCtl SettingPtr);
SDK_API MTUSB_SetWhiteBalance( DEV_HANDLE DevHandle );
SDK_API MTUSB_SetFrameRateLevel( DEV_HANDLE DevHanlde, int RateLevel );
SDK_API MTUSB_SetAutoExposure( DEV_HANDLE DevHanlde, int AutoExposureOn, int ShowExposureMark );
SDK_API MTUSB_GetCurrentFrameRate( DEV_HANDLE DevHandle );
SDK_API MTUSB_GetLastBMPFrame( DEV_HANDLE DevHandle, char *FileName );
SDK_API MTUSB_GetCurrentFrame( DEV_HANDLE DevHandle, int FrameType, unsigned char *Buffer );
SDK_API MTUSB_GetCurrentFrame2( DEV_HANDLE DevHandle, int FrameType, unsigned char *Buffer, unsigned char *ImagePropertyBuf );
SDK_API MTUSB_InstallFrameHooker( DEV_HANDLE DevHandle, int IsMaxFrameRate, int FrameType, GetFrameCallBack FrameHooker);
SDK_API MTUSB_InstallDeviceHooker( DeviceCallBack DeviceHooker );
SDK_API MTUSB_SaveFramesToFiles( DEV_HANDLE DevHandle, PImageCtl SettingPtr,
                                 char *FilePath, char *FileName );
SDK_API MTUSB_SetLEDBrightness( DEV_HANDLE DevHandle, unsigned char LEDChannel, 
                                unsigned char Brightness );
SDK_API MTUSB_SetGPIOConifg( DEV_HANDLE DevHandle, unsigned char ConfigByte );
SDK_API MTUSB_SetGPIOInOut( DEV_HANDLE DevHandle, unsigned char OutputByte,
                             unsigned char *InputBytePtr );"""
# RESOLUTION_LIST[TImageControl.Resolution] gives the resolution in pixels
RESOLUTION_LIST=[[32,32],[64,64],[160,120],[320,240],[640,480],[800,600],[1024,768],[1280,1024]]

#Default location for MTApplication.exe
DEFAULT_PATH_MTAPPLICATION=r'C:\Documents and Settings\sandersa\My Documents\Share\pyMeasure\Code\BackEnds'
#-------------------------------------------------------------------------------
# Module Functions
def launch_mightex_application(path=None):
    """ Uses sys to launch MTApplication.exe"""
    #TODO:PUT A Windows only filter
    #TODO: Figure out where os.system thinks it is
    if path is None:
        path=DEFAULT_PATH_MTAPPLICATION
    path_list=os.path.split(path)
    application_name='MTApplication.exe'
    os.system('cd ..')
##    for directory in path_list[1:]:
##        os.system('cd %s'%directory)
    os.system('start %s'%application_name)
    
        
        

#-------------------------------------------------------------------------------
# Class Definitions
class MightexWrapperError(Exception):
    """ An Error in the Wrapper """
    pass
class TImageAttachData(Structure):
    """ This strucuture is from MT_USBCamera_SDK.h, using ctypes 
    """
    _fields_=[('XStart',c_long),('YStart',c_long),('GreenGain',c_long),\
    ('BlueGain',c_long),('RedGain',c_long),('ExposureTime',c_long),
    ('TriggerOccurred',c_long),('Reserved1',c_long),('Reserved2',c_long)]
    
# TODO: something is weird about the structure it returns strange value for
# TODO: vertical mirror      
    
class TImageControl(Structure):
    """ This strucuture is from MT_USBCamera_SDK.h, using ctypes 
    typedef struct { 
    int Revision; 
    // For Image Capture 
    int Resolution; 
    int BinMode; 
    int XStart; 
    int YStart; 
    int GreenGain; 
    int BlueGain; 
    int RedGain; 
    int MaxExposureTimeIndex; 
    int ExposureTime; 
    // For Image Rendor 
    bool ImageRendorFitWindow; 
    int Gamma; 
    int Contrast; 
    int Bright; 
    int SharpLevel; 
    bool BWMode; 
    bool HorizontalMirror; 
    bool VerticalFlip; 
    // For Capture Files. 
    int CatchFrames; 
    bool IsAverageFrame; 
    bool IsCatchRAW; 
    bool IsRawGraph; 
    bool IsCatchJPEG; 
    bool CatchIgnoreSkip; 
    } TImageControl; 
    #pragma pack() """
    _fields_=[('Revision',c_long),('Resolution',c_long),('BinMode',c_long),
    ('XStart',c_long),('YStart',c_long),('GreenGain',c_long),\
    ('BlueGain',c_long),('RedGain',c_long),('MaxExposureTimeIndex',c_long),
    ('ExposureTime',c_long),('ImageRendorFitWindow',c_long),
    ('Gamma',c_long),('Contrast',c_long),('Bright',c_long),('SharpLevel',c_long),
    ('BWMode',c_long),('HorizontalMirror',c_long),
    ('VerticalFlip',c_long),('CatchFrames',c_long),('IsAverageFrame',c_long),
    ('IsCatchRAW',c_long),('IsRawGraph',c_long),('IsCatchJPEG',c_long),
    ('CatchIgnoreSkip',c_long)]
    
class Wrapper():
    """ Principle wrapper for the Mightex SDK """
    def __init__(self):
        """ Initilaizes the Mightex Wrapper"""
        # TODO: Instead of return function
        # TODO: use try: function except: raise MightexWrapperError(Function)
        os.chdir(os.path.join(PYMEASURE_ROOT,'Code','BackEnds'))
        # Load the c functions form the dll
        try:
            self.c_dll=windll["MT_USBCamera_SDK_Stdcall.dll"]
        except:
            print "The Wrapper requires MT_USBCamera_SDK_Stdcall.dll"
            print " Please download it and put in in BackEnds directory"
            raise MightexWrapperError('MT_USBCamera_SDK_Stdcall.dll not found')
        
    def MTUSB_InitDevice(self):
        """ Intialize the Cameras attached and return number of cameras--should 
        be the first function that any program calls."""
        return self.c_dll.MTUSB_InitDevice()
    
    def MTUSB_UnInitDevice(self):
        """This is the function to release all the resources reserved by 
        MTUSB_InitDevice(), user should invoke it before application terminates.
        always returns 0"""
        return self.c_dll.MTUSB_UnInitDevice()
    
    def MTUSB_ShowOpenDeviceDialog(self):
        """User may call this function to show the Device Open Dialog, 
        which lets user to select the camera will be operated. Returns Handle for
        the selected device"""
        return self.c_dll.MTUSB_ShowOpenDeviceDialog()
    
    def MTUSB_OpenDevice(self,device_ID):
        """If user doesn't want to use the previous Open Device Dialog for opening
        a selected device, user may use This function to open the device. Returns
        the device handle"""
        device_handle=self.c_dll.MTUSB_OpenDevice(device_ID)
        if device_handle == 0xFFFFFFFF :
            raise MightexWrapperError("""Camera Engine Running Shut down and try
            again""")
        return self.c_dll.MTUSB_OpenDevice(device_ID)
    
    def MTUSB_GetModuleNo(self,device_handle, pointer_char_for_module_number ):
        """For an opened device, user might get its Module Number by invoking 
        this function."""
        return self.c_dll.MTUSB_GetModuleNo(device_handle, 
                pointer_char_for_module_number)
                
    def MTUSB_GetSerialNo(self,device_handle,pointer_char_for_module_number ):
       """For an opened device,get the Serial Number by invoking 
       this function. """       
       return self.c_dll.MTUSB_GetSerialNo(device_handle,pointer_char_for_module_number )
   
    def MTUSB_StartCameraEngine(self,device_handle,ParentHandle=None):
        """We have a multiple threads camera engine internally, 
        which is responsible for all the frame grabbing, raw data to 
        RGB data conversion.etc. functions. User MUST start this engine for 
        all the following camera related operations"""   
        return self.c_dll.MTUSB_StartCameraEngine(ParentHandle,device_handle)
    
    def MTUSB_StopCameraEngine(self,device_handle):
        """This function stops the started camera engine."""
        return self.c_dll.MTUSB_StopCameraEngine(device_handle)
    
    def MTUSB_SetCameraWorkMode(self,device_handle,work_mode=0):
        """By default, the Camera is working in "Video" mode in which camera 
        deliver frames to PC continuously, however, 
        user may set it to "External Trigger" Mode, in which the camera is 
        waiting for an external trigger signal and capture ONE frame of image."""
        return self.c_dll.MTUSB_SetCameraWorkMode(device_handle,work_mode)
    
    def MTUSB_SetExternalParameters(self,device_handle,AutoLoop,IsRawGraph,IsJPEG,pointer_FilePath,pointer_FileName):
        """While the camera is in "External Trigger" Mode, invoking this 
        function set the parameters for external trigger mode. 
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        AutoLoop - Whether is "Automatic Loop" or only One Shot Wait.
        IsRawGraph - If it's true, the saved BMP or JPEG file is the raw graph which is not adjusted by Gamma, Contrast, Bright or Sharp settings.
        IsJPEG - Is the saved file in JPEG format (other than BMP format).
        FilePath, FileName - the directory and name of the saved file. Note that for path, the ending "\" is NOT needed, for filename, the extension (jpg or bmp) is NOT needed.
        Return: -1: If the function fails (e.g. invalid device handle or camera is NOT in External Trigger Mode or it's during waiting for external trigger )
        1: Call succeeds.
        Important: Invoking this function won't really start the waiting of the external
        trigger, this function only set the parameters for trigger mode, a 
        sequential invoking of the following MTUSB_WaitingExternalTrigger() 
        is needed to fulfill the whole external trigger services."""
        return self.c_dll.MTUSB_SetExternalParameters(device_handle,AutoLoop,IsRawGraph,IsJPEG,pointer_FilePath,pointer_FileName)
            
    def MTUSB_WaitingExternalTrigger(self,device_handle,StartWaiting, CallBackFunc):
        """While the camera is in "External Trigger" Mode, invoking this 
        function starting the waiting for external signal."""
        return self.c_dll.MTUSB_WaitingExternalTrigger(device_handle,StartWaiting, CallBackFunc)
    
    def MTUSB_HideFrameControlPanel(self,device_handle):
        """This function hides the control panel, note the control panel is always 
        there once the camera engine is started, hiding it only make it invisible.
        Argument: DevHandle - the device handle returned by either 
        MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        Return: -1 If the function fails (e.g. invalid device handle or if the engine is NOT started yet)
        1 if the call succeeds."""
        return self.c_dll.MTUSB_HideFrameControlPanel(device_handle)
    
    def MTUSB_ShowVideoWindow(self,device_handle,Top,Left,Width,Height):
        """This function shows the video window, user may customize it's position and size with the input arguments.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice() Left, Top - the Top-Left position of the video window.
        Width, Height - The width and height of the video window.
        Return: -1 If the function fails (e.g. invalid device handle or if the engine is NOT started yet)
        1 if the call succeeds."""
        return self.c_dll.MTUSB_ShowVideoWindow(device_handle,Top,Left,Width,Height)
    
    def MTUSB_StartFrameGrab(self,device_handle,TotalFrames ):
        return self.c_dll.MTUSB_StartFrameGrab(device_handle,TotalFrames )
    
    def MTUSB_ShowFrameControlPanel(device_handle,IsTriggerModeAllow,CloseParent,Title_pointer,Left,Top): 
        """For user to develop application conveniently and easily, 
        the library provides its second dialog window which has all the camera controls on it, 
        if user use this window in his application, it's NOT necessarily to use most of other functions. 
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog()
         or MTUSB_OpenDevice() 
        IsTriggerModeAllow - Set to control whether the Trigger Mode Selection 
        is visible on control panel. We provide this parameter for user doesn't 
        want to have "External Trigger" mode available on control panel. 
        CloseParent - Set to TRUE if user wants to close the Parent Window of 
        the control panel, while user click the [x] button of the panel, note 
        that this usually closes the whole application. Title - The Title will 
        be displayed on the control panel. 
        Left, Top - the Top-Left position of the control panel. 
        Return: -1 If the function fails (e.g. invalid device handle) 
        1 If the call succeeds. 
        Important: Close this control panel will close the whole application 
        (it will post a message of SC_CLOSE to it's parent window), so if user
         wants to have this control panel shown in application, the parent window 
         is NOT necessarily visible. If user wants to hide this panel, don't close it, 
         but invoke MTUSB_HideFrameControlPanel() function instead. """
        return self.c_dll.MTUSB_ShowFrameControlPanel(device_handle,IsTriggerModeAllow,CloseParent,Title_pointer,Left,Top)
    
    def MTUSB_StopFrameGrab(self,device_handle):
        """When camera engine is started, in Video mode, the engine prepares all the resources, but it does NOT start the frame grabbing , until MTUSB_StartFrameGrab() function is invoked. After it's successfully called, user should see video on the video window ( if it's showed ). User may call MTUSB_StopFrameGrab() to stop the engine from grabbing frames from camera.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        TotalFrames - This is used in MTUSB_StartFrameGrab() only, after grabbing this frames, the camera engine will automatically stop frame grabbing, if user doesn't want it to be stopped, set this number to 0x8888, which will doing frame grabbing forever, until user calls MTUSB_StopFrameGrab(). Return: -1 If the function fails (e.g. invalid device handle or if the engine is NOT started yet)
        1 if the call succeeds."""
        return self.c_dll.MTUSB_StopFrameGrab(device_handle)
    
    def MTUSB_GetFrameSetting(self,device_handle,setting_pointer):
        """User may get the current set of parameters by invoking this function, please note that the TimagControl data structure contains all the parameters for controlling Frame Grabbing, Video rendering and File savings.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        setting_pointer - the Pointer to variable of TImageControl structure.
        Return: -1 If the function fails (e.g. invalid device handle )
        1 if the call succedds.
        Important:
        1) There're two ways to change those settings, from the control panel OR by calling the following MTUSB_Setxxx functions, either way, the settings returned from this function are the current latest settings of the camera engine.
        2) The TimageControl data structure has the following elements, please refer to the c style comments in /* */ for their definition:
        typedef struct {
        int Revision; /* Reserved for internal use only */
        // For Image Capture
        int Resolution; /* This is an index to resolution settings, we have the following definition for it:
        0 - 32 x 32
        1 - 64 x 64
        2 - 160 x 120
        3 - 320 x 240
        4 - 640 x 480
        5 - 800 x 600
        6 - 1024 x 768
        7 - 1280 x 1024
        8 - 1600 x 1200 For 3M Camera only
        9 - 2048 x 1536 For 3M Camera only
        */
        int BinMode; /* 1 - No Skip mode, 2 - 2X skip or binning mode (1:2 decimation) */
        int XStart; /* Start Column of the ROI, should be even number or a value of multiple of 4 when it's in Skip mode*/
        int YStart; /* Start Row of the ROI, should be even number or a value of multiple of 4 when it's in Skip mode*/
        int GreenGain; /* Green Gain Value: 0 - 128, the actual gain is GreenGain/8 */
        int BlueGain; /* Blue Gain Value: 0 - 128, the actual gain is BlueGain/8 */
        int RedGain; /* Red Gain Value: 0 - 128, the actual gain is RedGain/8 */
        int MaxExposureTimeIndex; /* The index for maximum exposure time:
        0 - 5ms
        1 - 10ms
        2 - 100ms
        3 - 750ms
        */
        int ExposureTime; /* The current exposure time in Micro second, e.g. 10000 means 10ms */
        // For Video image rendor
        bool ImageRendorFitWindow; /* True if the image always fit video window, False if the image will keep the same
        resolution as the grabbing resolution
        */
        int Gamma; /* Gamma value: 0 - 20, means 0.0 - 2.0 */
        int Contrast; /* Contrast value: 0 - 100, means 0% -- 100% */
        int Bright; /* Brightness : 0 - 100, means 0% -- 100% */
        int SharpLevel; /* SharpLevel: 0 - 3, means Normal, Sharp, Sharper and Sharpest */
        bool BWMode; /* Black White mode? */
        bool HorizontalMirror; /* Horizontal Mirror? */
        bool VerticalFlip; /* Vertical Flip? */
        // For Capture Files.
        int CatchFrames; /* Number of frames to be captured */
        bool IsAverageFrame; /* Save only one frame, but it's the average of all grabbed frames */
        bool IsCatchRAW; /* Save as RAW Data File? */
        bool IsRawGraph; /* Save as JPG or BMP, but not corrected by Gamma, contrast, bright and sharp algorithm */
        bool IsCatchJPEG; /* Save as JPEG File? */
        bool CatchIgnoreSkip; /* Always capture full resolution? */
        } TImageControl;"""
        return self.c_dll.MTUSB_GetFrameSetting(device_handle,setting_pointer)
    
    def MTUSB_SetFrameSetting(self,device_handle,setting_pointer):
        """User may set the all parameters by invoking this function.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        SettingPtr - the Pointer to variable of TImageControl structure.
        Return: -1 If the function fails (e.g. invalid device handle )
        1 if the call succeeds.
        Important: This function set all of the parameters of SettingPtr to 
        camera engine, and is effective immediately after the call, if the frame
         grabbing is started, it's immediately affected by those settings."""
        return self.c_dll.MTUSB_SetFrameSetting(device_handle,setting_pointer)
    
    def MTUSB_SetResolution(self,device_handle,setting_pointer):
        return self.c_dll.MTUSB_SetResolution(device_handle,setting_pointer)
    
    def MTUSB_SetStartPosition(device_handle,setting_pointer):
        """User may set the start position of ROI parameters by invoking this function.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        SettingPtr - the Pointer to variable of TImageControl structure.
        Return: -1 If the function fails (e.g. invalid device handle )
        1 if the call succedds.
        Important: Although the second input argument is a pointer to 
        TimageControl structure, only two elements "XStart" and "YStart " 
        are used by this function, all others are ignored."""
        return self.c_dll.MTUSB_SetStartPosition(device_handle,setting_pointer)
    
    def MTUSB_SetGain(self,device_handle,setting_pointer):
        """User may set RGB Gains parameters by invoking this function.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        SettingPtr - the Pointer to variable of TImageControl structure.
        Return: -1 If the function fails (e.g. invalid device handle )
        1 if the call succeeds.
        Important: Although the second input argument is a pointer to 
        TimageControl structure, only three elements "GreenGaint", 
        "BlueGain" and "RedGain " are used by this function, all others are 
        ignored."""
        return self.c_dll.MTUSB_SetGain(device_handle,setting_pointer)
    
    def MTUSB_SetExposureTime(self,device_handle,setting_pointer):
        """User may set the exposure time parameters by invoking this function.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        SettingPtr - the Pointer to variable of TImageControl structure.
        Return: -1 If the function fails (e.g. invalid device handle )
        1 if the call succeeds.
        Important: Although the second input argument is a pointer to 
        TimageControl structure, only two elements "MaxExposureTimeIndex" 
        and "ExposureTime " are used by this function, all others are ignored."""
        return self.c_dll.MTUSB_SetExposureTime(device_handle,setting_pointer)
    
    def MTUSB_SetGammaValue(self,device_handle,setting_pointer):
        """User may set the Gamma, Contrast and Brightness parameters by invoking this function.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        SettingPtr - the Pointer to variable of TImageControl structure.
        Return: -1 If the function fails (e.g. invalid device handle )
        1 if the call succeeds.
        Important: Although the second input argument is a pointer to 
        TimageControl structure, only four elements "Gamma", "Contrast",
         "Bright " and "SharpLevel" are used by this function, all others are 
         ignored."""
        return self.c_dll.MTUSB_SetGammaValue(device_handle,setting_pointer)
    
    def MTUSB_SetGammaTable(self,device_handle,pointer_GammaTable ):
        """User may set the internal Gamma Table by invoking this function.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        GammaTable - the Pointer to 256 bytes array which contains the Gamma table.
        Return: -1 If the function fails (e.g. invalid device handle )
        1 if the call succeeds.
        Important: Camera engine has an internal Gamma table to do the Gamma 
        correction, all the output value is get as GammaTable[InputValue], 
        while InputValue is the ADC value read from CMOS sensor."""
        return self.c_dll.MTUSB_SetGammaTable(device_handle,pointer_GammaTable)
    
    def MTUSB_SetShowMode(self,device_handle,setting_pointer):
        """User may set the BWMode, HorizontalMirror and VerticalFlip parameters by invoking this function.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        SettingPtr - the Pointer to variable of TImageControl structure.
        Return: -1 If the function fails (e.g. invalid device handle)
        1 if the call succedds.
        Important: Although the second input argument is a pointer to 
        TimageControl structure, only three elements "BWMode",
         "HorizontalMirror" and "VerticalFlip " are used by this function, 
         all others are ignored."""
        return self.c_dll.MTUSB_SetShowMode(device_handle,setting_pointer)
    
    def MTUSB_SetWhiteBalance(self,device_handle):
        """User may call this function for Automatic White Balance set.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        Return: -1 If the function fails (e.g. invalid device handle)
        1 if the call succeeds.
        Important: This is the equivalent to the button of in control panel, 
        note that user should set proper exposure time and put a white paper at
         proper distance before this function is invoked."""
        return self.c_dll.MTUSB_SetWhiteBalance(device_handle)
    
    def MTUSB_SetFrameRateLevel(self,device_handle,RateLevel):
        """User may call this function to set the current frame grabbing rate.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        RateLevel - Can be from 0 - 10, while 0 means the lowest frame rate, 10 means the highest rate.
        Return: -1 If the function fails (e.g. invalid device handle)
        1 if the call succeeds.
        Important: In the current design, the actual frame rate is mainly 
        depending on the PC resources. The frame rate might be different on a 
        slow PC and a fast PC, the default setting of the camera engine is to 
        set the Maximum frame rate, however, that might not be ideal as almost 
        all the CPU resources will be used by camera engine, which will make
        other PC applications "hunger" of CPU time, user might want to reduce 
        the frame rate a little bit to politely give other application time to 
        run."""
        return self.c_dll.MTUSB_SetFrameRateLevel(device_handle,RateLevel)
    
    def MTUSB_SetAutoExposure(self,device_handle,AutoExposureOn,ShowExposureMark):
        """User may call this function to set the current frame grabbing rate.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        AutoExposureOn - True/False to turn the "Auto Exposure" feature On/Off.
        ShowExposureMark - True/False to show/hide the Exposure Mark.
        Return: -1 If the function fails (e.g. invalid device handle or camera engine is in "External Trigger" mode)
        1 if the call succeeds."""
        return self.c_dll.MTUSB_SetAutoExposure(device_handle,AutoExposureOn,ShowExposureMark)
    
    def MTUSB_GetCurrentFrameRate(self,device_handle):
        """User may call this function to get the current frame grabbing rate.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        Return: -1 : If the function fails (e.g. invalid device handle) -2 : Camera engine is not grabbing frames.
        -3 : Camera engine is grabbing frames, but the current camera is unplugged from the USB bus.
        1 : if the call succedds.
        Important: This is an average frame rate of the current grabbing, as PC is not a real time system, which might
        switch to other applications, so the actual frame rate is vary a little 
        bit from time to time. This function returns the frame rate at the 
        calling moment. With the control panel, frame rate is also shown on 
        the bottom right corner."""
        return self.c_dll.MTUSB_GetCurrentFrameRate(device_handle)
    
    def MTUSB_GetLastBMPFrame(self,device_handle,pointer_FileName):
        """User may call this function to get the bitmap format frame of the last captured frame.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        FileName - the full file name for the bitmap file.
        Return: -1 If the function fails (e.g. invalid device handle)
        1 if the call suceeds.
        Important: While the frame grabbing is running OR it's stopped, we can 
        always get the last (for the time this function is invoking) frame of 
        the Video window in Bitmap format. Note that this function may mainly 
        be used in situation of user stop the video as the frame is exactly the 
        user's interesting. Note that this bitmap frame is adjusted with user's 
        setting of Gamma, contrast, bright and sharp level, if user wants to get 
        un-adjusted image data, user might invoke
        MTUSB_SetGammaValue() function with Gamma set to 10 ( mean 1.0), 
        contrast and bright set to 50 ( mean 50%) and SharpLevel set to 0 
        ( mean Normal)."""
        return self.c_dll.MTUSB_GetLastBMPFrame(device_handle,pointer_FileName)
    
    def MTUSB_GetCurrentFrame(self,device_handle,FrameType,pointer_Buffer ):
        """User may call this function to get a frame.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        FrameType - 0: Raw Data
        1: 24bit Bitmap Data (DIB)
        Buffer - Byte buffer to hold the whole frame of image.
        Return: -1 If the function fails (e.g. invalid device handle or the frame grabbing is NOT running)
        1 if the call succedds.
        Important: This function can only be invoked while the frame grabbing is
        started, user might want to get a frame of image in memory, instead of 
        in a file. This function will put the current frame into Buffer, either 
        in Raw data format, or in bitmap format, note that it's caller's 
        responsibility to have big enough buffer to hold the image data, the 
        buffer size should be:
        In Raw Data format: At least (Row x Column) Bytes,
        In Bitmap Data Format, for Mono camera, At least (Row x Column ) Bytes, for Color Camera, At least 3 x ( Row x Column ) Bytes.
        Note that this buffer is from current frame flow, so it's affected with user's setting of Gamma, contrast, bright and sharp level, if user wants to get un-adjusted image data, user might invoke MTUSB_SetGammaValue() function with Gamma set to 10 ( mean 1.0), contrast and bright set to 50 ( mean 50%) and SharpLevel set to 0 ( mean Normal).
        For the data structure for Raw and DIB data, please refer to next function.
        The frame returned is the frame grabbed at the moment of this function is invoking, it's possible to return the same frame twice if user invokes this function sequentially, or it's possible to miss some frames if user invoke this function in a long interval. For getting each grabbing frame once, it's recommended to use the next function, which installs a callback hooker.
        For the format of memory buffer, please refer to the next function."""
        return self.c_dll.MTUSB_GetCurrentFrame(device_handle,FrameType,pointer_Buffer )
		
    def MTUSB_InstallFrameHooker(self,device_handle,IsMaxFrameRate,FrameType,FrameHooker):
        """Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        IsMaxFrameRate - Set to True if user wants to get Maximum Frame Rate, otherwise set to False.
        FrameType - 0: Raw Data
        1: 24bit Bitmap Data (DIB)
        FrameHooker - Callback function installed.
        Return: -1 If the function fails (e.g. invalid device handle or the frame grabbing is NOT running)
        1 if the call succedds.
        Important: This function can only be invoked while the frame grabbing is started, user might want to be notified every time the camera engine get a new frame, user might use this function to install a callback function, and the callback will be invoked once for each new frame.
        Note
        1). User may use this function to install a callback, or use the previous function to get a frame directly, it's recommended to use only one of these two functions.
        2). For some applications need maximum frame rate of a ROI, user might set IsMaxFrameRate to True, which will give user optimized maximum frame rate on a certain PC. The actual frame rate is depending on the Exposure time and the PC resources. [ Note that you might see frame rate always changes, this is due to the Windows' resource sharing]
        3). The callback has the following prototype:
        typedef void (* GetFrameCallBack)(int FrameType, int Row, int Col,
        TimageAttachData* Attributes, unsigned char *BytePtr );
        The TimageAttachData is defined as:
        typedef struct {
        int XStart;
        int YStart;
        int GreenGain;
        int BlueGain;
        int RedGain;
        int ExposureTime;
        // The following three parameters are increased from SDK versionV1.4.0.0, 2006/10/9
        int TriggerOccurred;
        int Reserve1;
        int Reserve2;
        } TImageAttachData;
        While it's invoked, the FrameType is the same as the FrameType we set, 
        while the BytePtr points to a buffer holds the image data. 
        Row and Col are the size of the image. The TimageAttachData has the 
        Image attributes for this particular frame, this is a very useful 
        information if user want to have a Close Loop Control on the Image 
        Analysis.etc. Note that the installed callback should not include any 
        Blocking functions and it should BE as fast as possible, otherwise it 
        will block the camera engine and reduce the frame rate, and it's also 
        very important that there's no GUI operations in this callback hooker, 
        as it's actually invoked in a working thread, which is NOT sync with the
         main GUI thread (The main GUI thread is written in Delphi, the VCL of Delphi 
         is not supporting multi-thread invoking), So if user has to use messages
          (e.g. postmessage(.) ) for showing any messages on GUI. From SDK V1.4.0.0,
           we increase the "TriggerOccurred" parameter which is "1" if a falling edge occurred on camera's trigger pin before the completing of the frame grabbing. Note this is a "One Shot" flag, an occurrence(or more than one occurrences, but all occurred during one frame grabbing) only set this parameter to "1" for this frame. This gives user a chance to know the occurrence of the external trigger while the camera is working in "Video" mode.
        Caution: The external trigger should be filtered properly so that there's no glitches on this pin.
        From firmware V1.1.3 and later, the Reserve1 field is used to provide a "Time Stamp" for each frame, note that the
        Time stamp is a number from 0 - 65535, it represents 0ms - 65535ms( and round back), with this field, user may
        Know the time interval between two frames.
        4). The callback function is invoked from a working thread, other than the main thread of the application ( usually the UI thread ), so attention must be paid for synchronize issues and data sharing.
        5). While it's in DIB format, the image data is from current frame flow, so it may be corrected with user's setting of Gamma, contrast, bright and sharp level, if user wants to get un-adjusted image data, user might invoke MTUSB_SetGammaValue() function with Gamma set to 10 ( mean 1.0), contrast and bright set to 50 ( mean 50%) and SharpLevel set to 0 ( mean Normal). While the Raw data is definitely un-modified, it's ADC value from sensor.
        6). For Raw data, the BytePtr points to a buffer which contains a raw image data, it has the following format:
        typedef struct {
        unsigned char RawImageData[Rows][Columns];
        } tRawImageData;
        Here, Rows and Columns are set by user ( Resolution, e.g. in case of 1280x1024, its RawImageData[1024][1280]. Also note that the Rows are from top to bottom of the image, Columns are from Right to Left.
        For DIB data, it's different for Mono camera and Color camera:
        For Mono camera, as internally we generate a 8bit bmp, so the buffer points to
        typedef struct {
        unsigned char Bitmap[Rows][Columns];
        } tDIBImageData;
        Each pixel contain a byte, which represents the gray level ( 0 - 255), please note that for BMP, the Rows are from bottom to top of the image, Columns are from Left to Right.
        For Color camera, we're using 24bit bmp internally so the BytePtr points to a buffer which is actually a tDIBImageData structure as following:
        Typedef struct {
        unsigned char Blue;
        unsigned char Green;
        unsigned char Red;
        } tRGBTriple;
        typedef struct {
        tRGBTriple DIBImageData[Rows][Columns];
        } tDIBImageData;
        The Rows are from bottom to top of the image, Columns are from Left to Right.
        Note that all above data structure is "Byte" aligned.
        As you can notice, for Mono camera, it's actually the same for Raw data and Bmp data, except for the orientation of the row and column."""
        return self.c_dll.MTUSB_InstallFrameHooker(device_handle,IsMaxFrameRate,FrameType,FrameHooker)
        
    def MTUSB_SaveFramesToFiles(self,device_handle,setting_pointer,pointer_FilePath,pointer_FileName ):
        """User may call this function to save one or more frames to files.
        Argument: DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        SettingPtr - the Pointer to variable of TImageControl structure.
        FilePath - the directory to store the saved files.
        FileName - the Filename used for file saving, note that the actual file name will be FileName_x.bmp (or
        FileName_x.jpg).
        Return: -1 If the function fails (e.g. invalid device handle or the frame grabbing is NOT running)
        1 if the call succedds.
        Important: Note that This function can only be invoked while the frame 
        grabbing is started, user might want to get one or more frames and save 
        them into a specified location, the "CatchFrames" , "IsAverageFrame", 
        "IsCatchRAW", "IsRawGraph", "IsCatchJPEG" and "CatchIgnoreSkip" in the
         data structure pointed by SettingPtr will be used for number of frames, 
         frame format (Raw, Bmp or Jpeg) and ignore skip mode options.
        Note:
        IsAverageFrame gives user an option to get only ONE frame but it's the 
        average of all the captured frames.
        IsCatchRAW gives user an option to save the files as CMOS sensor raw data,
        currently, we generate a Text file for user's ease of observation
        IsRawGraph gives user an option to save the graphic file ( jpg or bmp) 
        with the data which are NOT corrected with the current Gamma, contrast, 
        bright or sharp algorithm."""
        return self.c_dll.MTUSB_SaveFramesToFiles(device_handle,setting_pointer,pointer_FilePath,pointer_FileName )
    
    def MTUSB_SetLEDBrightness(self,device_handle,LEDChannel,Brightness):
        """User may call this function to set the Brightness of LED Channels
        Argument : DevHandle -- DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        LED Channel - 1 - 5, while 1 - 4 means the channel1 - channel4 of LED light head, 5 means global.
        Brightness - 0 - 100, it's the percentage of the brightness, while 0 mean OFF, 100 mean all ON.
        Return: -1 If the function fails (e.g. invalid device handle or it's a camera WITHOUT LED Driver. )
        1 if the call succeeds.
        Important: Note that This function can only be invoked if the camera is
        with LED driver built in (GLN or MLE)."""
        return self.cdll.MTUSB_SetLEDBrightness(device_handle,LEDChannel,Brightness)
    
    def MTUSB_SetGPIOConifg(self,device_handle,ConfigByte):
        """User may call this function to configure GPIO pins.
        Argument : DevHandle -- DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        ConfigByte - Only the 4 LSB are used, bit0 is for GPIO1, bit1 is for GPIO2 and so on. Set a certain bit to 1 configure the corresponding GPIO to output, otherwise it's input.
        Return: -1 If the function fails (e.g. invalid device handle or it's a camera WITHOUT GPIO )
        1 if the call succedds.
        Important: Note that This function can only be invoked if the camera is 
        with built in GPIO (MCN, GLN and MCE)."""
        return self.cdll.MTUSB_SetGPIOConifg(device_handle,ConfigByte)
    
    def MTUSB_SetGPIOInOut(self,device_handle,OutputByte,pointer_InputBytePtr ):
        """User may call this function to set GPIO output pin states and read the input pins states.
        Argument : DevHandle -- DevHandle - the device handle returned by either MTUSB_ShowOpenDeviceDialog() or MTUSB_OpenDevice()
        OutputByte - Only the 4 LSB are used, bit0 is for GPIO1, bit1 is for GPIO2 and so on. Set a certain bit to 1 will output High on the corresponding GPIO pin, otherwise it outputs Low. Note that it's only working for those pins are configured as "Output".
        InputBytePtr - the Address of a byte, which will contain the current Pin States, only the 4 LSB bits are used, note that even a certain pin is configured as "output", we can still get its current state.
        Return: -1 If the function fails (e.g. invalid device handle or it's camera WITHOUT GPIO)
        1 if the call succedds.
        Important: Note that This function can only be invoked if the camera is with built in GPIO (MCN, GLN and MCE).
        For the above SDK APIs, it's recommended to invoke them in the main thread
        of an application (usually this is the UI thread), as those APIs actually 
        modify the UI of the main control panel (even the panel is not shown). 
        For user needs to have working threads, it's recommended to use working 
        thread for signal/image processing purpose, and notify Main thread 
        (with Windows Thread Sync mechanisms) for the SDK API invoking. Please 
        refer to the Delphi and VC++ examples for the using of those APIs."""
        return self.cdll.MTUSB_SetGPIOInOut(device_handle,OutputByte,pointer_InputBytePtr)
    
    def MTUSB_InstallDeviceHooker(self,DeviceHooker):
        """User may call this function to install a callback, which will be invoked by camera engine while a Mightex camera is added or removed from the USB bus, note that the USB device is not necessarily a Mightex camera, it might a USB device other than the standard USB devices (e.g. USB HID devices, USB Mass Storage Devices.etc.)
        Argument: DeviceHooker - the callback function registered to camera engine.
        Return: It always return 1.
        Note:
        1). If plug or unplug occurs, the camera engine will stop its grabbing and invoke the installed callback function. This notifies the host the occurrence of the device configuration change and it's recommended for host to arrange all the "cleaning" works. Host might simply do house keeping and terminate OR host might let user to re-start the camera engine.
        2). The callback function has the following prototype:
        typedef void (* DeviceFaultCallBack)( int FaultType );
        The FaultType is as following:
        0 - A camera is removed from USB Bus
        1 - A camera is attached to USB Bus
        2 - Low level USB communication error occurred.
        3). Some times defected USB connection (caused by the USB connector or cable) might also cause the Plug/Unplug event.
        In the VC++ example code, this API is used for installing a callback for 
        P&P event."""    
        return self.cdll.MTUSB_InstallDeviceHooker(DeviceHooker)
#-------------------------------------------------------------------------------
# Module Scripts
def test_Wrapper():
    """ Some tests of the Wrapper Class """
    wrapper=Wrapper()
    print dir(wrapper)
    #raise MightexWrapperError('MT_USBCamera_SDK_Stdcall.dll not found')
    
def test_structure():
    """ See if the strucutures defined work"""
    os.chdir(os.path.join(PYMEASURE_ROOT,'Code','BackEnds'))
    new=TImageControl()
    wrapper=Wrapper()
    wrapper.MTUSB_InitDevice() 
    device=wrapper.MTUSB_OpenDevice(0)
    wrapper.MTUSB_StartCameraEngine(device)
    
    wrapper.MTUSB_GetFrameSetting(device,byref(new)) 
    state={}
    for field in new._fields_:
        print field
        print eval('new.%s'%field[0])
        state[field[0]]=eval('new.%s'%field[0])
        print "state[%s]=%s"%(field[0],'new.%s'%field[0])
    for key,value in state.iteritems():
        print key,value
##    new.HorizontalMirror=0
##    print wrapper.MTUSB_SetFrameSetting(device,byref(new))
##    for field in new._fields_:
##        print field
##        print eval('new.%s'%field[0])
##        state[field[0]]=eval('new.%s'%field[0])
##        print "state[%s]=%s"%(field[0],'new.%s'%field[0])
##    for key,value in state.iteritems():
##        print key,value
    #image
    buffer=c_char_p(''*RESOLUTION_LIST[new.Resolution][0]*RESOLUTION_LIST[new.Resolution][1])
    pointer_FileName=c_char_p('bitmap2.bmp')
    pointer_FilePath=c_char_p(os.path.join(PYMEASURE_ROOT,'Code','BackEnds'))
    new.CatchFrames=1
    new.IsCatchRAW=1
    wrapper.MTUSB_ShowVideoWindow(device,0,0,640,480)
    wrapper.MTUSB_StartFrameGrab(device,100)
   # print pointer_FileName.value
    
    #wrapper.MTUSB_SaveFramesToFiles(device, byref(new),pointer_FilePath,pointer_FileName)
    #wrapper.MTUSB_GetCurrentFrame(device,1,buffer)
    #print buffer
    wrapper.MTUSB_StopFrameGrab(device)
    #wrapper.MTUSB_GetLastBMPFrame(device,pointer_FileName)
    wrapper.MTUSB_StopCameraEngine(device)
    wrapper.MTUSB_UnInitDevice() 
       
def test_camera():
    """ A general test of the camera using code written by Ryan Going"""
    os.chdir(os.path.join(PYMEASURE_ROOT,'Code','BackEnds'))
    cam = windll["MT_USBCamera_SDK_Stdcall.dll"]
    print cam.MTUSB_InitDevice()
    device1 = cam.MTUSB_OpenDevice(0)
    serialpoint=c_char_p(''*20)
    serial=cam.MTUSB_GetSerialNo(device1,serialpoint)
    print serialpoint
    print serial
    print cam.MTUSB_StartCameraEngine(None,device1)
    # Adjust Settings
    print cam.MTUSB_SetAutoExposure(device1,True,False)
    time.sleep(1) # Pause for autoexposure to take effect
    cam.MTUSB_SetAutoExposure(device1,False,False)
    #print cam.MTUSB_ShowVideoWindow(1)
    #print cam.MTUSB_StartFrameGrab(device1,100)
    cam.MTUSB_ShowFrameControlPanel( device1, True, False, "VC++ Example", 8, 8 )        
    time.sleep(5)
#    cam.MTUSB_SetFrameRate(device1,10)
    # Show video
##    print cam.MTUSB_ShowVideoWindow(device1,0,0,640,480)
##    print cam.MTUSB_StartFrameGrab(device1,100)
##    time.sleep(5)
##    cam.MTUSB_StopFrameGrab(device1)
    #Shut everything down
    #cam.MTUSB_StopCameraEngine(device1)
    #cam.MTUSB_UnInitDevice()
    
def test_Gui():
    import wx
    os.chdir(os.path.join(PYMEASURE_ROOT,'Code','BackEnds'))
    cam = windll["MT_USBCamera_SDK_Stdcall.dll"]
    cam.MTUSB_InitDevice()
    device1 = cam.MTUSB_OpenDevice(0)
    #app=wx.App()
    #frame=cam.MTUSB_ShowFrameControlPanel( device1, True, False, "VC++ Example", 8, 8 )
    from ctypes.wintypes import HWND, LPCSTR, UINT
    prototype = WINFUNCTYPE(c_int, HWND, LPCSTR, LPCSTR, UINT)
    paramflags = (1, "hwnd", 0), (1, "text", "Hi"), (1, "caption", None), (1, "flags", 0)
    MessageBox = prototype(("MessageBoxA", windll.user32), paramflags)
    MessageBox()
    #MTUSB_StartCameraEngine( HWND ParentHandle, DEV_HANDLE DevHandle );
    #app.MainLoop()
def test_launch_mightex_application():
    """Tests the launch of the mightex application. Only works on Windows."""
    launch_mightex_application()
#-------------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    test_launch_mightex_application()
    