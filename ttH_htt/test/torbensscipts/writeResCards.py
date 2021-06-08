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
parser.add_option("--spinCase", type="string", dest="spinCase", help="The spin case either spin0 or spin2")
parser.add_option("--channel", type="string", dest="channel", help="The multilepton channel, either 0l_4tau, 1l_3tau, 2lss, 2l_2tau, 3l, 3l_1tau, 4l")
parser.add_option("--era", type="string", dest="era", help="The data taking period.")
parser.add_option("--withCR", action='store_true',dest="withCR", default=False)
(options, args) = parser.parse_args()

inputPath = options.inputPath
outPath = options.outPath
spinCase = options.spinCase
channel = options.channel
era = options.era
withCR = options.withCR
listproc = glob.glob( "%s/*.root" % inputPath)
commands = []
for card in listproc:
    if spinCase in card and channel in card:
        cardname = card.split("/")[-1]
        mass = cardname.split("_")[-2]
        inPath = card.strip(cardname)
        outputfile = 'datacard_' + channel + '_' + era + '_' + spinCase + "_" + mass
        command1 = 'WriteDatacards.py  --inputShapes %s --channel %s --HHtype "multilepton" --analysis HH --noX_prefix --era %s --signal_type "res" --renamedHHInput --shapeSyst  --forceModifyShapes --mass %s --output_file %s/%s' %(card,channel, era, (spinCase + "_" + mass),outPath, outputfile)
        if withCR: command1 = command1 + ' --withCR'
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
        
