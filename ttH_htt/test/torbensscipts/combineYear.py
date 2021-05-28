#!/usr/bin/env python
import os, shlex
import subprocess
import glob
import shutil
import ROOT
from collections import OrderedDict

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputPath", type="string", dest="inputPath", help="Full path of where datacards are ")
parser.add_option("--WZPath", type="string", dest="WZPath", help="WZCR Path ", default = None)
parser.add_option("--ZZPath", type="string", dest="ZZPath", help="ZZCR Path ", default = None)
parser.add_option("--channel", type="string", dest="channel", help="channel name ")
(options, args) = parser.parse_args()
inputPath = options.inputPath
channel = options.channel
WZPath = options.WZPath
ZZPath = options.ZZPath

path16 = inputPath + "2016/"
path17 = inputPath + "2017/"
path18 = inputPath + "2018/"
pathRun2 = inputPath + "Run2/"


commands = []
commands.append('rm %s*'%(pathRun2))
commands.append('cp %s*.root %s'%(path16,pathRun2))
commands.append('cp %s*.root %s'%(path17,pathRun2))
commands.append('cp %s*.root %s'%(path18,pathRun2))
if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(WZPath),pathRun2))
if ZZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(ZZPath),pathRun2))

listproc = glob.glob( "%s/*.txt" % path16)
for card in listproc:
    cardbasename=card.split("/")[-1]
    card16=card
    card17=path17+cardbasename.replace('2016','2017') 
    card18=path18+cardbasename.replace('2016','2018') 
    cardRun2=pathRun2+cardbasename.replace('2016','Run2')
    combineCommand = 'combineCards.py HH_%s_2016=%s HH_%s_2017=%s HH_%s_2018=%s'%(channel, card16, channel,card17, channel,card18)
    if WZPath: combineCommand = combineCommand  + 'HH_WZCR_2016=%s HH_WZCR_2017=%s HH_WZCR_2018=%s'%(WZPath.replace('ERA','2016'), WZPath.replace('ERA','2017'), WZPath.replace('ERA','2018'))
    if ZZPath: combineCommand = combineCommand  + 'HH_ZZCR_2016=%s HH_ZZCR_2017=%s HH_ZZCR_2018=%s'%(ZZPath.replace('ERA','2016'), ZZPath.replace('ERA','2017'), ZZPath.replace('ERA','2018'))
    combineCommand = combineCommand  + ' > %s'%(cardRun2)
    commands.append(combineCommand)
    commands.append("sed -i 's|%s||g' %s"%(path16, cardRun2))
    commands.append("sed -i 's|%s||g' %s"%(path17, cardRun2))
    commands.append("sed -i 's|%s||g' %s"%(path18, cardRun2))
    if WZPath: commands.append("sed -i 's|%s||g' %s"%(os.path.dirname(WZPath), cardRun2))
    if ZZPath: commands.append("sed -i 's|%s||g' %s"%(os.path.dirname(ZZPath), cardRun2))

for command in commands:
    print command
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print line.rstrip("\n")
    print 'done'
    retval = p.wait()


