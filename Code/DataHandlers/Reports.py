#-----------------------------------------------------------------------------
# Name:        Reports.py
# Purpose:     To generate HTML reports of data
#
# Author:      Aric Sanders
#
# Created:     2011/02/18
# RCS-ID:      $Id: Reports.py $
# Copyright:   (c) 2009
# Licence:     GPL
#-----------------------------------------------------------------------------
""" Reports generates HTML files and plots after data aquistion."""
#-------------------------------------------------------------------------------
# Standard Imports-- All in the python standard library


import os                                          # path functions etc. 
import sys                                         # System 
import re                                          # For regular expressions     
import datetime                                    # For timestamping     
import xml.dom                                     # Xml document handling 
import xml.dom.minidom                             # For xml parsing
from xml.dom.minidom import getDOMImplementation   # Making blank XML documents 
from types import *                                # to allow input testing
import math
#-------------------------------------------------------------------------------
# Third Party Imports
try: 
    import pyMeasure
except:
    print("The topmost pyMeasure folder was not found please make sure that the directory directly above it is on sys.path") 
    raise
try:
    import matplotlib.pyplot as plt
    import matplotlib
except:
    print "Needs Matplotlib to be installed to make plots, please load it"
    raise

try:
    from lxml import etree
    XSLT_CAPABLE=1
except:
    print("Transformations using XSLT are not available please check the lxml module")
    XSLT_CAPABLE=0
    pass

try:
    from pyMeasure.Code.Misc.Alias import *
    METHOD_ALIASES=1
except:
    METHOD_ALIASES=0
    pass
try: 
    import pyMeasure
    import pyMeasure.Code.DataHandlers.Measurements
    import pyMeasure.Code.DataHandlers.States
except:
    print("""This module needs pyMeasure to function. The folder directly above
    PYMEASURE_ROOT must be on sys.path""")
    raise
try: 
    import scipy
    import scipy.optimize
    import scipy.stats
    #import scipy.linspace
except:
    raise
    print("""This module requires scipy to be on sys.path to do fits""") 
#-------------------------------------------------------------------------------
# Module Constants
PYMEASURE_ROOT=os.path.dirname(os.path.realpath(pyMeasure.__file__))
MEASUREMENTS_DIRECTORY=os.path.join(PYMEASURE_ROOT,'Data','Measurements').replace('\\','/')
REPORTS_DIRECTORY=os.path.join(PYMEASURE_ROOT,'Data','Reports').replace('\\','/')
K=1.3806503*10**-23 #Boltzman Constant in mks
q=1.60218*10**-19 #electron charge in mks
T=302.9146  #temperature in kelvin, changed to melting point of gallium
RICHARDSON=26.4*10**4
BETA=q/(K*T)
#-------------------------------------------------------------------------------
# Module Functions

def convert_datetime(ISO_datetime_string,format_string='%m/%d/%Y at %H:%M:%S'):
    "Converts from long ISO format 2010-05-13T21:54:25.755000 to something reasonable"
    #strip any thing smaller than a second
    time_seconds=ISO_datetime_string.split('.')[0]
    
    #then get it into a datetime format
    time_datetime=datetime.datetime.strptime(time_seconds,"%Y-%m-%dT%H:%M:%S")
    return time_datetime.strftime(format_string)
def diode_function(a,I):
    """ a[0]=ideality factor,a[1]=beta,a[2]=series resistance"""
    
    return (a[0]/BETA)*math.log(I*1/a[1])-I*a[2]
    
def fit(function,xdata,ydata,a0):
    fit_dictionary={}
    error_function=lambda a, xdata, ydata:function(a,xdata)-ydata
    a,succes=scipy.optimize.leastsq(error_function, a0,args=(xdata,ydata))
    return a


#-------------------------------------------------------------------------------
# Module Classes

class Report():
    """ An xml sheet describing a large data set."""
    def __init__(self):
        pass
class SandiaReport(Report):
    """ Class to handle the data taken at Sandia on 02/2011"""
    def __init__(self):
        """ Intializes the SandiaReport Class"""
        # First we need to locate the data
        all_measurements=os.listdir(MEASUREMENTS_DIRECTORY)
        # filter for dates and such
        self.data_files=[]
        for file in all_measurements:
            if re.search('021411|021511|021611|021711|051013',file) and re.search('xml',file,re.IGNORECASE):
                self.data_files.append(file)    
        self.device_pads=['II 1-5','III 7-6','III 8-3','II1-5','III 5-2','I 2-8',
        'I 3-4','IV 4-3','III 7-5', 'III 8-4',' 5-2']
        self.beta=q/(K*T)
    def load_data_files(self,device_pad,*filter_list):
        """ Loads data with certain characteristics"""
        files_to_load=[]
        #print self.data_files
        for file in self.data_files:
            path=os.path.join(MEASUREMENTS_DIRECTORY,file)
            temp_load=pyMeasure.Code.DataHandlers.Measurements.DataTable(path)
            
            if re.search(device_pad,temp_load.get_header()):
                files_to_load.append(file)
        filtered_files=[]
        for filter in filter_list:
            for file in files_to_load:
                if re.search(filter,file):
                 filtered_files.append(file)
        files_to_load=filtered_files
        if re.search('all',device_pad,re.IGNORECASE):
           files_to_load=self.data_files 
         
        #print files_to_load,filtered_files
        self.loaded_files=[]
        for file in files_to_load:
            path=os.path.join(MEASUREMENTS_DIRECTORY,file)
            self.loaded_files.append(pyMeasure.Code.DataHandlers.Measurements.DataTable(path))
    def fit_diode_parameters(self,data_table,**fit_options):
        """ Fits parameters in data files"""
        options={'v_min_R_fit':.6,'v_max_R_fit':'max','v_max_log_I_fit':.6,'v_max_cheung_fit':.6,
        'print_information':True,'print_R':False,'contact_area':840*10**-9*210*10**-9,
        'plot_R_fit':True,'plot_ln_I_fit':True,'plot_cheung_fit':True}
        try:
            for key,value in fit_options.iteritems():
                options[key]=value
        except:
            pass
        # First we estimate R using the highest values and doing a linear fit
        R_voltage_list=[]
        R_current_list=[]
        f=lambda x:float(x)
        g=lambda x:x.strip('A')
        voltage_list=map(g,data_table.to_list('Voltage'))
        current_list=map(g,data_table.to_list('Current'))
        voltage_list=map(f,voltage_list)
        current_list=map(f,current_list)
        try:
            if re.search('max',options['v_max_R_fit'],re.IGNORECASE):
                options['v_max_R_fit']=max(voltage_list)
            if re.search('max',options['v_min_R_fit'],re.IGNORECASE):
                string=options['v_min_R_fit']
                options['v_min_R_fit']=max(voltage_list)-float(string.split('-')[-1])
                #print options['v_min_R_fit']
            if re.search('min',options['v_min_R_fit'],re.IGNORECASE):
                options['v_min_R_fit']=min(voltage_list)
        except:pass  
        for index,v in enumerate(voltage_list):
            if v>options['v_min_R_fit'] and v<options['v_max_R_fit']:
                R_voltage_list.append(float(v))
                R_current_list.append(float(current_list[index]))
        [a,b,ar,br,err]=scipy.stats.linregress(R_voltage_list,R_current_list)
        resistance=1/a
        
        # Now we use the method found in Cheung APL (vol. 49, (2) July 1986)to calculate n
        # first calculate delta V over delta ln(J)
        delta_vlnJ_list=[]
        current_density_list=[]
        for index,v in enumerate(voltage_list):
            if v>3*K*T/q and index<len(voltage_list)-2 and v<options['v_max_cheung_fit']:
                try:
                    delta_vlnJ=(voltage_list[index+1]-voltage_list[index])/(
                    math.log(current_list[index+1]/options['contact_area'])
                    -math.log(current_list[index]/options['contact_area']))
                
                    delta_vlnJ_list.append(delta_vlnJ)
                    current_density_list.append((current_list[index+1]+
                    current_list[index])/(2.0*options['contact_area']))
                except:pass
        try:
            [resistance_area,n_div_beta,ra_error,nerror,
            delta_fit_error]=scipy.stats.linregress(current_density_list,delta_vlnJ_list)
        except:
            [resistance_area,n_div_beta,ra_error,nerror,
            delta_fit_error]=[0,0,0,0,0]
        #Ideality factor
        n=n_div_beta*self.beta 
        # Now for the barrier height
        # calculate H=V-(n/beta)ln(J/(RICHARDSON*T^2))
        H_list=[]
        current_density_list_2=[]
        for index,v in enumerate(voltage_list):
           if v>3*K*T/q and index<len(voltage_list)-1 and v<options['v_max_cheung_fit']:
                try:
                    J=(current_list[index])/(options['contact_area'])
                    H_list.append(v-(n/self.beta)*math.log(J/(RICHARDSON*T**2)))
                    current_density_list_2.append(J)
                except:pass
        #print H_list,current_density_list_2
        try:
            [resistance_area_2,n_barrier,ra2_error,barrier_error,
            H_fit_error]=scipy.stats.linregress(current_density_list_2,H_list)
        except:
            [resistance_area_2,n_barrier,ra2_error,barrier_error,
            H_fit_error]=[0,0,0,0,0]              
        # And now to just find n and barrier with ln(I)=ln(contact area*RICHARDSON*T^2)
        # +-Barrier/kT + qV/nkT
        ln_I_list=[]
        ln_I_voltage_list=[]
        for index,v in enumerate(voltage_list):
            if v>3*K*T/q and v<options['v_max_log_I_fit']:
                try:
                    ln_I_list.append(math.log(current_list[index]))
                    ln_I_voltage_list.append(v)
                except:pass
        
        
        
        
        try:
            [slope_ln_I,intercept_ln_I,r_ln_I,double_sided_prob_ln_I,
            standard_error_ln_I]=scipy.stats.linregress(ln_I_voltage_list,ln_I_list)
            n_from_ln_I=self.beta/slope_ln_I
            barrier_from_ln_I=1/self.beta*(-intercept_ln_I+
            math.log(options['contact_area']*RICHARDSON*T**2))
        except: 
            [slope_ln_I,intercept_ln_I,r_ln_I,double_sided_prob_ln_I,
            standard_error_ln_I]=[0,0,0,0,0]
        
        
        if options['print_R']:
            print 'Resistance is %4g ohms \n'%(1/a)              
        if options['print_information']:
            print "Voltage's between %s and %s being anlayzed"%(options['v_min_R_fit'],options['v_max_R_fit'])
            print 'Number of points in Fit: %s'%len(R_voltage_list)
            print 'Fit Equation is I = %s *voltage + %s'%(a,b)
            print 'Fit Error: %s'%(err)
            print 'Resistance is %4g ohms'%(1/a)
            print 'Error in the fit is: r:%4g,2 tailed probabilty: %4g,Standard Error: %4g'%(ar,br,err)
            print '\n'
            print 'Number of points in Cheung fit:%s'%len(delta_vlnJ_list)
            print 'Assumed contact area: %4g meters squared'%options['contact_area']
            print 'Fitted resistance area product from delta V divided by delta ln J:' 
            print 'Resistance * Area: %4g'%resistance_area
            print 'Yielding a fitted resistance: %4g Ohms'%(resistance_area/options['contact_area'])
            print 'The Resistance * Area divided by linear fit resistance is:%4g'%(resistance_area*a)
            print 'Fitted n divided by beta:%4g'%n_div_beta
            print 'Yielding a ideality factor n: %4g'%(n_div_beta*self.beta)
            print 'Error in the fit is: r:%4g,2 tailed probabilty: %4g,Standard Error: %4g'%(ra_error,nerror,delta_fit_error)
            print '\n'
            print 'Number of points in H function fit:%s'%len(H_list)
            print 'Assumed contact area: %4g meters squared'%options['contact_area']
            print 'Fitted resistance area product from H function fit:' 
            print 'Resistance * Area: %4g'%resistance_area_2
            print 'Yielding a fitted resistance: %4g Ohms'%(resistance_area_2/options['contact_area'])
            print 'The Resistance * Area divided by linear fit resistance is:%4g'%(resistance_area_2*a)
            print 'The calculated barrier is: %4g'%(n_barrier/n)
            print 'Error in the fit is: r:%4g,2 tailed probabilty: %4g,Standard Error: %4g'%(ra2_error,barrier_error,H_fit_error)
            print '\n'
            try:
                print 'The number of points in log I fit:%s'%len(ln_I_list)
                print ' Voltages from %4g to %4g are analyzed'%(3/self.beta,max(ln_I_voltage_list))
                print 'n from fit of log I is: %s'%n_from_ln_I
                print 'Barrier from fit of log I is %4g'%barrier_from_ln_I
                print 'Error in the fit is: r:%4g,2 tailed probabilty: %4g,Standard Error: %4g'%(r_ln_I,double_sided_prob_ln_I,standard_error_ln_I)
            except:
                print 'Log I fit failed'
                
        
        try:
            out={'Linear Fit Resistance':resistance,
            'Delta Fit Resistance':resistance_area,'Ideality Factor':n,'Barrier':n_barrier/n,'a':a,'b':b,
            'slope_ln_I':slope_ln_I,'intercept_ln_I':intercept_ln_I}
        except:
            out={'Linear Fit Resistance':resistance,'Ideality Factor':0,'Barrier':0}
        return out
    def plot(self,data_table,**options):
        """ Plots a data table IV"""
        options={'plot_fits':'all'}
        f=lambda x:float(x)
        voltage_list=map(f,data_table.to_list('Voltage'))
        current_list=map(f,data_table.to_list('Current'))

        try:
            
            import matplotlib.pyplot as plt
            import matplotlib
            import matplotlib.ticker as ticker
            diode_parameters=self.fit_diode_parameters(data_table,**{'v_min_R_fit':'max-4','v_max_R_fit':'max','print_R':True,'print_information':False})
            x=scipy.linspace(min(voltage_list)+1,max(voltage_list)+.1,100)
            fit_x=x.tolist()
            fit_y=[diode_parameters['a']*v + diode_parameters['b'] for v in fit_x]
            params={
            'axes.labelsize': 24,
            'text.fontsize': 24,
            'legend.fontsize': 24,
            'xtick.labelsize': 24,
            'ytick.labelsize': 24,
            'figure.figsize':(10,7.5),
            'axes.formatter.limits':(2,-2)}
            
            matplotlib.rcParams.update(params)    
            
            plt.hold(True)          
            plt.plot(voltage_list,current_list,lw='3')
            plt.plot(fit_x,fit_y,lw='2',color='k')
            plt.xlabel("Voltage (V)")
            plt.ylabel("Current (A)")
            
            plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))
            #plt.show()
        except:
            raise
            print('An Error in the function plot has occurred')
    def plot_ln_I(self,data_table,**options):
        """ Plots a data table IV"""
        options={'plot_fits':'all'}
        f=lambda x:float(x)
        voltage_list=map(f,data_table.to_list('Voltage'))
        current_list=map(f,data_table.to_list('Current'))
        ln_I_list=[]
        ln_I_voltage_list=[]
        for index,v in enumerate(voltage_list):
            if v>3*K*T/q :
                try:
                    ln_I_list.append(math.log(current_list[index]))
                    ln_I_voltage_list.append(v)
                except:pass        
        try:
            
            import matplotlib.pyplot as plt
            import matplotlib
            
            params={
            'axes.labelsize': 24,
            'text.fontsize': 24,
            'legend.fontsize': 24,
            'xtick.labelsize': 24,
            'ytick.labelsize': 24,
            'figure.figsize':(10,7.5)}

            matplotlib.rcParams.update(params)    
            
            diode_parameters=self.fit_diode_parameters(data_table)
            x=scipy.linspace(min(ln_I_voltage_list),max(ln_I_voltage_list),100)
            fit_x=x.tolist()
            fit_y=[diode_parameters['slope_ln_I']*v + diode_parameters['intercept_ln_I'] for v in fit_x]
            plt.plot(fit_x,fit_y,lw='4',color='b')
            plt.hold(True)          
            plt.plot(ln_I_voltage_list,ln_I_list,lw='4',color='r')
            plt.xlabel("Voltage (V)")
            plt.ylabel("ln(Current)")
            plt.show()
        except:
            raise
            print('An Error in the function plot has occurred')
    def plot_cheung_fits(self,data_table,**options):
        """ Plots a result of chueng fit for diodes"""
        # These are the default options, I need to change the code so it does not overide the ones passed
        defaults={'plot_fits':'all','v_min_R_fit':.6,'v_max_R_fit':'max','v_max_log_I_fit':.6,'v_max_cheung_fit':.6,
        'print_information':True,'contact_area':840*10**-9*210*10**-9,
        'plot_R_fit':True,'plot_ln_I_fit':True,'plot_cheung_fit':True,'show_text':True}
        
        # This is a general pattern for adding a lot of options
        # The next more advanced thing to do is retrieve defaults from a settings file
        all_options={}
        for key,value in defaults.iteritems():
            all_options[key]=value
        for key,value in options.iteritems():
            all_options[key]=value
        options=all_options    
        
        f=lambda x:float(x)
        voltage_list=map(f,data_table.to_list('Voltage'))
        current_list=map(f,data_table.to_list('Current'))
        
        # Now we use the method found in Cheung APL (vol. 49, (2) July 1986)to calculate n
        # first calculate delta V over delta ln(J)
        delta_vlnJ_list=[]
        current_density_list=[]
        for index,v in enumerate(voltage_list):
            if v>3*K*T/q and index<len(voltage_list)-2 and v<options['v_max_cheung_fit']:
                try:
                    delta_vlnJ=(voltage_list[index+1]-voltage_list[index])/(
                    math.log(current_list[index+1]/options['contact_area'])
                    -math.log(current_list[index]/options['contact_area']))
                
                    delta_vlnJ_list.append(delta_vlnJ)
                    current_density_list.append((current_list[index+1]+
                    current_list[index])/(2.0*options['contact_area']))
                except:pass
        [resistance_area,n_div_beta,ra_error,nerror,
        delta_fit_error]=scipy.stats.linregress(current_density_list,delta_vlnJ_list)
        #Ideality factor
        n=n_div_beta*self.beta 
        # Now for the barrier height
        # calculate H=V-(n/beta)ln(J/(RICHARDSON*T^2))
        H_list=[]
        current_density_list_2=[]
        for index,v in enumerate(voltage_list):
           if v>3*K*T/q and index<len(voltage_list)-1 and v<options['v_max_cheung_fit']:
                try:
                    J=(current_list[index])/(options['contact_area'])
                    H_list.append(v-(n/self.beta)*math.log(J/(RICHARDSON*T**2)))
                    current_density_list_2.append(J)
                except:pass
        #print H_list,current_density_list_2
        [resistance_area_2,n_barrier,ra2_error,barrier_error,
        H_fit_error]=scipy.stats.linregress(current_density_list_2,H_list)
        barrier=(n_barrier/n)   
        voltage_list=map(f,data_table.to_list('Voltage'))
        current_list=map(f,data_table.to_list('Current'))
        ln_I_list=[]
        ln_I_voltage_list=[]
        for index,v in enumerate(voltage_list):
            if v>3*K*T/q :
                try:
                    ln_I_list.append(math.log(current_list[index]))
                    ln_I_voltage_list.append(v)
                except:pass        
        try:
            

            
            params={
            'axes.labelsize': 24,
            'text.fontsize': 24,
            'legend.fontsize': 24,
            'xtick.labelsize': 24,
            'ytick.labelsize': 24,
            'figure.figsize':(10,7.5)}

            matplotlib.rcParams.update(params)  
            
            diode_parameters=self.fit_diode_parameters(data_table)
            x=scipy.linspace(min(current_density_list_2),max(current_density_list_2),100)
            fit_x=x.tolist()
            fit_y=[resistance_area_2*v + n_barrier for v in fit_x]
            plt.figure(1)
            plt.plot(fit_x,fit_y,lw='4',color='k')
            plt.hold(True)          
            plt.plot(current_density_list_2,H_list,ls='None',marker='s',color='r',ms=15)
        
            plt.xlabel("Current Density (A/m2)")
            plt.ylabel("H(Volts)")
            plt.figure(2)
            #ax_2=plt.axes().twinx()
            fit_y2=[resistance_area*v + n_div_beta for v in fit_x]
            
            plt.plot(current_density_list,delta_vlnJ_list,ls='None',marker='s',color='r',ms=15)
            plt.plot(fit_x,fit_y2,lw='4',color='k')
            plt.xlabel("Current Density (A/m2)")
            plt.ylabel("J*Ln(V)")
##            if options['show_text']:
##                barrier_text=' Fitted barrier: %s, r squared:%s '%(barrier,ra2_error)
##                n_text=' Fitted ideality factor: %s, r squared %s'%(n,ra_error)
##                plot_text=barrier_text+'\n'+n_text
##                ax_2.text(0, 1, 'Test', fontsize=18, ha='center', va='top')
##                print "text added"

            
            plt.show()
        except:
            print('An Error in the function plot has occurred')
            raise
class AurigaReport(SandiaReport):
    pass
#-------------------------------------------------------------------------------
# Module Scripts

#TODO: Make a filter to pass to the script
def make_notes_sheet_robot():
    """ Makes a sheet of notes from measurements folder"""
    os.chdir(MEASUREMENTS_DIRECTORY)
    files=os.listdir(MEASUREMENTS_DIRECTORY)
    os.chdir(REPORTS_DIRECTORY)
    name=pyMeasure.Code.Misc.Names.auto_name(
            'Measurements','Notes',
            REPORTS_DIRECTORY)
    name=name.replace('xml','txt')
    text=''
    for file in files:
        if re.search('xml',file):
            path=os.path.join(MEASUREMENTS_DIRECTORY,file)
            measurement=pyMeasure.Code.DataHandlers.Measurements.DataTable(file_path=path)
            try:
                
                
                print file
                date=measurement.document.getElementsByTagName('Date')[0].firstChild.nodeValue
                out=measurement.get_header()
                date=convert_datetime(date)
                print out
                text=text+file+'\n'+date+'\n'+out+'\n'
            except:pass
    out_file=open(name,'w')
    out_file.write(text)
    out_file.close()
def test_SandiaReport():
    "Tests the SandiaReport Class"
    report=SandiaReport()
    report.load_data_files('III 7-5')
    #print len(report.loaded_files)
    for file in report.loaded_files:
        data=file
        date=data.document.getElementsByTagName('Date')[0].firstChild.nodeValue
        out=data.get_header()
        date=convert_datetime(date)
        print '*'*80
        
        print '\n'
        try:
            print 'Analyzing file: %s'%data.path
            print 'Time data was taken: %s'%date
            print data.document.getElementsByTagName('Name')[0].firstChild.nodeValue
            print data.document.getElementsByTagName('Notes')[0].firstChild.nodeValue
            print 'R: %s Ohms'%data.document.getElementsByTagName('Resistance')[0].firstChild.nodeValue
            R=report.fit_diode_parameters(data,**{'v_min_R_fit':.3,'v_max_log_I_fit':.4})
        except:pass
        print '_'*80
    
def test_plots(**options):
    report=SandiaReport()
    default_options={'files':['50','51','52','77','78','79','80','81'],'device':'III 7-5'}
    user_options=default_options
    for key,value in options.iteritems():
        user_options[key]=value
    report.load_data_files(user_options['device'],*user_options['files'])
    for index,file in enumerate(report.loaded_files):
        print file.path
        plt.hold(1)
        report.plot(file)
    plt.show()
    
def test_fit():
    report=SandiaReport()
    report.load_data_files('III 7-5','78')
    for file in report.loaded_files:
        print file.path
    report.plot(report.loaded_files[0])
    voltage_list=report.loaded_files[0].to_list('Voltage')
    current_list=report.loaded_files[0].to_list('Current')
    a=[2,10**-8,10000]
    fit_results=fit(diode_function,current_list,voltage_list,a)
    print fit_results
    
def plot_n_barrier_vs_R_script(**options):
    """ Automatically cycles through all the data from sandia and plots a two axis plot of R,n, and Phi"""
    options={'plot_type':'scatter'}
    
        
    report=SandiaReport()
    n_list=[]
    R_list=[]
    barrier_list=[]
    report.load_data_files('all')
    for file in report.loaded_files:
        diode_parameters=report.fit_diode_parameters(file,**{'print_information':False})
        [n,R,barrier]=[diode_parameters['Ideality Factor'],
        diode_parameters['Linear Fit Resistance'],diode_parameters['Barrier']]
        # Need to filter out- Linear IV, #IND, and IV's under ebeam 
        try: 
            n=float(n)
            R=float(R)
            barrier=float(barrier)
            if 10**11>R>0 and 0< barrier <10 and 0<n<100:
                n_list.append(n)
                R_list.append(R)
                barrier_list.append(barrier)
        except:pass
    try:
        import math
        import numpy
            
        params={
            'axes.labelsize': 24,
            'text.fontsize': 24,
            'legend.fontsize': 24,
            'xtick.labelsize': 24,
            'ytick.labelsize': 24,
            'figure.figsize':(10,7.5)}

        matplotlib.rcParams.update(params)  
            
            
        if re.search('scatter',options['plot_type']):
            plt.semilogx(R_list,barrier_list,ls='None',marker='s',color='r',ms=15)
            #plt.xlabel("Resistance (Ohms)")
            #plt.ylabel("Barrier (V)")
            
            ax_2=plt.axes().twinx()
            ax_2.loglog(R_list,n_list,ls='None',marker='^',color='b',ms=15)
            
            #ax_2.yaxis.label("Ideality Factor")
        if re.search('histogram|hist',options['plot_type']):
            plt.figure(1)
            plt.hist(barrier_list,facecolor='red')
            #plt.xlabel("Resistance (Ohms)")
            #plt.ylabel("Barrier (V)")
            plt.figure(2)
            #ax_2=plt.axes().twiny()
            plt.hist(n_list, facecolor='blue')
            plt.figure(3)
            plt.hist(R_list)
            #ax_2.yaxis.label("Ideality Factor")
        if re.search('loghist|log',options['plot_type']):
            #Barrier Plot
            plt.figure(1)
            log_barrier_list=[math.log10(barrier) for barrier in barrier_list]
            plt.hist(log_barrier_list,facecolor='red')
            # Ideality Plot
            plt.figure(2)
            log_n_list=[math.log10(n) for n in n_list]
            plt.hist(log_n_list, facecolor='blue')
            
            #Resistance Plot
            plt.figure(3)
            log_R_list=[math.log10(R) for R in R_list]
            plt.hist(log_R_list)
  
        n_array=numpy.array(n_list)
        R_array=numpy.array(R_list)
        barrier_array=numpy.array(barrier_list)
        print 'The number of measurements analyzed is: %s'%(len(n_list))
        print " The mean barrier is: %s"%(numpy.mean(barrier_array))+" +- %s"%(numpy.std(barrier_array))
        print " The median barrier is: %s"%(numpy.median(barrier_array))
        print " The mean Reistance is: %s Ohms"%(numpy.mean(R_array))+" +- %s Ohms"%(numpy.std(R_array))
        print " The median Reistance is: %s Ohms"%(numpy.median(R_array))
        print " The mean ideality factor is: %s "%(numpy.mean(n_array))+" +- %s V"%(numpy.std(n_array))
        print " The median ideality factor is: %s "%(numpy.median(n_array))
        plt.show()
    except:
        print "Error in plot has occurred"
        raise
def analyze_ebeam_pt_lead_script(**options):
    """ Analyzes data taken on 05102013 """
    report=AurigaReport()
    default_options={'print_R':False,'show_notes':True,'print_information':False,'v_min_R_fit':'max-5','v_max_R_fit':'max','print_plot_data':True,
    'print_path':True}
    user_options=default_options
    for key,value in options.iteritems():
        user_options[key]=value
    plot_data=[] 
    R_list=[]    
    #Distance inside to inside taken from image 22
    length_leads={6:1.015,5:3.118,4:5.773,3:8.243,2:10.686,1:13.409}
    data_by_lead={}
    #lead_6
    file_filter_options={'files':['23','22','21'],'device':'I 4-8 Wire C'}
    report.loaded_files=[]
    report.load_data_files(file_filter_options['device'],*file_filter_options['files'])
    for file in report.loaded_files:
        diode_parameters=report.fit_diode_parameters(file,**user_options)
        [n,R,barrier]=[diode_parameters['Ideality Factor'],
        diode_parameters['Linear Fit Resistance'],diode_parameters['Barrier']]
        R_list.append(R)
        plot_data.append((length_leads[6],R))
        if user_options['print_path']:
            print file.path
    data_by_lead[6]=R_list
    
    #lead_5
    file_filter_options={'files':['20','19','18'],'device':'I 4-8 Wire C'}
    report.loaded_files=[]
    report.load_data_files(file_filter_options['device'],*file_filter_options['files'])
##    for file in report.loaded_files:
##        print file.path
    for file in report.loaded_files:
        diode_parameters=report.fit_diode_parameters(file,**user_options)
        [n,R,barrier]=[diode_parameters['Ideality Factor'],
        diode_parameters['Linear Fit Resistance'],diode_parameters['Barrier']]
        R_list.append(R)
        plot_data.append((length_leads[5],R))
        if user_options['print_path']:
            print file.path
    data_by_lead[5]=R_list
    

    #lead_4
    file_filter_options={'files':['17','16','15'],'device':'I 4-8 Wire C'}
    report.loaded_files=[]
    report.load_data_files(file_filter_options['device'],*file_filter_options['files'])
    for file in report.loaded_files:
        diode_parameters=report.fit_diode_parameters(file,**user_options)
        [n,R,barrier]=[diode_parameters['Ideality Factor'],
        diode_parameters['Linear Fit Resistance'],diode_parameters['Barrier']]
        R_list.append(R)
        plot_data.append((length_leads[4],R))
        if user_options['print_path']:
            print file.path
    data_by_lead[4]=R_list
    
    
    #lead_3
    file_filter_options={'files':['14','_13','_12'],'device':'I 4-8 Wire C'}
    report.loaded_files=[]
    report.load_data_files(file_filter_options['device'],*file_filter_options['files'])
    for file in report.loaded_files:
        diode_parameters=report.fit_diode_parameters(file,**user_options)
        [n,R,barrier]=[diode_parameters['Ideality Factor'],
        diode_parameters['Linear Fit Resistance'],diode_parameters['Barrier']]
        R_list.append(R)
        plot_data.append((length_leads[3],R))
        if user_options['print_path']:
            print file.path
    data_by_lead[3]=R_list
    
    
    
    #lead_2-looks like sweep 2 did not get saved
    file_filter_options={'files':['_11','_10'],'device':'I 4-8 Wire C'}
    report.loaded_files=[]
    report.load_data_files(file_filter_options['device'],*file_filter_options['files'])
    for file in report.loaded_files:
        diode_parameters=report.fit_diode_parameters(file,**user_options)
        [n,R,barrier]=[diode_parameters['Ideality Factor'],
        diode_parameters['Linear Fit Resistance'],diode_parameters['Barrier']]
        R_list.append(R)
        plot_data.append((length_leads[2],R))
        if user_options['print_path']:
            print file.path
    data_by_lead[2]=R_list
    
    
    
    #lead_1
    file_filter_options={'files':['_9','_8','_7'],'device':'I 4-8 Wire C'}
    report.loaded_files=[]
    report.load_data_files(file_filter_options['device'],*file_filter_options['files'])
    for file in report.loaded_files:
        diode_parameters=report.fit_diode_parameters(file,**user_options)
        [n,R,barrier]=[diode_parameters['Ideality Factor'],
        diode_parameters['Linear Fit Resistance'],diode_parameters['Barrier']]
        R_list.append(R)
        plot_data.append((length_leads[1],R))
        if user_options['print_path']:
            print file.path
    data_by_lead[1]=R_list
    
    if user_options['print_plot_data']:
        print plot_data
    params={
            'axes.labelsize': 24,
            'text.fontsize': 24,
            'legend.fontsize': 24,
            'xtick.labelsize': 24,
            'ytick.labelsize': 24,
            'figure.figsize':(10,7.5)}

    matplotlib.rcParams.update(params)
    L_data=[point[0] for point in plot_data]
    R_data=[point[1] for point in plot_data]
    plt.plot(L_data,R_data,'o')
    plt.show()
    print report.loaded_files
        
def plot_all_fits_together_script(Data_Table=None):
    """ Plots the four fits together"""
    

def bending_plot_script():
    """ Plot for the effect of bending"""
      
    report=SandiaReport()
    report.load_data_files('III 7-6')   
        
#-------------------------------------------------------------------------------
# Module Runner    
        
if __name__ == '__main__':
    #test_SandiaReport()
    #}
    #test_plots(**{'files':['7','8','9'],'device':'I 4-8 Wire C'})
    analyze_ebeam_pt_lead_script()
    