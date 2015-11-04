#Boa:Frame:Frame1

import wx
from scipy import linspace 
import visa
import pickle

def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1BUTTON2, wxID_FRAME1IVBUTTON, wxID_FRAME1NUMLABEL, 
 wxID_FRAME1NUMSTEPS, wxID_FRAME1SAVEBUTTON, wxID_FRAME1STARTLABEL, 
 wxID_FRAME1STOPLABEL, wxID_FRAME1VOLTSTART, wxID_FRAME1VOLTSTOP, 
] = [wx.NewId() for _init_ctrls in range(10)]

class Frame1(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(421, 252), size=wx.Size(400, 250),
              style=wx.DEFAULT_FRAME_STYLE, title='Simple IV')
        self.SetClientSize(wx.Size(392, 216))

        self.VoltStart = wx.TextCtrl(id=wxID_FRAME1VOLTSTART, name='VoltStart',
              parent=self, pos=wx.Point(16, 40), size=wx.Size(100, 21), style=0,
              value='-1')
        self.VoltStart.SetToolTipString('Start Voltage')

        self.VoltStop = wx.TextCtrl(id=wxID_FRAME1VOLTSTOP, name='VoltStop',
              parent=self, pos=wx.Point(128, 40), size=wx.Size(100, 21),
              style=0, value='1')
        self.VoltStop.SetToolTipString('Stop Voltage')

        self.numSteps = wx.TextCtrl(id=wxID_FRAME1NUMSTEPS, name='numSteps',
              parent=self, pos=wx.Point(240, 40), size=wx.Size(100, 21),
              style=0, value='10')
        self.numSteps.SetToolTipString('Number of Steps')

        self.startLabel = wx.StaticText(id=wxID_FRAME1STARTLABEL,
              label='Start Voltage', name='startLabel', parent=self,
              pos=wx.Point(24, 16), size=wx.Size(80, 21),
              style=wx.SUNKEN_BORDER)

        self.stopLabel = wx.StaticText(id=wxID_FRAME1STOPLABEL,
              label='Stop Voltage', name='stopLabel', parent=self,
              pos=wx.Point(136, 16), size=wx.Size(88, 21),
              style=wx.SUNKEN_BORDER)

        self.numLabel = wx.StaticText(id=wxID_FRAME1NUMLABEL,
              label='Number of Steps', name='numLabel', parent=self,
              pos=wx.Point(240, 16), size=wx.Size(96, 21),
              style=wx.SUNKEN_BORDER)

        self.IVButton = wx.Button(id=wxID_FRAME1IVBUTTON, label='Take IV',
              name='IVButton', parent=self, pos=wx.Point(8, 184),
              size=wx.Size(96, 23), style=0)
        self.IVButton.SetToolTipString('Press to take IV')
        self.IVButton.Bind(wx.EVT_BUTTON, self.OnButton1Button,
              id=wxID_FRAME1IVBUTTON)

        self.button2 = wx.Button(id=wxID_FRAME1BUTTON2,
              label='Plot Current Data', name='button2', parent=self,
              pos=wx.Point(112, 184), size=wx.Size(123, 23), style=0)
        self.button2.Bind(wx.EVT_BUTTON, self.OnButton2Button,
              id=wxID_FRAME1BUTTON2)

        self.saveButton = wx.Button(id=wxID_FRAME1SAVEBUTTON, label='Save Data',
              name='saveButton', parent=self, pos=wx.Point(248, 184),
              size=wx.Size(120, 23), style=0)
        self.saveButton.SetToolTipString('Save Data')
        self.saveButton.Bind(wx.EVT_BUTTON, self.OnsaveButtonButton,
              id=wxID_FRAME1SAVEBUTTON)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnButton1Button(self, event):
        [vStart,vStop,numSteps]=[self.VoltStart.GetValue(),self.VoltStop.GetValue(),self.numSteps.GetValue()]
        vList=self.MakeVList(vStart,vStop,numSteps)
        self.outFile=[]
        self.IntializeKeithley()
        for index,v in enumerate(vList):
            
            self.outFile.append([index,self.WriteVToKeithley(v)])
            visa.instrument("GPIB::22").write("CURR:RANG:AUTO ON")

        self.errorMessage('Done!')
        self.WriteVToKeithley(0)
   
    def OnButton2Button(self, event):
        try:
            self.makePlot(self.outFile)
        except:
            self.errorMessage('An Error in Plotting has Occurred')
            raise
            
    def OnsaveButtonButton(self,event):
        try:
            savedialog=wx.FileDialog(self,'Save Current Data','.','',"*.*",style=wx.FD_SAVE)
            if savedialog.ShowModal()==wx.ID_OK:
                f=open(savedialog.GetPath(),'w')
                for line in self.outFile:
                    f.write(str(line)+'\n')
        except:
            self.errorMessage('An Error in saving the Data has Occurred')
            raise
            
        
            
            
            
            
                    
    def MakeVList(self,Start,Stop,NumSteps):
        """Makes a list of floats given a string or numbers"""
        try:
            if (type(Start)!=float or type(Stop)!=float or type(NumSteps)!=float):
                [Start,Stop,NumSteps]=map(lambda x: float(x),[Start,Stop,NumSteps])
            vArray=linspace(Start,Stop,NumSteps)
            vList=vArray.tolist()
            return vList
        except:
            self.errorMessage('An Error in MakeVlist has Occurred')
    
    
    def IntializeKeithley(self,GPIBAddress=22):
        """Sends intialization string to Keithley picoammeter"""
        try:
            intialize_list=["*RST","FUNC 'CURR'","SYST:ZCH:STAT ON",
            "CURR:RANG 2E-4","INIT","SYST:ZCOR:STAT OFF","SYST:ZCOR:ACQ",
            "SYST:ZCH:STAT OFF","SYST:ZCOR ON","SOUR:VOLT:STAT ON",
            "FORM:ELEM ALL","CURR:RANG:AUTO ON"]
            
            for command in intialize_list:
                visa.instrument("GPIB::"+str(GPIBAddress)).write(command)
            # TODO: Check for Instrument Errors
            
        except:
            self.errorMessage('An error intializing the keithley has occurred')
            
    def WriteVToKeithley(self,voltage):
        """Sets the Keithley to a specified voltage and returns a single reading"""
        try:
            wx.Sleep(.2)
            visa.instrument("GPIB::22").write("SOUR:VOLT "+str(voltage))
            wx.Sleep(.2)
            return visa.instrument("GPIB::22").ask("READ?")
        except:
            self.errorMessage('An error talking to the keithley has occurred')
            
    def errorMessage(self,error='Error'):
        """A standard error dialog"""
        errordlg=wx.MessageDialog(self,error,'Error',wx.ICON_ERROR)
        errordlg.ShowModal()
           
    def makePlot(self,inFile):
        """ Makes a plot using matplotlib"""
       # TODO: make plot update continously
        
        try:
            import matplotlib.pyplot as plt
                      
            voltList=[map(lambda x: float(x.strip('A')),linex[1].split(','))[3] for linex in inFile]
            currentList=[map(lambda x: float(x.strip('A')),linex[1].split(','))[0] for linex in inFile]
            plt.plot(voltList,currentList)
            plt.xlabel("Voltage (V)")
            plt.ylabel("Current (A)")
            plt.show()
        except:
            self.errorMessage('An Error in the function makePlot has occurred')
           
           
       
