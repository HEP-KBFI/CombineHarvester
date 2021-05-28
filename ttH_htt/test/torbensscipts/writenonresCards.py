#!/usr/bin/env python
import os, shlex
import subprocess
import glob
import shutil
import ROOT
from collections import OrderedDict


from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputPath", type="string", dest="inputPath", help="Full path of where prepareDatacards.root are ")
parser.add_option("--outPath", type="string", dest="outPath", help="Full path of where the cards should be created ")
parser.add_option("--channel", type="string", dest="channel", help="The multilepton channel, either 0l_4tau, 1l_3tau, 2lss, 2l_2tau, 3l, 3l_1tau, 4l")
parser.add_option("--era", type="string", dest="era", help="The data taking period.")
parser.add_option("--sigtype", type="string", dest="sigtype", help="The signaltype either nonresLO or nonresNLO")
parser.add_option("--withCR", action='store_true',dest="withCR", default=False)
parser.add_option("--binByBin", action='store_true',dest="binByBin", default=False)
parser.add_option("--removeLowYieldShapes", action='store_true',dest="removeLowYieldShapes", default=False)
parser.add_option("--removeLowImpactShapes", action='store_true',dest="removeLowImpactShapes", default=False)
(options, args) = parser.parse_args()

inputPath = options.inputPath
outPath = options.outPath
channel = options.channel
era = options.era
sigtype = options.sigtype
withCR = options.withCR
binByBin = options.binByBin
removeLowYieldShapes = options.removeLowYieldShapes
removeLowImpactShapes = options.removeLowImpactShapes
bmcases = ["SM","JHEP04BM1","JHEP04BM2","JHEP04BM3","JHEP04BM4","JHEP04BM5","JHEP04BM6","JHEP04BM7","JHEP04BM8","JHEP04BM9","JHEP04BM10","JHEP04BM11","JHEP04BM12","JHEP04BM8a","JHEP03BM1","JHEP03BM2","JHEP03BM3","JHEP03BM4","JHEP03BM5","JHEP03BM6","JHEP03BM7","extrabox"]
if "NLO" in sigtype:
    bmcases = ["SM","JHEP04BM1","JHEP04BM2","JHEP04BM3","JHEP04BM4","JHEP04BM5","JHEP04BM6","JHEP04BM7","JHEP04BM8","JHEP04BM9","JHEP04BM10","JHEP04BM11","JHEP04BM12"]
listproc = glob.glob( "%s/*.root" % inputPath)
commands = []
for card in listproc:
    for BMCase in bmcases:
        if ('MVAOutput_' + BMCase + '.') in card and channel in card:
            cardname = card.split("/")[-1]
            inPath = card.strip(cardname)
            outputfile = 'datacard_' + channel + '_' + era + '_' + BMCase
            command1 = 'WriteDatacards.py  --inputShapes %s --channel %s --HHtype "multilepton" --analysis HH --noX_prefix --era %s --signal_type %s --renamedHHInput --shapeSyst  --forceModifyShapes --output_file %s/%s' %(card,channel, era, sigtype, outPath, outputfile)
            if withCR: command1 = command1 + ' --withCR'
            if binByBin: command1 = command1 + ' --binByBin'
            if removeLowYieldShapes: command1 = command1 + ' --removeLowYieldShapes'
            if removeLowImpactShapes: command1 = command1 + ' --removeLowImpactShapes'
            command2= 'rm %s*mod*'%(inputPath)
            commands.append(command1)
            commands.append(command2)
for command in commands:
    print command
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print line.rstrip("\n")
    print 'done'
    retval = p.wait()
        
