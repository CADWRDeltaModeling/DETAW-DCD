# Delta Channel Depletion Model (DCDv1.0)
#<license>
#    Copyright (C) State of California, Department of Water Resources.
#    This file is part of DCDv1.0.

#    DCDv1.0 is free software: 
#    you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DCDv1.0 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DCDv1.0.  If not, see <http://www.gnu.org/licenses>.
#</license>
#
# Enter the following line in the command window to run the model:
#    Python DCD.py 
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
    
    os.environ['GW_RATES.TXT'] = '../../../NODCU/GW_RATES.TXT'   #update data in the file each year ----no adjustment-GW_RATES.TXT
    os.environ['GW_LOWLANDS.TXT']='../../../NODCU/GW_LOWLANDS.TXT' #set for DETAW-CD
    os.environ['DIVFCTR.RMA']='../../../NODCU/DIVFCTR.DSM.2-92'
    os.environ['DRNFCTR.RMA']='../../../NODCU/DRNFCTR.DSM.2-92'
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
    
    status=os.system('python ../converttoDSS.py junk1_1.txt')
    status=os.system('python ../converttoDSS.py junk1_2.txt')
    status=os.system('python ../converttoDSS.py junk2_1.txt')
    status=os.system('python ../converttoDSS.py junk2_2.txt')
    status=os.system('python ../converttoDSS.py junk3_1.txt')
    status=os.system('python ../converttoDSS.py junk3_2.txt')
    if supmodel == 1:
        shutil.copy(outputfile,owd+"\\Output\\DSM2\\")
    elif supmodel == 2:
        tempfile = outputfile.split(".")[0].strip()+"_noWS_leach"+str(leachoption)+".dss"
        os.rename(outputfile,tempfile)
        shutil.copy(tempfile,owd+"\\Output\\SCHISM\\")        
    elif supmodel == 3:
        status=os.system('python ../converttoDSS.py roisl.txt')
        status=os.system('python ../converttoDSS.py gwbyisl.txt')
        tempstr = "python ../DCD_post-process_C3.py "+outputfile+" DP_island.dss GW_per_island.dss"
        status = os.system(tempstr)
        tempfile = outputfile.split(".")[0].strip()+"_mon_C3.dss"
        shutil.copy(tempfile,owd+"\\Output\\CALSIM3\\")
        tempfile = outputfile.split(".")[0].strip()+"_mon.dss"
        shutil.copy(tempfile,owd+"\\Output\\CALSIM3\\")
        tempfile = "DP_island_mon.dss"
        shutil.copy(tempfile,owd+"\\Output\\CALSIM3\\")
        tempfile = "GW_per_island_mon.dss"
        shutil.copy(tempfile,owd+"\\Output\\CALSIM3\\")
    os.chdir("../")
    shutil.rmtree(".\DCD_outputs")
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
    status=os.system('python DETAW.py')
    os.chdir(owd)
    return(endyear,outputfile)

def main():
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
    print("output file =", outputfile)
    

if __name__ == "__main__":
    main()