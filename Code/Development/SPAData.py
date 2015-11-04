#-----------------------------------------------------------------------------
# Name:        SPAData.py
# Purpose:    A datahandler tanslation program for data from the kiethly SPA 
#
# Author:      Aric Sanders 
#
# Created:     2011/04/18
# RCS-ID:      $Id: IVData.py $

#-----------------------------------------------------------------------------
""" SPAData is a module to manipulate, move and save data from the Keithley IV SPA"""

#TODO: get directories from settings file
#TODO: Interface to a plot
#TODO:
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
    import pyMeasure.Code.DataHandlers.Measurements
    
except:
    print("""This module needs pyMeasure to function. The folder directly above
    PYMEASURE_ROOT must be on sys.path""")
    raise

try:
    import win32com.client
except:
    print "COM is required to talk to excel"
    pass

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

PYMEASURE_ROOT=r'C:\Documents and Settings\sandersa\My Documents\Share\pyMeasure'
MEASUREMENTS_DIRECTORY=os.path.join(PYMEASURE_ROOT,'Data','Measurements').replace('\\','/')
DEFAULT_STATE_XSL=os.path.join(PYMEASURE_ROOT,'Data/States',
'DEFAULT_STATE_STYLE.XSL').replace('\\','/')
DEFAULT_MEASUREMENT_XSL=os.path.join(PYMEASURE_ROOT,'Data/Measurements',
'DEFAULT_MEASUREMENT_STYLE.XSL').replace('\\','/')


#-------------------------------------------------------------------------------
# Class Definitions


class TextData():
    """ Class that handles text IV Data"""
    
    def __init__(self,path=None,**options_dictionary):
        self.path=path
        self.header=''
        self.footer=''
        self.data=[]
        self.data_dictionary={}
        data_list=[]
        in_file=open(path,'r')
        for index,line in enumerate(in_file.readlines()):
            if index is 0:
                self.names=line.split('\t')
            elif index>0:
                if line in ['','\t','\n']:
                    break
                self.data.append(line.split('\t'))
                data_list.append(dict(zip(self.names,line.split('\t'))))
        self.data_dictionary['Data']=data_list
        self.XML=pyMeasure.Code.DataHandlers.Measurements.DataTable(**self.data_dictionary)
    def save_as_XML(self,path=None):
        if path is None:
            self.XML.save(self.path.replace('txt','xml'))
        else:
            self.XML.save(path)

    def __str__(self):
        string_form='*'*80+'\n'
        for name in self.names:
            string_form=string_form+'\t'+name
        string_form=string_form+'\n' + '*'*80+'\n'
        for row in self.data:
            for column in row:
                string_form=string_form + column+ '\t'
            string_form=string_form + '\n'
        
        return string_form
        
    def plot(self,x_data_name='AV',y_data_name='AI',**plot_options):
        " Plots the current data "
        x_data=self.XML.to_list(x_data_name)
        y_data=self.XML.to_list(y_data_name)
        
        x_data=filter(lambda x:x not in ['','\n'] ,x_data)
        y_data=filter(lambda x:x not in ['','\n'],y_data)
        
            
##        print x_data,y_data
        params={
            'axes.labelsize': 24,
            'text.fontsize': 24,
            'legend.fontsize': 24,
            'xtick.labelsize': 24,
            'ytick.labelsize': 24,
            'figure.figsize':(20,20)}

        matplotlib.rcParams.update(params)    
        f=plt.figure(1)
        plot_axes=plt.axes()
        plt.xlabel(x_data_name,fontsize=28)
        plt.ylabel(y_data_name,fontsize=28)
        plt.plot(x_data,y_data,lw='4',color='r')
        plot_axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))
        plt.show()   
    
        
class ExcelData():
    def __init__(self,path=None,**options_dictionary):
        if not path is None:
            self.path=path
            self.application=win32com.client.Dispatch('Excel.Application')
            self.workbook=self.application.Workbooks.Open(path)
            self.settings_sheet=self.workbook.Sheets.Item('Settings')
            self.calc_sheet=self.workbook.Sheets.Item('Calc')
            self.data_sheet=self.workbook.Sheets.Item('Data')
            
            #I am not sure why but the following is not always a robust way to get
            # the last row.
            self.last_row=self.data_sheet.Columns.End(4)
##            print self.last_row
        
        self.data_names=self.worksheet_to_list(**{'return':'names','name_row':1})    
        data_dictionary=self.worksheet_to_list(**{'return':'dictionary','name_row':1})
        data_table={'Data_Description':self.get_settings()}
        data_table['Data']=data_dictionary['Data']
        self.XML=pyMeasure.Code.DataHandlers.Measurements.DataTable(**data_table)
    def worksheet_to_list(self,sheet_name='Data',**options_dictionary):
        """ Creates a 2-D list given a sheet name"""
        sheet=self.workbook.Sheets.Item(sheet_name)
        # default options, note the max_row,max_column should be set
        options={'max_row':self.last_row,'max_column':10,'return':'data','name_row':1}
        try:
            for key,value in options_dictionary.iteritems():
                options[key]=value
        except:
            pass
        
        if 'name_row' in options_dictionary.keys():
            self.names=[]
            new_name=next_name='start'
            column=1
            while not next_name in ['',None]:
                 new_name=sheet.Cells(options_dictionary['name_row'],column).Value
                 next_name=sheet.Cells(options_dictionary['name_row'],column+1).Value
                 self.names.append(new_name)
                 options['max_column']=column
                 column+=1
                 if column>10000:
                     break
##        print options['max_column'], options['max_row']
        out=[[0]*options['max_column'] for i in range(options['max_row'])]
        for column in range(options['max_column']):
            for row in range(options['max_row']):
                out[row][column]=sheet.Cells(row+1,column+1).Value
##        print out,self.names
        if re.search('data',options['return']):
            return out     
        elif re.search('name',options['return']):
            try:
                if re.search('no',options['return']):
                    #print self.names
                    #print out
                    out.remove(self.names)
                    return out
                else:
                    return self.names
            except:
                print "Error, remember that name_row must be defined in options"
        elif re.search('dictionary',options['return']) and self.names:
            data_list=[]
            out.remove(self.names)
            for row,data_row in enumerate(out):
                # Here I replace any parentheses with undrescores
                def replace_p(list_of_strings):
                    for index,string in enumerate(list_of_strings):
                        new_string=string.replace(')','_')
                        new_string=new_string.replace('(','_')
                        list_of_strings[index]=new_string
                    return list_of_strings
                self.names=replace_p(self.names)
                tuple=dict([(name,out[row][index]) for index,name in enumerate(self.names)])
                
                data_list.append(tuple)
                    
            dictionary_out={'Data':data_list}        
            return dictionary_out
    def get_settings(self):
        settings_length=22
        #self.settings_sheet.Columns.End(4)
        # I just hard coded this in, there seems to be an oddity woth settings length
        # for small numbers it returns useless string
        settings=self.worksheet_to_list('Settings',**{'name_row':9,'max_row':settings_length})
        settings_names=self.worksheet_to_list('Settings',**{'name_row':9,'max_row':settings_length,'return':'names'})
        try:
            settings_names=[name.replace(' ','_') for name in settings_names]
        except:pass
        #print settings_names
        settings_dictionary={}
        
        #print settings
        for i in range(7):
            settings_dictionary[settings[i][0].replace(' ','_')]=settings[i][1]
        try:    
            for j in range(len(settings_names)-1):
                terminal_string=''
                for i in range(8,settings_length):
                    if i is 8 :
                        terminal_string=str(settings[i][0]+' : '+settings[i][j+1])
                    else:
                        terminal_string=terminal_string+' , '+str(settings[i][0]+' : '+settings[i][j+1])
                settings_dictionary[settings_names[j+1]]=terminal_string
        except:pass
                
        return settings_dictionary
            
            
            
            
    def save_as_XML(self):

        self.XML.save(self.path.replace('xls','xml'))
        
    def plot(self,x_data_name='AV',y_data_name='AI',**plot_options):
        " Plots the current data "

        x_data=self.XML.to_list(x_data_name)
        y_data=self.XML.to_list(y_data_name)
        
        x_data=filter(lambda x:x not in ['','\n',None,'None'] ,x_data)
        y_data=filter(lambda x:x not in ['','\n',None,'None'],y_data)
        
            
##        print x_data,y_data
        params={
            'axes.labelsize': 24,
            'text.fontsize': 24,
            'legend.fontsize': 24,
            'xtick.labelsize': 24,
            'ytick.labelsize': 24,
            'figure.figsize':(20,20)}

        matplotlib.rcParams.update(params)    
        f=plt.figure(1)
        plot_axes=plt.axes()
        plt.xlabel(x_data_name,fontsize=28)
        plt.ylabel(y_data_name,fontsize=28)
        plt.plot(x_data,y_data,lw='4',color='r')
        plot_axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))
        plt.show()          
        
#-------------------------------------------------------------------------------
# Module Scripts

def test_save_as_xml(path=r'C:\Documents and Settings\sandersa\My Documents\Share\4ptWafer_2\Die 4\II 1 3\VDS vs Vg.xls'):
    test_workbook=ExcelData(path)  
    test_workbook.save_as_XML()
def test_excel_plot(path=r'C:\Documents and Settings\sandersa\My Documents\Share\4ptWafer_2\Die 4\II 2 6\UV Stress.xls'):
    test_workbook=ExcelData(path)  
    test_workbook.plot(test_workbook.data_names[1],test_workbook.data_names[0])
    
    
def test_print_text(path=r'C:\Documents and Settings\sandersa\My Documents\Share\pyMeasure\Code\Development\I-11-1_1.txt'):
    test_file=TextData(path)
    print test_file
    
def test_save_as_XML_text(path=r'C:\Documents and Settings\sandersa\My Documents\Share\pyMeasure\Code\Development\I-11-1_1.txt'):
    test_file=TextData(path)
    test_file.save_as_XML()
       
def test_text_plot(path=r'C:\Documents and Settings\sandersa\My Documents\Share\pyMeasure\Code\Development\I-11-1_1.txt'):
    test_file=TextData(path)
    print test_file.names[0],test_file.names[1]
    print test_file.names
    test_file.plot(test_file.names[1],test_file.names[0])
    
def plot_for_paper(path=r'C:\Documents and Settings\sandersa\My Documents\Share\Core Shell paper\HVPE coatings on GaN NWs\Sample Folders\N112 on B992 L25\text file data\Single NWs only\N112 on B992 L25\IV-3-1_2a.txt')         :
        
    test_file=TextData(path)
    x_data=test_file.XML.to_list(test_file.names[2])
    y_data=test_file.XML.to_list(test_file.names[1])
        
    x_data=filter(lambda x:x not in ['','\n',None,'None'] ,x_data)
    y_data_1=filter(lambda x:x not in ['','\n',None,'None'],y_data)
    
    y_data=[float(y)*10**6 for y in y_data_1]
           
    #print x_data,y_data
    params={
            'axes.labelsize': 24,
            'text.fontsize': 24,
            'legend.fontsize': 24,
            'xtick.labelsize': 24,
            'ytick.labelsize': 24,
            'figure.figsize':(10,10)}

    matplotlib.rcParams.update(params)    
    f=plt.figure(1)
    plot_axes=plt.axes()
    plt.xlabel('Voltage (V)',fontsize=28)
    plt.ylabel(r"Current ($\mu$A)",fontsize=28)
    plt.plot(x_data,y_data,lw='4',color='r')
    plot_axes.xaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=False))
    plt.show()     
if __name__ == '__main__':
    plot_for_paper()
