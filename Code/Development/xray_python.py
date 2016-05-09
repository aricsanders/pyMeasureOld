#-----------------------------------------------------------------------------
# Name:        xray_python.py
# Purpose:     This Module Plots Xray data saved in csv format
#
# Author:      Aric Sanders
#
# Created:     2009/12/11
# RCS-ID:      $Id: xray_python.py $
#-----------------------------------------------------------------------------
# 
""" Module to Handle and plot xray data"""

#-------------------------------------------------------------------------------
# Standard imports

import re
import os 
import sys
import fnmatch
import math

#-------------------------------------------------------------------------------
# Third Party imports
try:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker


    import scipy
    import scipy.optimize
    import scipy.stats
except:
    print """Requires scipy to on the path. Please either download it from 
    http://www.scipy.org/ or place it in the sys.path"""
    raise

#-------------------------------------------------------------------------------
# Module Constants

XRAY_DIRECTORY="C:\Documents and Settings\sandersa\My Documents\Share\XRAY"

#-------------------------------------------------------------------------------
# Module Functions
def get_line_value(name,line):
    """ The value in a line of form name,value"""

    tag_match=re.search(
    '%s,(?P<value>\w+)'%(name),
     line)
    return tag_match.group('value')



def line_data(line,mode=None):
    """Return angle,counts or subset given mode='angle' or mode='counts' from
    single text line"""
    data_match=re.search('(?P<angle>\d+.\d+),(?P<counts>\w+)',line)
    if data_match:
        (angle,counts)=(data_match.group('angle'),data_match.group('counts')) 
        if mode is None:
            return (float(angle),float(counts))
        elif mode is 'counts':
            return float(counts)
        elif mode is 'angle':
            return float(angle)
    else:
        return None
def lorentzian_function(a,x):
    "a[0]=amplitude,a[1]=center,a[2]=FWHM"
    return a[0]*1/(1+(x-a[1])**2/(a[2]**2))

def gaussian_function(a,x):
    " a[0]=amplitude, a[1]=center, a[2]=std deviation"
    return a[0]*scipy.exp(-(x-a[1])**2/(2.0*a[2]**2))

##def error_function(fit=None,a=None,x=None,y=None):
##    """ Error function is fit(a,x)-y"""
##    return fit(a,x)-y

def fit(function,xdata,ydata,a0):
    fit_dictionary={}
    error_function=lambda a, xdata, ydata:function(a,xdata)-ydata
    a,succes=scipy.optimize.leastsq(error_function, a0,args=(xdata,ydata))
    return a
#-------------------------------------------------------------------------------
# Class Definitions

class XrayData():
    """ An Xray data object using the csv format"""
    lambda_k_alpha=.1540595
    def __init__(self,path=None):
        if not path is None:
            data=[]
            counts=[]
            angle=[]
            self.path=path
            file_name=os.path.basename(path)
            #This requires the correct naming scheme
            name_match=re.search('(?P<sample>\w+)_(?P<h>\d)(?P<k>\d)(?P<l>\d)_(?P<curve_type>\w+).\w+',file_name)
            self.sample=name_match.group('sample')
            self.h=name_match.group('h')
            self.k=name_match.group('k')
            self.l=name_match.group('l')
            f=open(path,'r')
            for index,line in enumerate(f.readlines()):
                if re.match('Time per step',line):
                    self.time_per_step=float(get_line_value('Time per step',line))
                elif index>28:
                    data.append(line_data(line))
                    counts.append(line_data(line,'counts'))
                    angle.append(line_data(line,'angle'))
            self.data=[(data_point[0],data_point[1]/self.time_per_step) for data_point
        in data]
            self.counts=counts
            self.angle=angle
            #print self.time_per_step
            self.cps=[count/self.time_per_step for count in self.counts]
            self.normalized_counts=[(count-min(self.counts))/(max(self.counts)-min(self.counts))
             for count in self.counts]
             
            self.max_value=max(self.cps)
            self.max_position=self.angle[self.cps.index(self.max_value)]
            self.max_index=self.angle.index(self.max_position)
            self.half_list=[self.angle[index] for index,value in 
            enumerate(self.normalized_counts) if value>.5]
            
            
            self.d=self.lambda_k_alpha/(2*math.sin(self.peak('weighted')*math.pi/360))
    
            self.particle_size()
    
    
    
            
    def peak(self,type=None,**fit_options):
        "Returns the Peak position in self.data"
        
        
        min_angle=min(self.half_list)
        left=self.max_index-self.half_list.index(min_angle)
        
        max_angle=max(self.half_list)
        right=self.max_index-self.half_list.index(max_angle)
        
        if type is None:
            return self.max_position
        
        elif type in ['weighted']:
            weighted_list=[self.angle[index]*value for index,value in 
            enumerate(self.normalized_counts) if value>.5]
            weights=[value for index,value in 
            enumerate(self.normalized_counts) if value>.5]
            return sum(weighted_list)/sum(weights)
        
        elif type in ['parabolic','x2']:
            maxium=self.max_index
            try:
                number_points_below=fit_options['number_points_below']
                number_points_above=fit_options['number_points_above']
            except:
                number_points_below=3
                number_points_above=3
            x=self.angle[(maxium-number_points_below):(maxium+number_points_above)]
            y=self.normalized_counts[(maxium-number_points_below):(maxium+number_points_above)]
            self.fit=scipy.polyfit(x,y,2)
            return -self.fit[1]/(2*self.fit[0])
        elif type in ['lorentzian']:
            maxium=self.max_index
            try:
                number_points_below=fit_options['number_points_below']
                number_points_above=fit_options['number_points_above']
            except:
                number_points_below=left
                number_points_above=right
            x=self.angle[(maxium-number_points_below):(maxium+number_points_above)]
            y=self.normalized_counts[(maxium-number_points_below):(maxium+number_points_above)]
            a=[1,self.max_position,.01] 
            self.fit=fit(lorentzian_function,x,y,a)
            return self.fit[1]
        elif type in ['gaussian']:
            maxium=self.max_index
            try:
                number_points_below=fit_options['number_points_below']
                number_points_above=fit_options['number_points_above']
            except:
                number_points_below=left
                number_points_above=right
            x=self.angle[(maxium-number_points_below):(maxium+number_points_above)]
            y=self.normalized_counts[(maxium-number_points_below):(maxium+number_points_above)]
            a=[1,self.max_position,.01] 
            self.fit=fit(gaussian_function,x,y,a)
            return self.fit[1]
                
    def particle_size(self,delta=.1,type='mean'):
        """Calculate an estimate of the particle size assuming the FWHM 
        is of the scherrer form"""
        # find things close to the Half max point
        half_list=[abs(intensity-.5) for intensity in self.normalized_counts]
            
        top=[self.angle[index] for index,value in enumerate(half_list)
         if value<delta and self.angle[index]>self.max_position ]
        bottom=[self.angle[index] for index,value in enumerate(half_list)
         if value<delta and self.angle[index]<self.max_position ]
         
        mean_match=re.compile('mean|average',re.IGNORECASE) 
        if re.search(mean_match,type):
            #print 'top,bottom is %s,%s'%(top,bottom)
            self.FWHM=float(sum(top))/len(top)-float(sum(bottom))/len(bottom)
        else:
            self.FWHM=max(top)-min(bottom)
        #print "FWHM is %s, or fractionally %g"%(self.FWHM,self.FWHM/self.max_position)
        return .9*self.lambda_k_alpha/((self.FWHM)*math.cos(self.max_position*math.pi/360))
    
    def lattice_parameters(self,c=None):
        """ Calculates the lattice parameters that are possible"""
        if self.h in [0,'0'] and self.k in [0,'0']:
            self.c=float(self.l)*self.d
            return self.c
        elif not c is None:
            h=float(self.h)
            k=float(self.k)
            l=float(self.l)
            d=float(self.d)
            self.a=math.sqrt(4.0/3.0*(h**2+h*k+k**2)*(1/d**2-l**2/c**2)**-1)
            return self.a
    
        
    def plot(self,show_fit=False):
        "Plots Amplitude versus Angle"
        
        
        plt.figure()
        plt.plot(self.angle,self.normalized_counts)
        plt.xlabel(r"Angle (2$\theta$)",fontsize=24)
        plt.ylabel("Intensity (Arb.)",fontsize=24)
        
        plt.show()
#-------------------------------------------------------------------------------
# Scripts

def plot_all_files_script(directory=XRAY_DIRECTORY):
    """ Plots all the files in the current directory"""
    file_names=os.listdir(directory)
    file_names=fnmatch.filter(file_names,'*.csv')
    data_list=[]
    print file_names
    for index,name in enumerate(file_names):
        new_data=XrayData(name)
        data_list.append(new_data)
        
    print data_list[0].path,data_list[0].data
    data_list[0].plot()
def comparision_plot(*file_names):
    data_list=[]
    below=20
    above=20
    plt.figure()
    for index,name in enumerate(file_names):
        new_data=XrayData(name)
        print 'The peak position is %s, The max position is %s'%(new_data.peak('lorentzian'),new_data.peak())
        print new_data.particle_size()
        print new_data.sample
        print 'Diffraction is (%s,%s,%s)'%(new_data.h,new_data.k,new_data.l)
        print 'C lattice parameter is %s'%(new_data.lattice_parameters())
        print 'a lattice parameter is %s'%(new_data.lattice_parameters(c=0.518503))
        plt.plot(new_data.angle,new_data.normalized_counts,
        label=new_data.path,lw=4)
        plt.plot(new_data.angle[(new_data.max_index-below):(new_data.max_index+above)]
        ,lorentzian_function(new_data.fit,
        new_data.angle[(new_data.max_index-below):(new_data.max_index+above)]),
        'r-',label=new_data.path+'_fit')
        
        plt.hold(1)
    #plt.xlim(34.5,34.65)
    plt.xlabel(r"Angle (2$\theta$-$\omega$)",fontsize=24)
    plt.ylabel("Intensity (Arb.)",fontsize=24)
    plt.legend(loc=(-.2,0.2))
    plt.show()  
    
def compare_fit_script(*file_names):
    """ Compares the available fits to the data"""
        
##        plt.figure()
##        plt.hold(1)
##        plt.plot(new_data.angle,new_data.normalized_counts,
##        label=new_data.path,lw=4)
##    
##        plt.ylim=[0,1]
    
    c_lattice=[]
    for name in file_names:
        new_data=XrayData(name)
        max=new_data.peak()
        
        print 'For the (%s,%s,%s) diffraction:'%(new_data.h,new_data.k,new_data.l)
        print "FWHM is %s, or fractionally %g"%(new_data.FWHM,new_data.FWHM/new_data.max_position)
        FWHM=new_data.FWHM
        print '2theta from max position is %s'%max
        parabolic=new_data.peak('parabolic')
        print '2theta from parabolic fit is %s'%parabolic
        lorentzian=new_data.peak('lorentzian')
        print '2theta from lorentzian fit is %s'%lorentzian
        gaussian=new_data.peak('gaussian')
        print '2theta from gaussian fit is %s'%gaussian
        weighted=new_data.peak('weighted')
        print '2theta from a weighted sum from half max to half max is %s'%weighted
        
        weighted_error_list=[(c*new_data.angle[index]/sum(new_data.counts)*(1/c+
        (.0001/new_data.angle[index])**2+1/sum(new_data.counts))**.5)**2 for 
        index,c in enumerate(new_data.counts) if new_data.normalized_counts[index]>.5]
        weighted_error=(sum(weighted_error_list))**.5
        print 'Weighted error is %g'%weighted_error
        print 'Weighted fractional error is %g'%(weighted_error/weighted)
        error_mean=(FWHM/(2.3548*float(len(weighted_error_list))**.5))
        print 'Error in the mean is %g'%error_mean
        print 'Fractional Error in the mean is %g'%(error_mean/weighted)
        difference_list=[max-max,parabolic-max,lorentzian-max,gaussian-max,weighted-max]
        
        print 'The difference is (%s,%s,%s,%s,%s)'%tuple(difference_list) 
        error=sum(difference_list)/(sum([max,parabolic,lorentzian,gaussian,weighted]))
        print "Average fractional error from centroid determination is %g"%error
        if not new_data.lattice_parameters() is None:
            c_lattice.append(new_data.lattice_parameters())
        print 'C lattice parameter is %s'%(new_data.lattice_parameters())
        print 'reference is %g from C023 or %g from GN169'%(5.5*10**-6/.518503,3*10**-5/.518537)
        print '-'*80
    average_c_lattice=sum(c_lattice)/len(c_lattice)
    error_c_lattice=scipy.stats.samplestd(c_lattice)
    
    print "For the sample %s:"%new_data.sample
    print "Average c lattice parameter is %g +- %g"%(average_c_lattice,error_c_lattice)
    print "Fractional error is %g"%(error_c_lattice/average_c_lattice)
    
    a_lattice=[]
    for name in file_names:
        new_data=XrayData(name)
        if new_data.lattice_parameters() is None:
            a_lattice.append(new_data.lattice_parameters(c=average_c_lattice))
    
    average_a_lattice=sum(a_lattice)/len(a_lattice)
    error_a_lattice=scipy.stats.samplestd(a_lattice)
    print "Average a lattice parameter is %g +- %g"%(average_a_lattice,error_a_lattice)
    print "Fractional error is %g"%(error_a_lattice/average_a_lattice)   
    
    

def make_report_script():
    """ Makes a report of lattice parameters from xray data"""
    pass
def make_plots_for_paper_script(plot_type,**plot_options):
    """ Makes plots for the core shell nanowire paper"""
    #file_list=os.listdir(XRAY_DIRECTORY)
    # First we want to plot all of the diffractions before and after overcoating
    # For at least one sample. 
    diffraction_list=['002','004','006','104','105','205']
    before_sample='B982'
    after_sample='GN97'
    #Values computed using compare fit script, need to check GN84 (used GN84+GN84b)
    # Should this be the normalized difference in GN84 and GN84b?
    # Error has now been changed to 2 sigma or 120ppm which ever is bigger 
    before_after={'B982':'GN97','B738':'GN84','C023':'GN169'}
    c_lattice={'B982':.518459,'GN97':.51846,'B738':.518432,'GN84':.51844,'GN84b':.51844,
    'C023':.518494,'GN169':.518536}
    c_lattice_error={'B982':.00003,'GN97':.00003,'B738':.00003,'GN84':.00003,'GN84b':.00005,
    'C023':.00003,'GN169':.00007}
    a_lattice={'B982':.31888,'GN97':.31893,'B738':.318984,'GN84':.319177,'GN84b':.318933,
    'C023':.31905,'GN169':.31888}
    a_lattice_error={'B982':.00004,'GN97':.00004,'B738':.00003,'GN84':.0002,'GN84b':.0003,
    'C023':.0001,'GN169':.00007}
    
    #c Lattice plot
    if plot_type in ['c_lattice_plot','c'] :
        defalt_size=48
        axis_label_size=48
        params = {
            'axes.labelsize': defalt_size,
            'text.fontsize': defalt_size,
            'legend.fontsize':defalt_size,
            'xtick.labelsize': defalt_size,
            'ytick.labelsize': defalt_size}

        matplotlib.rcParams.update(params)

        f=plt.figure(1)
        plot_axes=plt.axes()
        plt.xlabel(r"Sample",fontsize=axis_label_size)
        plt.ylabel(r"$\mathit{c}$ Lattice (nm)",fontsize=axis_label_size)
    
        plt.axhspan(0.51845, 0.51865, facecolor='0.25', alpha=0.25)
        plt.hold(1)
        def x_name(i):
            if (i+1)%2 is 0:
                return 'Core-Shell'
            else:
                return 'Core'
        
        i=0
        x_names=[]
        for key,value in before_after.iteritems():
            i=2*before_after.keys().index(key)+1
            x=[i,i+1]
            x_names.insert(i,key)
            x_names.insert(i+1,value)
            print key,x
            y=[c_lattice[key],c_lattice[value]]
            error=[c_lattice_error[key],c_lattice_error[value]]
            a=plt.errorbar(x, y, error,fmt='s',lw=4)
        
        plot_axes.yaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))
    
        abc='a a b b c c'.split(' ')
    
        #x_labels=[x_name(i)+' ('+abc+')' for i,abc in enumerate(abc)]
        x_labels=x_names
        x_labels.insert(0,'')
        plot_axes.set_xticklabels(x_labels,fontsize=axis_label_size)
    
        plt.show() 

    if plot_type in ['a_lattice_plot','a']:  
        defalt_size=32
        axis_label_size=32 
        params={
            'axes.labelsize': defalt_size,
            'text.fontsize': defalt_size,
            'legend.fontsize': defalt_size,
            'xtick.labelsize': defalt_size,
            'ytick.labelsize': defalt_size}

        matplotlib.rcParams.update(params)    
        f=plt.figure(1)
        plot_axes=plt.axes()
        plt.xlabel(r"Sample",fontsize=axis_label_size)
        plt.ylabel(r"$\mathit{a}$ Lattice (nm)",fontsize=axis_label_size)
        # reference rectangle -- Porowski JCG 1998, Lo
        plt.axhspan(0.31876, 0.31894, facecolor='0.25', alpha=0.25)
        plt.hold(1)
        def x_name(i):
            if (i+1)%2 is 0:
                return 'Core-Shell'
            else:
                return 'Core'
        
        i=0
        x_names=[]
        for key,value in before_after.iteritems():
            i=2*before_after.keys().index(key)+1
            x=[i,i+1]
            x_names.insert(i,key)
            x_names.insert(i+1,value)
            print key,x
            y=[a_lattice[key],a_lattice[value]]
            error=[a_lattice_error[key],a_lattice_error[value]]
            a=plt.errorbar(x, y, error,fmt='s',lw=4)
        
        plot_axes.yaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))
    
        abc='a a b b c c'.split(' ')
     
        #x_labels=[x_name(i)+' ('+abc+')' for i,abc in enumerate(abc)]
        x_labels=x_names
        x_labels.insert(0,'')
        plot_axes.set_xticklabels(x_labels,fontsize=axis_label_size)
    
        plt.show() 
        
    if plot_type in ['before_after_two_theta','two_theta']:
        params={
            'axes.labelsize': 32,
            'text.fontsize': 32,
            'legend.fontsize': 32,
            'xtick.labelsize': 32,
            'ytick.labelsize': 32}

        matplotlib.rcParams.update(params)    
        f=plt.figure(1)
        plot_axes=plt.axes()
        plt.xlabel(r"2 $\theta-\omega$",fontsize=38)
        plt.ylabel("Normalized Intensity (Arb.)",fontsize=38)
        try:
            before_data=XrayData(plot_options['before'])
            after_data=XrayData(plot_options['after'])
        except:
            raise

        plt.plot(before_data.angle,before_data.normalized_counts,lw='4',color='b')
        plt.hold(1)
        plt.plot(after_data.angle,after_data.normalized_counts,lw='4',color='r')
        h=before_data.h
        k=before_data.k
        l=before_data.l
        sample_1=before_data.sample
        sample_2=after_data.sample
        #plt.title('Diffraction (%s %s %s) of Samples: %s (blue), %s (red)'%(h,k,l,sample_1,sample_2),
        #fontsize=32)
        plot_axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))
        try:
            plt.xlim((before_data.peak()-plot_options['angle_span'],
            before_data.peak()+plot_options['angle_span']))
            plt.ylim((-.01,1.01))
        except:
            raise
    
        plt.show()        
#-------------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    #file_list=['B982_002_2ThOm.csv','GaNcontrol_002_2thom.csv','C023_002_2ThOm.csv']
    file_list=['B982_002_2ThOm.csv','GN97_002_2ThOm.csv']
    #file_list=os.listdir(XRAY_DIRECTORY)
    #file_list=fnmatch.filter(file_list,'*B738*.csv')
    #print fnmatch.filter(file_list,'*C023*002*.csv')
    #comparision_plot(*file_list)
    #compare_fit_script(*file_list)
##    options={'before':fnmatch.filter(file_list,'*C023*204*.csv')[0],
##    'after':fnmatch.filter(file_list,'*GN169_*204*.csv')[0],'angle_span':.25}
    #make_plots_for_paper_script('two_theta',**options)
    make_plots_for_paper_script('c')