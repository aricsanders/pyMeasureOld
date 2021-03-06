#-----------------------------------------------------------------------------
# Name:        QE65000Panel.py
# Purpose:     A simple interface for the USB2000 Spectrometer
#
# Author:      Aric Sanders
#
# Created:     2009/10/19
# RCS-ID:      $Id: QE65000Panel.py $
#-----------------------------------------------------------------------------
#Boa:FramePanel:QE65000Panel
""" Base Panel For Simple QE65000 Ocean Optics Spectrometer Interface"""
import time
import os
import wx
import wx.lib.buttons
import wx.lib.plot
from pyMeasure.Code.BackEnds.Instruments import OceanOpticsInstrument
try: 
    import pyMeasure
except:
    print("The topmost pyMeasure folder was not found please make sure that the directory directly above it is on sys.path") 
    raise
#-------------------------------------------------------------------------------
#Constants
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))

[wxID_QE65000PANEL, wxID_QE65000PANELAVERAGES, wxID_QE65000PANELBOXCAR_PIXELS, 
 wxID_QE65000PANELGENBITMAPTEXTTOGGLEBUTTON1, 
 wxID_QE65000PANELINTEGRATION_TIME, wxID_QE65000PANELPANEL1, 
 wxID_QE65000PANELPANEL2, wxID_QE65000PANELPLOTCANVAS1, 
 wxID_QE65000PANELSET_PARAMETERS, wxID_QE65000PANELSINGLE_SPECTRUM, 
 wxID_QE65000PANELSTATICTEXT1, wxID_QE65000PANELSTATICTEXT2, 
 wxID_QE65000PANELSTATICTEXT3, 
] = [wx.NewId() for _init_ctrls in range(13)]

class QE65000Panel(wx.Panel):
    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.panel1, 1, border=2, flag=wx.EXPAND)
        parent.AddWindow(self.plotCanvas1, 5, border=2, flag=wx.EXPAND)
        parent.AddWindow(self.panel2, 1, border=2, flag=wx.EXPAND)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_QE65000PANEL, name=u'QE65000Panel',
              parent=prnt, pos=wx.Point(385, 351), size=wx.Size(762, 502),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(754, 468))

        self.panel1 = wx.Panel(id=wxID_QE65000PANELPANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(754, 66),
              style=wx.TAB_TRAVERSAL)
        self.panel1.SetLabel(u'panel1')
        self.panel1.SetHelpText(u'Settings')
        self.panel1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False,
              u'Tahoma'))

        self.plotCanvas1 = wx.lib.plot.PlotCanvas(id=wxID_QE65000PANELPLOTCANVAS1,
              name='plotCanvas1', parent=self, pos=wx.Point(0, 66),
              size=wx.Size(754, 334), style=0)

        self.panel2 = wx.Panel(id=wxID_QE65000PANELPANEL2, name='panel2',
              parent=self, pos=wx.Point(0, 400), size=wx.Size(754, 66),
              style=wx.TAB_TRAVERSAL)
        self.panel2.SetBackgroundColour(wx.Colour(128, 128, 192))
        self.panel2.SetBackgroundStyle(wx.BG_STYLE_SYSTEM)
        self.panel2.SetHelpText(u'Aquistion')

        self.integration_time = wx.SpinCtrl(id=wxID_QE65000PANELINTEGRATION_TIME,
              initial=0, max=2000000, min=0, name=u'integration_time',
              parent=self.panel1, pos=wx.Point(8, 24), size=wx.Size(160, 21),
              style=wx.SP_ARROW_KEYS)
        self.integration_time.Bind(wx.EVT_SPINCTRL,
              self.OnIntegration_timeSpinctrl,
              id=wxID_QE65000PANELINTEGRATION_TIME)

        self.averages = wx.SpinCtrl(id=wxID_QE65000PANELAVERAGES, initial=0,
              max=100, min=0, name=u'averages', parent=self.panel1,
              pos=wx.Point(184, 24), size=wx.Size(104, 21),
              style=wx.SP_ARROW_KEYS)
        self.averages.SetMinSize(wx.Size(21, 21))
        self.averages.Bind(wx.EVT_SPINCTRL, self.OnAveragesSpinctrl,
              id=wxID_QE65000PANELAVERAGES)

        self.boxcar_pixels = wx.SpinCtrl(id=wxID_QE65000PANELBOXCAR_PIXELS,
              initial=0, max=100, min=0, name=u'boxcar_pixels',
              parent=self.panel1, pos=wx.Point(296, 24), size=wx.Size(72, 21),
              style=wx.SP_ARROW_KEYS)
        self.boxcar_pixels.SetMinSize(wx.Size(42, 21))
        self.boxcar_pixels.Bind(wx.EVT_SPINCTRL, self.OnBoxcar_pixelsSpinctrl,
              id=wxID_QE65000PANELBOXCAR_PIXELS)

        self.single_spectrum = wx.Button(id=wxID_QE65000PANELSINGLE_SPECTRUM,
              label=u'Single Spectrum', name=u'single_spectrum',
              parent=self.panel2, pos=wx.Point(8, 8), size=wx.Size(120, 32),
              style=0)
        self.single_spectrum.Bind(wx.EVT_BUTTON, self.OnButton1Button,
              id=wxID_QE65000PANELSINGLE_SPECTRUM)

        self.staticText1 = wx.StaticText(id=wxID_QE65000PANELSTATICTEXT1,
              label=u'Integration Time (microseconds) ', name='staticText1',
              parent=self.panel1, pos=wx.Point(8, 8), size=wx.Size(158, 13),
              style=0)
        self.staticText1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL,
              False, u'Tahoma'))

        self.staticText2 = wx.StaticText(id=wxID_QE65000PANELSTATICTEXT2,
              label=u'Averages', name='staticText2', parent=self.panel1,
              pos=wx.Point(200, 8), size=wx.Size(47, 13), style=0)

        self.staticText3 = wx.StaticText(id=wxID_QE65000PANELSTATICTEXT3,
              label=u'BoxCar Pixels', name='staticText3', parent=self.panel1,
              pos=wx.Point(296, 8), size=wx.Size(66, 13), style=0)

        self.genBitmapTextToggleButton1 = wx.lib.buttons.GenBitmapTextToggleButton(bitmap=wx.Bitmap(str(os.path.join(PYMEASURE_ROOT,'Settings/Images/Run.png')),
              wx.BITMAP_TYPE_PNG),
              id=wxID_QE65000PANELGENBITMAPTEXTTOGGLEBUTTON1,
              label=u'Continous Acquire', name='genBitmapTextToggleButton1',
              parent=self.panel2, pos=wx.Point(136, 8), size=wx.Size(176, 32),
              style=0)
        self.genBitmapTextToggleButton1.SetToggle(False)
        self.genBitmapTextToggleButton1.Bind(wx.EVT_BUTTON,
              self.OnGenBitmapTextToggleButton1Button,
              id=wxID_QE65000PANELGENBITMAPTEXTTOGGLEBUTTON1)

        self.set_parameters = wx.Button(id=wxID_QE65000PANELSET_PARAMETERS,
              label=u'Set Acquisition Parameters', name=u'set_parameters',
              parent=self.panel1, pos=wx.Point(424, 16), size=wx.Size(160, 31),
              style=0)
        self.set_parameters.Bind(wx.EVT_BUTTON, self.OnSet_parametersButton,
              id=wxID_QE65000PANELSET_PARAMETERS)

        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)
        try:
            self.backend=OceanOpticsInstrument('QE65000')
            self.on_off=0
            inital_state=self.backend.get_state()
        except:
            inital_state={'setIntegrationTime':0,'setScansToAverage':0,'setBoxcarWidth':0}
        self.integration_time.SetValue(inital_state['setIntegrationTime'])
        self.averages.SetValue(inital_state['setScansToAverage'])
        self.boxcar_pixels.SetValue(inital_state['setBoxcarWidth'])

    def OnButton1Button(self, event):
        """ Single Spectra Button"""
        self.update_plot()

    def OnGenBitmapTextToggleButton1Button(self, event):
        self.on_off=not(self.on_off)
        
    def update_plot(self):
        """ Gets a spectrum and draws it the plot"""
        self.current_data=self.backend.get_spectrum()
        data_line = wx.lib.plot.PolyLine(self.current_data, colour='blue', width=1)
        gaphics = wx.lib.plot.PlotGraphics([data_line],
            'QE6500 Spectrometer', "Wavelength(nm)", "Amplitude(arb.)")
        self.plotCanvas1.Draw(gaphics)            

    def OnSet_parametersButton(self, event):
        state_dictionary=self.get_state()
        self.backend.set_state(**state_dictionary)
        
    def get_state(self):
        state_dictionary={}
        state_dictionary['setIntegrationTime']=self.integration_time.GetValue()
        state_dictionary['setScansToAverage']=self.averages.GetValue()
        state_dictionary['setBoxcarWidth']=self.boxcar_pixels.GetValue()
        return state_dictionary

    def OnIntegration_timeSpinctrl(self, event):
        state_dictionary=self.get_state()
        self.backend.set_state(**state_dictionary)
        event.Skip()

    def OnAveragesSpinctrl(self, event):
        state_dictionary=self.get_state()
        self.backend.set_state(**state_dictionary)
        event.Skip()
        
    def OnBoxcar_pixelsSpinctrl(self, event):
        state_dictionary=self.get_state()
        self.backend.set_state(**state_dictionary)
        event.Skip()
        
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None,size=wx.Size(762, 502))
    panel=QE65000Panel(id=1, name=u'QE65000Panel',
              parent=frame, pos=wx.Point(350, 204), size=wx.Size(762, 502),
              style=wx.TAB_TRAVERSAL)
    sizer=wx.BoxSizer()
    sizer.Add(panel,1,wx.EXPAND,2)
    frame.SetSizerAndFit(sizer)
    frame.Show()

    app.MainLoop()


