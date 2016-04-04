import os, sys
from Ganga import *
from GridScript.Ganga.Reconstruction import Marlin


"""
Helper function to create a ganga job
"""
def createJob(executable, args = [], backend='CREAM', backendCE='lyogrid07.in2p3.fr:8443/cream-pbs-calice'):
  j = Job()
  j.application = Executable(exe=File(executable), args=args)
  j.backend = backend
  j.backend.CE = backendCE
  return j


# reconstruction settings
energy = "200"
# runs = ["00"]
# subruns = ["0"]
runs = ["0"+str(i) for i in range(0, 10, 1)]
subruns = [str(i) for i in range(0, 1000, 100)]

# ArborPFA settings
ArborPFAVersion = "v02-01-00"
ArborPFADir = "/gridgroup/ilc/CommonSoft/ArborPFA/" + ArborPFAVersion
ArborPFAScriptDir = ArborPFADir + "/build/MarlinArbor-prefix/src/MarlinArbor/scripts"
job_config_files_dir = "/gridgroup/ilc/rete/GridScript/ArborPFA/Common/job_config_files"
lcioInputFile = ""

# marlin input stuff
ilcsoftInitScript = "/gridsoft/ipnls/ilc/v01-17-03/init_ilcsoft.sh"
gearFile = ArborPFAScriptDir + "/GearOutput_ILD_o2_v05.xml"
lcioInputGridPath = "/grid/calice/SDHCAL/simu/ILD_o2_v05/"
marlinXml = ArborPFAScriptDir + "/MarlinArbor_v01-17-03.xml"
pandoraXml = ArborPFAScriptDir + "/ArborSettingsDefault.xml"

# marlin libraries
marlinDlls = ArborPFADir + "/lib/libMarlinArbor.so:/gridsoft/ipnls/ilc/v01-17-03/MarlinReco/v01-07/lib/libMarlinReco.so:/gridsoft/ipnls/ilc/v01-17-03/PandoraAnalysis/v00-05/lib/libPandoraAnalysis.so:/gridsoft/ipnls/ilc/v01-17-03/LCFIVertex/v00-06-01/lib/libLCFIVertex.so:/gridsoft/ipnls/ilc/v01-17-03/CEDViewer/v01-07/lib/libCEDViewer.so:/gridsoft/ipnls/ilc/v01-17-03/Overlay/v00-13/lib/libOverlay.so:/gridsoft/ipnls/ilc/v01-17-03/FastJetClustering/v00-02/lib/libFastJetClustering.so:/gridsoft/ipnls/ilc/v01-17-03/MarlinFastJet/v00-01/lib/libMarlinFastJet.so:/gridsoft/ipnls/ilc/v01-17-03/LCTuple/v01-03/lib/libLCTuple.so:/gridsoft/ipnls/ilc/v01-17-03/MarlinKinfit/v00-01-02/lib/libMarlinKinfit.so:/gridsoft/ipnls/ilc/v01-17-03/MarlinTrkProcessors/v01-09-01/lib/libMarlinTrkProcessors.so:/gridsoft/ipnls/ilc/v01-17-03/Clupatra/v00-10/lib/libClupatra.so:/gridsoft/ipnls/ilc/v01-17-03/LCFIPlus/v00-05-02/lib/libLCFIPlus.so:/gridsoft/ipnls/ilc/v01-17-03/ForwardTracking/v01-07/lib/libForwardTracking.so:/gridsoft/ipnls/ilc/v01-17-03/MarlinTPC/v00-14/lib/libMarlinTPC.so:/gridsoft/ipnls/ilc/v01-17-03/Garlic/v2.10.1/lib/libGarlic.so"

# output settings
lcioOutputFileSuffix = "REC"
lcioOutputFile = ""  # to be built job per job
pandoraAnalysisFile = ""  # to be built job per job
lcioOutputGridPath = "/grid/calice/SDHCAL/simu/ILD_o2_v05/"+lcioOutputFileSuffix
pandoraOutputAnalysisGridPath = "/grid/calice/SDHCAL/simu/ILD_o2_v05/PANDORA_ANALYSIS"

# Fill parser with base config
parser = ConfigParser.ConfigParser()

parser.add_section("GridInput")
parser.add_section("GridOutput")

marlin = Marlin()
marlin.setGearFile(gearFile)
marlin.setMarlinXml(marlinXml)
marlin.setLibraries(marlinDlls.split(':'))
marlin.setIlcsoftInitScript(ilcsoftInitScript)

marlin.setReplacementOption("global.Verbosity", "SILENT")
marlin.setReplacementOption("MyMarlinArbor.PandoraSettingsXmlFile", "SILENT")


for r in runs:
    for sr in subruns:
      
        j = createJob()
        
        # build file names
        lcioInputFile = 'uds{0}_{1}.stdhep_{2}_100.slcio'.format(energy, r, sr)
        pandoraAnalysisFile = 'PFOAnalysis_uds{0}_{1}.stdhep_{2}_100.root'.format(energy, r, sr)
        lcioOutputFile = 'uds{0}_{1}.stdhep_{2}_100_{3}.slcio'.format(energy, r, sr, lcioOutputFileSuffix)
        
        # add it to grid interface sections
        parser.set("GridInput", lcioInputFile, lcioInputGridPath)
        parser.set("GridOutput", lcioOutputFile, lcioOutputGridPath)
        parser.set("GridOutput", pandoraAnalysisFile, pandoraOutputAnalysisGridPath)
        
        # add files to marlin
        marlin.setReplacementOption("global.LCIOInputFiles", lcioInputFile)
        marlin.setReplacementOption("MyLCIOOutputProcessor.LCIOOutputFile", lcioOutputFile)
        marlin.setReplacementOption("MyPfoAnalysis.RootFile", pandoraAnalysisFile)
        
        # write config on disk      
        configFileName = job_config_files_dir + "/cfg_file_"+ str(j.id) +".cfg"
        f = open(configFileName, 'w')
        marlin.writeConfigFile(parser)
        parser.write(f)
        f.close()
        
        j.application.args = ['/gridgroup/ilc/CommonSoft/GridScript/bin/run_marlin.py', configFileName]
        j.submit()      
      
      
      
      