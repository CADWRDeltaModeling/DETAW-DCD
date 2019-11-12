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


def main():
    tempstring = "DETAW-DCD estimates the Sacramento-San Joaquin Delta hydrology, including consumptive use, ground surface water balance, and channel depletion, given the climate and land use data.\
    It could support the historical, planning or forecasting studies related to the Delta surface water quantity and quality.\
    This version provides three options to estimate the Delta channel depletions in the customized output formats applied to three models: 1-DSM2, 2-SCHISM, and 3-CALSIM.\
    The model inputs and outputs of these options could be taken as the basis for developing various Delta water environmental studies."
    print("------------------------------------------------------------------------------")
    print("                           DETAWv2.0-DCDv1.0")
    print("------------------------------------------------------------------------------")
    print("")
    print(tempstring)
    print("")
    print("    OPTION 1 - DCD estimates the daily historical channel depletions, including diversions, drainages and seepage of DSM2 nodes.")
    print("    OPTION 2 - DCD estimates the daily historical channel depletions without water surface evaporation. SCHISM itself can estimate the water surface evapotration of SCHISM simulation region.")
    print("    OPTION 3 - DCD estimates the monthly planning channel depletions for seven Delta nodes of CALSIM3, monthly island deep percolations, and monthly island groundwater supplies to crop ET.")
    print("")
    print("------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------")
    var = input("Please enter the number you select: ")
    supmodel = int(var)
    print("------------------------------------------------------------------------------")
    
    owd = os.getcwd()
    dir_dst = "../DETAW/"
    os.chdir(dir_dst)
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    
    if supmodel == 1:
        inputfile = "./Input/historical_study/LODI_PT.csv"
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
        outputfile = "DCD_"+months[endmonth-1]+endyear+".dss"
        status=os.system('python DETAW.py DSM2')
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
        outputfile = "DCD_"+months[endmonth-1]+endyear+".dss"
        status=os.system('python DETAW.py CALSIM3')
    elif supmodel == 2:
        inputfile = "./Input/historical_study/LODI_PT.csv"
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
        outputfile = "DCD_noWS_"+months[endmonth-1]+endyear+".dss"
        status=os.system('python DETAW.py SCHISM')
    print("output file =", outputfile)
        
    os.chdir(owd)
    
    dir_dst = ".\\NODCU\\DCD_Cal\\DCD_outputs\\"
    os.chdir(dir_dst)
    
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
    
    #date
    status=os.system('DETAW_CD.exe')
    
    status=os.system('python converttoDSS.py junk1_1.txt')
    status=os.system('python converttoDSS.py junk1_2.txt')
    status=os.system('python converttoDSS.py junk2_1.txt')
    status=os.system('python converttoDSS.py junk2_2.txt')
    status=os.system('python converttoDSS.py junk3_1.txt')
    status=os.system('python converttoDSS.py junk3_2.txt')
    if supmodel == 1:
        shutil.copy(outputfile,owd+"\\Output\\DSM2\\")
    elif supmodel == 2:
        shutil.copy(outputfile,owd+"\\Output\\SCHISM\\")
    elif supmodel == 3:
        status=os.system('python converttoDSS.py roisl.txt')
        status=os.system('python converttoDSS.py gwbyisl.txt')
        tempstr = "python DCD_post-process_C3.py "+outputfile+" DP_island.dss GW_per_island.dss"
        status = os.system(tempstr)
        tempfile = outputfile.split(".")[0].strip()+"_mon_C3.dss"
        shutil.copy(tempfile,owd+"\\Output\\CALSIM3\\")
        tempfile = outputfile.split(".")[0].strip()+"_mon.dss"
        shutil.copy(tempfile,owd+"\\Output\\CALSIM3\\")
        tempfile = "DP_island_mon.dss"
        shutil.copy(tempfile,owd+"\\Output\\CALSIM3\\")
        tempfile = "GW_per_island_mon.dss"
        shutil.copy(tempfile,owd+"\\Output\\CALSIM3\\")
    
    print("finish")

if __name__ == "__main__":
    main()