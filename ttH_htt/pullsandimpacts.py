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
parser.add_option("--signal_type", type="string", dest="signal_type", help="resonant, nonresonant")
parser.add_option("--asimov", action="store_true", dest="asimov", help="produce toy or not", default=False)
(options, args) = parser.parse_args()

inputCard = options.inputCard
channel = options.channel
era = options.era
signal_type = options.signal_type
asimov = options.asimov

commands = []
basename = "pulls_%s_%s_%s_asimov_%s" %(channel,era, signal_type, asimov)
commands.append("text2workspace.py %s -m 125 -o %s.root"%(inputCard, basename))
cmd = "combineTool.py -m 125 -M Impacts -d %s.root -m 125 --expectSignal 1 --doInitialFit --robustFit 1 -n %s_r1 --parallel 20 --setParameterRanges r=-100,100" %(basename,basename)
if asimov: cmd += " -t -1 "
commands.append(cmd)
cmd = "combineTool.py -m 125 -M Impacts -d %s.root -m 125 --expectSignal 1 --doFits --robustFit 1 -n %s_r1 --parallel 20 --setParameterRanges r=-100,100 --exclude 'rgx{BR}','rgx{thu_shape}','rgx{QCDscale}','rgx{alpha}',pdf_qqH,pdf_ggH,pdf_tHW,pdf_tHq,pdf_ttH" %(basename,basename)
if asimov: cmd += " -t -1 "
cmd += "1>pull_impact_%s_out_r1.txt 2>pull_impact_%s_err_r1.txt" %(basename, basename)
commands.append(cmd)
cmd = "combineTool.py -m 125 -M Impacts -d %s.root -m 125 --expectSignal 1  -n %s_r1 --parallel 20 --setParameterRanges r=-100,100 -o impacts_%s_r1.json"%(basename, basename, basename)
if asimov: cmd += " -t -1 "
commands.append(cmd)
commands.append("plotImpacts.py -i impacts_%s_r1.json -o impacts_%s_r1"%(basename,basename))
commands.append("rm higgsCombine_initialFit_%s_r1.MultiDimFit.mH125.root"%(basename))
commands.append("rm higgsCombine_paramFit_%s_r1*.root"%(basename))

cmd += "combineTool.py -m 125 -M Impacts -d %s.root -m 125 --expectSignal 0 --setParameterRanges r=-100,100 --doInitialFit --robustFit 1 -n %s_r0 --parallel 20" %(basename,basename)
if asimov: cmd += " -t -1 "
commands.append(cmd)
cmd = "combineTool.py -m 125 -M Impacts -d %s.root -m 125 --expectSignal 0 --doFits --robustFit 1 --setParameterRanges r=-100,100 -n %s_r0 --parallel 20 --exclude 'rgx{BR}','rgx{thu_shape}','rgx{QCDscale}','rgx{alpha}',pdf_qqH,pdf_ggH,pdf_tHW,pdf_tHq,pdf_ttH"  %(basename, basename)
if asimov: cmd += " -t -1 "
cmd += "1>pull_impact_%s_r0_out.txt 2>pull_impact_%s_r0_err.txt" %(basename, basename)
commands.append(cmd)
cmd = "combineTool.py -m 125 -M Impacts -d %s.root -m 125 --expectSignal 0  -n %s_r0 --parallel 20 --setParameterRanges r=-100,100 -o impacts_%s_r0.json"%(basename, basename, basename)
if asimov: cmd += " -t -1 "
commands.append(cmd)
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
