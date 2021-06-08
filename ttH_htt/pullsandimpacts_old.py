#!/usr/bin/env python
import os, shlex
import subprocess
import glob
import shutil
import ROOT
from collections import OrderedDict


from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputCard", type="string", dest="inputCard", help="Full path to the datacard")
parser.add_option("--channel", type="string", dest="channel", help="The multilepton channel, either 0l_4tau, 1l_3tau, 2lss, 2l_2tau, 3l, 3l_1tau, 4l")
parser.add_option("--era", type="string", dest="era", help="The data taking period.")
(options, args) = parser.parse_args()

inputCard = options.inputCard
channel = options.channel
era = options.era

commands = []
basename = "%s_%s"%(channel,era)
commands.append("text2workspace.py %s -m 125 -o %s.root"%(inputCard, basename))
commands.append("combineTool.py -m 125 -M Impacts -d %s.root -m 125 -t -1 --expectSignal 1 --doInitialFit --robustFit 1 -n %s_r1 --parallel 16"%(basename,basename))
commands.append("combineTool.py -m 125 -M Impacts -d %s.root -m 125 -t -1 --expectSignal 1 --doFits --robustFit 1 -n %s_r1 --parallel 16"%(basename, basename))
commands.append("combineTool.py -m 125 -M Impacts -d %s.root -m 125 -t -1 --expectSignal 1  -n %s_r1 --parallel 16 -o impacts_%s_r1.json"%(basename, basename, basename))
commands.append("plotImpacts.py -i impacts_%s_r1.json -o impacts_%s_r1"%(basename,basename))
commands.append("rm higgsCombine_initialFit_%s_r1.MultiDimFit.mH125.root"%(basename))
commands.append("rm higgsCombine_paramFit_%s_r1*.root"%(basename))
commands.append("combineTool.py -m 125 -M Impacts -d %s.root -m 125 -t -1 --expectSignal 0 --doInitialFit --robustFit 1 -n %s_r0 --parallel 16"%(basename,basename))
commands.append("combineTool.py -m 125 -M Impacts -d %s.root -m 125 -t -1 --expectSignal 0 --doFits --robustFit 1 -n %s_r0 --parallel 16"%(basename, basename))
commands.append("combineTool.py -m 125 -M Impacts -d %s.root -m 125 -t -1 --expectSignal 0  -n %s_r0 --parallel 16 -o impacts_%s_r0.json"%(basename, basename, basename))
commands.append("plotImpacts.py -i impacts_%s_r0.json -o impacts_%s_r0"%(basename,basename))
commands.append("rm higgsCombine_initialFit_%s_r0.MultiDimFit.mH125.root"%(basename))
commands.append("rm higgsCombine_paramFit_%s_r0*.root"%(basename))
commands.append("rm %s.root"%(basename))
for command in commands:
    print command
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print line.rstrip("\n")
    print 'done'
    retval = p.wait()
