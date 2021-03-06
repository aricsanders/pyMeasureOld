#-----------------------------------------------------------------------------
# Name:        MatplotlibWxPanel.py
# Purpose:     To be a plugin advanced plot panel for pyMeasure
#
# Author:      Aric Sanders
#
# Created:     2010/12/18
# RCS-ID:      $Id: MatplotlibWxPanel.py $
# Copyright:   (c) 2009
# Licence:     GPL
#-----------------------------------------------------------------------------
#!/usr/bin/env python
"""
An example of how to use wx or wxagg in an application with a custom
toolbar, Modified to work inside of BOA by AWS. Serves as an advanced plot window for pyMeasure.
"""

#-------------------------------------------------------------------------------
# Standard Imports
import wx


#-------------------------------------------------------------------------------
# Third Party imports
# Used to guarantee to use at least Wx2.8 Was removed.

try:
    from numpy import arange, sin, pi

    import matplotlib
    import matplotlib.ticker as ticker
    matplotlib.use('WXAgg')
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
    from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg

    from matplotlib.backends.backend_wx import _load_bitmap
    from matplotlib.figure import Figure
    from numpy.random import rand

except:
    print "Please make sure matplotlib package is installed and in sys.path"
try:
    import pyMeasure.Code.DataHandlers.Measurements
except: 
    print "import of pyMeasure.Code.DataHandlers.Measurements failed"
    
#-------------------------------------------------------------------------------
# Constants
MEASUREMENT_ROOT=r'C:\Documents and Settings\sandersa\My Documents\Share\pyMeasure\Data\Measurements'

    
#-------------------------------------------------------------------------------
# Class Definitions


# This class was ripped from an example on the matplotlib site
class MyNavigationToolbar(NavigationToolbar2WxAgg):
    """
    Extend the default wx toolbar with your own event handlers
    """
    ON_CUSTOM = wx.NewId()
    def __init__(self, canvas, cankill):
        NavigationToolbar2WxAgg.__init__(self, canvas)

        # for simplicity I'm going to reuse a bitmap from wx, you'll
        # probably want to add your own.wx.ART_FOLDER_OPEN 
        #wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN) is the stock icons command
        self.AddSimpleTool(self.ON_CUSTOM, wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN),
                           'Plot measurement', 'Plot an XML data file')
        wx.EVT_TOOL(self, self.ON_CUSTOM, self._on_custom)
        
        self.AddSimpleTool(self.ON_CUSTOM, wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN),
                           'Click me', 'Activate custom contol')
        #wx.EVT_TOOL(self, self.ON_CUSTOM, self._on_custom)        

    def _on_custom(self, evt):
        # add some text to the axes in a random location in axes (0,1)
        # coords) with a random color

##        # get the axes
##        ax = self.canvas.figure.axes[0]
##
##        # generate a random location can color
##        x,y = tuple(rand(2))
##        rgb = tuple(rand(3))
##
##        # add the text and draw
##        ax.text(x, y, 'You clicked me',
##                transform=ax.transAxes,
##                color=rgb)
##        self.canvas.draw()
        # This is a stub out for a file chooser to plot.
        dlg = wx.FileDialog(self, 'Choose a file', MEASUREMENT_ROOT, '', '*.*', wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                try:
                    data_sheet=pyMeasure.Code.DataHandlers.Measurements.DataTable(
                    filename)
                    self.canvas.figure.clear()
                    self.axes = self.canvas.figure.add_subplot(111)
                    ax = self.canvas.figure.axes[0]
                    # This needs to be generalized with a chooser so that things with
                    # lots of columns can be plotted
                    #print data_sheet.get_attribute_names()
                    
                    if 'Current' in data_sheet.get_attribute_names():
                        y_name='Current'
                    if 'Voltage' in data_sheet.get_attribute_names():
                        x_name='Voltage'
                            
                    else:
                        y_name=data_sheet.get_attribute_names()[0]
                        x_name=data_sheet.get_attribute_names()[1]
                    params={'axes.labelsize': 18,'text.fontsize': 18,
                    'legend.fontsize': 18,            
                    'xtick.labelsize': 18,
                    'ytick.labelsize': 18,
                    }

                    matplotlib.rcParams.update(params)
                    self.axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=True))
                    self.axes.yaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=True))
                    #print x_name,y_name
                    self.axes.set_xlabel(x_name,fontsize=20)
                    self.axes.set_ylabel(y_name,fontsize=20)
                    ax.plot(data_sheet.to_list(x_name),data_sheet.to_list(y_name))
                    self.canvas.draw()
                    # Set the Title
                    try:
                        self.Parent.Parent.SetTitle(data_sheet.path)
                    except:
                        pass
                    self.Update()
                except:
                    
                    pass
        finally:
            dlg.Destroy()
        evt.Skip()

# In the original example this was a frame, I have modified it to work with BOA
class MatplotlibWxPanel(wx.Panel):
    """ This is a wx.Panel that shows a plot with a custom toolbar"""
    def __init__(self, parent, id, pos, size, style, name):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)

        self.SetBackgroundColour(wx.NamedColour("WHITE"))

        self.figure = Figure(figsize=(5,4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        t = arange(0.0,3.0,0.01)
        s = sin(2*pi*t)

        self.axes.plot(t,s)

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)
        # Capture the paint message
        wx.EVT_PAINT(self, self.OnPaint)

        self.toolbar = MyNavigationToolbar(self.canvas, True)
        self.toolbar.Realize()
        if wx.Platform == '__WXMAC__':
            # Mac platform (OSX 10.3, MacPython) does not seem to cope with
            # having a toolbar in a sizer. This work-around gets the buttons
            # back, but at the expense of having the toolbar at the top
            self.SetToolBar(self.toolbar)
        else:
            # On Windows platform, default window size is incorrect, so set
            # toolbar width to figure width.
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            # By adding toolbar in sizer, we are able to put it at the bottom
            # of the frame - so appearance is closer to GTK version.
            # As noted above, doesn't work for Mac.
            self.toolbar.SetSize(wx.Size(fw, th))
            self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)

        # update the axes menu on the toolbar
        self.toolbar.update()
        self.SetSizer(self.sizer)
        self.Fit()


    def OnPaint(self, event):
        self.canvas.draw()
        event.Skip()

#-------------------------------------------------------------------------------
# Script Definitions




if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None,size=wx.Size(900, 800))
    panel=MatplotlibWxPanel(id=1, name=u'MatplotlibWxPanel',
              parent=frame, pos=wx.Point(350, 204), size=wx.Size(200, 800),
              style=wx.TAB_TRAVERSAL)
    sizer=wx.BoxSizer()
    sizer.Add(panel,1,wx.EXPAND,2)
    frame.SetSizerAndFit(sizer)
    frame.SetSize(wx.Size(1000, 800))
    frame.Show()
    app.MainLoop()