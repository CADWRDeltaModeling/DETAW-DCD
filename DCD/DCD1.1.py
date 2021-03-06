# Delta Channel Depletion Model (DCDv1.1)
#<license>
#    Copyright (C) State of California, Department of Water Resources.
#    This file is part of DCDv1.1.

#    DCDv1.1 is free software: 
#    you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DCDv1.1 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DCDv1.1.  If not, see <http://www.gnu.org/licenses>.
#</license>
#
# This version 1.1 was developed only for supporting CALSIM3 studies. 
#
# Enter the following line in the command window to run the model:
#    Python DCD1.1.py 
# 

import pandas as pd
import pyhecdss
import os,sys
import shutil

def callDCD(supmodel,leachoption,endyear,outputfile):
    owd = os.getcwd()
    dir_dst = ".\\NODCU\\DCD_Cal\\"
    os.chdir(dir_dst)
    if not os.path.exists(".\DCD_outputs"):
        os.mkdir(".\DCD_outputs")
    shutil.copy('DCD_kernel.exe',".\DCD_outputs")
    shutil.copy('WYTYPES',".\DCD_outputs")
    os.chdir(".\DCD_outputs")
    
    os.environ['DICU5.14']='../../../../DETAW/Output/DICU5.14' 
    os.environ['DICU5.17']='../../../../DETAW/Output/DICU5.17' 
    os.environ['DICU5.12']='../../../../DETAW/Output/DICU5.12' 
    os.environ['DICU5.27']='../../../../DETAW/Output/DICU5.27' 
    os.environ['DICU5.30']='../../../../DETAW/Output/DICU5.30' 
    
    if supmodel == 3:
        os.environ['GW_RATES.TXT'] = '../../../NODCU/GW_RATES_CALSIM3.TXT'
    else:
        os.environ['GW_RATES.TXT'] = '../../../NODCU/GW_RATES.TXT'   #update data in the file each year ----no adjustment-GW_RATES.TXT
    os.environ['GW_LOWLANDS.TXT']='../../../NODCU/GW_LOWLANDS.TXT' #set for DETAW-CD
    os.environ['DIVFCTR.RMA']='../../../NODCU/DIVFCTR.2020'
    os.environ['DRNFCTR.RMA']='../../../NODCU/DRNFCTR.2020'
    os.environ['LEACHAPL.DAT']='../../../NODCU/LEACHAPL.DAT'
    os.environ['LEACHDRN.DAT']='../../../NODCU/LEACHDRN.DAT'
    os.environ['IDRNTDS.DAT']='../../../NODCU/IDRNTDS.DAT'
    os.environ['DRNCL.123']='../../../NODCU/DRNCL.123'
    os.environ['GEOM-NODES']='../../../NODCU/GEOM-NODES-1.5'
    
    os.environ['IRREFF.DAT']='../../../NODCU/IRREFF-3MWQIregions'
    os.environ['subarea-info']='../../../NODCU/subarea-info'
    
    
    # Runtime variables
    # The years assumed are incorrect, so 'N'
    os.environ['years_ok']='N'
    # The correct beginning year to run is
    os.environ['begwy']='1922'
    # The correct last year to run is
    os.environ['endwy']=endyear                        
    # Type of drainage concentration data (1 for TDS, 2 for chloride)
    os.environ['datatype']='1'
    # Do you want to creat an ascii file?
    os.environ['ascii']='Y'
    # The dss file to save output
    os.environ['dssfile']=outputfile 
    # The leach scale factor   
    os.environ['leachscale']=str(leachoption)
        
    status=os.system('DCD_kernel.exe')
    
    if supmodel == 1:
        shutil.copy(outputfile,owd+"\\Output\\DSM2\\")
    elif supmodel == 2:
        tempfile = outputfile.split(".")[0].strip()+"_noWS_leach"+str(leachoption)+".dss"
        os.rename(outputfile,tempfile)
        shutil.copy(tempfile,owd+"\\Output\\SCHISM\\")        
    elif supmodel == 3:
        status=os.system('python ../converttoDSS.py roisl.txt')
        status=os.system('python ../converttoDSS.py gwbyisl.txt')
        status=os.system('python ../converttoDSS.py drn_wo_ro_isl.txt')
        status=os.system('python ../converttoDSS.py div_wo_spg_isl.txt')
        status=os.system('python ../converttoDSS.py spgisl.txt')
        
        tempstr = "python ../DCD_post-process_C3.py "+outputfile+ " base"
        status = os.system(tempstr)
        filestocopy = ["drn_wo_ro_island.dss","div_wo_spg_island.dss","GW_per_island.dss","RO_island.dss","DP_island.dss","spg_island.dss"]
        for i in range(len(filestocopy)):
            tempfile = filestocopy[i]
            daytomonth(tempfile,"DCD_island_month.dss")
            shutil.copy(tempfile, "D_"+tempfile)
            shutil.copy(tempfile, "C_"+tempfile)
        shutil.copy("DCD_island_month.dss",owd+"\\Output\\CALSIM3\\")
    
    os.chdir(owd)

def callDETAW(supmodel,leachoption):
    owd = os.getcwd()
    dir_dst = "../DETAW/"
    os.chdir(dir_dst)
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    
    if supmodel == 1 or supmodel == 2:
        inputfile = "./Input/historical_study/LODI_PT.csv"
    elif supmodel == 3:
        inputfile = "./Input/planning_study/LODI_PT.csv"
        
    f0 = open(inputfile, 'r')
    templ = ""
    endyear = 0
    for line in f0:
        if line:
            templ = line
            if line.split(",")[5].strip()=="0" and line.split(",")[6].strip()=="0":
                break
    endyear = templ.split(",")[1]  
    endmonth = int(templ.split(",")[2])
    outputfile = "DCD_"+months[endmonth-1]+endyear+"_Lch"+str(leachoption)+".dss" 
    status=os.system('python DETAW2.1.py')
    os.chdir(owd)
    return(endyear,outputfile)
    
def get_pathname(dssfh, path):
    '''
    reads catalog to get full pathname if it exists
    The assumption is that the path provided does not have a time window
    returns the first matching pathname with exactly the A,B,C,E and F parts
    '''
    pathparts=path.split('/')
    dfcat=dssfh.read_catalog()
    #@dfpath=dfcat[(dfcat.A==pathparts[1]) & (dfcat.B==pathparts[2]) 
    #@                & (dfcat.C==pathparts[3]) & (dfcat.E==pathparts[5])
    #@                & (dfcat.F==pathparts[6])]
    dfpath=dfcat[(dfcat.B==pathparts[2])]
    pathname=dssfh.get_pathnames(dfpath)[0]
    return pathname
    
def daytomonth(inputfile,outputfile):
    d=pyhecdss.DSSFile(inputfile)
    #outputfile = os.getcwd()+"\\"+inputfile.split(".")[0]+"_mon.dss"
    do=pyhecdss.DSSFile(outputfile)
    plist=d.get_pathnames()
    for p in plist:
        df,u,p=d.read_rts(p)
        do.write_rts(df.columns[0].replace('1DAY','1MON'),df.resample('M').mean(),u,'PER-AVER')
    d.close()
    do.close()
        
def changepaths(inDSSfile,pathfile,outDSSfile,EPART):
    f0 = open(pathfile, 'r')
    islands = []
    for line in f0:
        if line:
            islands.append(line)
            
    dssifh=pyhecdss.DSSFile(inDSSfile)
    dssofh=pyhecdss.DSSFile(outDSSfile)
    for i in range(len(islands)):
        templ = islands[i]        
        pathin = "//"+templ.split(",")[0].strip()+"/////"
        cpart = get_pathname(dssifh,pathin).split("/")[3]
        tdss,cunits,ctype = dssifh.read_rts(get_pathname(dssifh,pathin))
        pathout = "/"+templ.split(",")[1].strip()+"/"+templ.split(",")[0].strip()+"/"+cpart+"//"+EPART+"/"+templ.split(",")[2].strip()+"/"
        dssofh.write_rts(pathout,tdss.shift(freq='D'),cunits,ctype)
    dssifh.close()
    dssofh.close()
    
def callDCD_ext(supmodel,leachoption,endyear,outputfile,extension):
    owd = os.getcwd()
    
    dir_dst = ".\\NODCU\\DCD_Cal\\"
    os.chdir(dir_dst)
    if not os.path.exists(".\DCD_outputs"):
        os.mkdir(".\DCD_outputs")
    shutil.copy('DCD_kernel.exe',".\DCD_outputs")
    shutil.copy('WYTYPES',".\DCD_outputs")
    os.chdir(".\DCD_outputs")
    
    tempn = '../../../../DETAW/Output/DICU5_'+extension
    os.environ['DICU5.14']=tempn+'.14' 
    os.environ['DICU5.17']=tempn+'.17' 
    os.environ['DICU5.12']=tempn+'.12' 
    os.environ['DICU5.27']=tempn+'.27' 
    os.environ['DICU5.30']=tempn+'.30' 
    os.environ['GW_RATES.TXT'] = '../../../NODCU/GW_RATES_CALSIM3.TXT'
    os.environ['GW_LOWLANDS.TXT']='../../../NODCU/GW_LOWLANDS.TXT' #set for DETAW-CD
    os.environ['DIVFCTR.RMA']='../../../NODCU/DIVFCTR.2020'
    os.environ['DRNFCTR.RMA']='../../../NODCU/DRNFCTR.2020'
    tempn ='../../../NODCU/LEACHAPL_'+extension
    os.environ['LEACHAPL.DAT']=tempn+'.DAT'
    tempn ='../../../NODCU/LEACHDRN_'+extension    
    os.environ['LEACHDRN.DAT']=tempn+'.DAT'
    os.environ['IDRNTDS.DAT']='../../../NODCU/IDRNTDS.DAT'
    os.environ['DRNCL.123']='../../../NODCU/DRNCL.123'
    os.environ['GEOM-NODES']='../../../NODCU/GEOM-NODES-1.5'
    
    os.environ['IRREFF.DAT']='../../../NODCU/IRREFF-3MWQIregions'
    tempn ='../../../NODCU/subarea-info_'+extension
    os.environ['subarea-info']=tempn+'.TXT'
    
    
    # Runtime variables
    # The years assumed are incorrect, so 'N'
    os.environ['years_ok']='N'
    # The correct beginning year to run is
    os.environ['begwy']='1922'
    # The correct last year to run is
    os.environ['endwy']=endyear                        
    # Type of drainage concentration data (1 for TDS, 2 for chloride)
    os.environ['datatype']='1'
    # Do you want to creat an ascii file?
    os.environ['ascii']='Y'
    # The dss file to save output
    os.environ['dssfile']=outputfile 
    # The leach scale factor   
    os.environ['leachscale']=str(leachoption)
        
    status=os.system('DCD_kernel.exe')
    
    status=os.system('python ../converttoDSS.py roisl.txt')
    status=os.system('python ../converttoDSS.py gwbyisl.txt')
    status=os.system('python ../converttoDSS.py drn_wo_ro_isl.txt')
    status=os.system('python ../converttoDSS.py div_wo_spg_isl.txt')
    status=os.system('python ../converttoDSS.py spgisl.txt')
    
    tempstr = "python ../DCD_post-process_C3.py "+outputfile+ " base"
    status = os.system(tempstr)
    filestocopy_day = ["spg_island.dss","RO_island.dss","drn_wo_ro_island.dss","div_wo_spg_island.dss","DP_island.dss","GW_per_island.dss"]
    for i in range(len(filestocopy_day)):
        tempfile = "ext_"+filestocopy_day[i]
        changepaths(filestocopy_day[i],"../../../NODCU/path_"+extension+".txt",tempfile,"1DAY")
        daytomonth(tempfile,"ext_DCD_island_month.dss")
        #if extension == "ex3":
            #shutil.copy(tempfile,owd+"\\Output\\CALSIM3\\")
            #shutil.copy(tempfile.split(".")[0]+"_mon.dss",owd+"\\Output\\CALSIM3\\")
    if extension == "ex3":
        shutil.copy("ext_DCD_island_month.dss",owd+"\\Output\\CALSIM3\\")
        tempstr = "python ../DCD_post-process_C3.py "+outputfile+" ex3"
        status = os.system(tempstr)
    
    os.chdir(owd)


def createoutputs(outputfile):
    owd = os.getcwd()
    
    dir_dst = ".\\NODCU\\DCD_Cal\\"
    os.chdir(dir_dst)
    if not os.path.exists(".\DCD_outputs"):
        os.mkdir(".\DCD_outputs")
    shutil.copy('DCD_kernel.exe',".\DCD_outputs")
    shutil.copy('WYTYPES',".\DCD_outputs")
    os.chdir(".\DCD_outputs")
    tempstr = "python ../DCD_post-process_C3.py "+outputfile+" out"
    status = os.system(tempstr)
    
    #shutil.rmtree(".\DCD_outputs")
    os.chdir(owd)


def main():
    pyhecdss.set_message_level(0)
    owd = os.getcwd()
    modelparafile = "./NODCU/DCD_parameters.inp"
    fmp = open(modelparafile,"r")
    modeloption = 0
    outputfile = ""
    for line in fmp:
        if line:
            if not("#" in line):
                if "Model to streamline" in line:
                    modeloption = int(line.split("=")[1]) 
                if "Leach scale factor" in line:
                    leachoption = int(line.split("=")[1])
    (endyear,outputfile) = callDETAW(modeloption,leachoption)
    
    callDCD(modeloption,leachoption,endyear,outputfile)
    if modeloption == 3:
        callDCD_ext(modeloption,leachoption,endyear,outputfile,"ex1")
        callDCD_ext(modeloption,leachoption,endyear,outputfile,"ex2")
        callDCD_ext(modeloption,leachoption,endyear,outputfile,"ex3")
    
    createoutputs(outputfile)
    
    shutil.rmtree(".\\NODCU\\DCD_Cal\\DCD_outputs", ignore_errors=True)
    #print("output file =", outputfile)
    os.chdir(owd)

if __name__ == "__main__":
    main()