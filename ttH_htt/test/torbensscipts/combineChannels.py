#!/usr/bin/env python
import os, shlex
import subprocess
import glob
import shutil
import ROOT
from collections import OrderedDict

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputPath", type="string", dest="inputPath", help="Base path of where datacards are ")
parser.add_option("--channels", type="string", dest="channels", help="List of channels separeted by:")
parser.add_option("--outPath", type="string", dest="outPath", help="Base path to output datacards")
parser.add_option("--outChannel", type="string", dest="outChannel", help="Name of the output channel", default ="multilepton")
parser.add_option("--WZPath", type="string", dest="WZPath", help="WZCR Path ", default = None)
parser.add_option("--ZZPath", type="string", dest="ZZPath", help="ZZCR Path ", default = None)
(options, args) = parser.parse_args()
inputPath = options.inputPath
outPath = options.outPath
channels = options.channels
channels = channels.split(":")
outChannel = options.outChannel
WZPath = options.WZPath
ZZPath = options.ZZPath

path16 = outPath + "2016/"
path17 = outPath + "2017/"
path18 = outPath + "2018/"
pathRun2 = outPath + "Run2/"

paths16 = []
paths17 = []
paths18 = []
for i in range(len(channels)):
    ch = channels [i]
    paths16.append(inputPath + "/" + ch.replace('_','') + "/2016/")
    paths17.append(inputPath + "/" + ch.replace('_','') + "/2017/")
    paths18.append(inputPath + "/" + ch.replace('_','') + "/2018/")

commands = []
commands.append('rm %s*'%(path16))
commands.append('rm %s*'%(path17))
commands.append('rm %s*'%(path18))
commands.append('rm %s*'%(pathRun2))
for i in range(len(paths16)):
    commands.append('cp %s*.root %s'%(paths16[i],pathRun2))
    commands.append('cp %s*.root %s'%(paths16[i],path16))
    commands.append('cp %s*.root %s'%(paths17[i],pathRun2))
    commands.append('cp %s*.root %s'%(paths17[i],path17))
    commands.append('cp %s*.root %s'%(paths18[i],pathRun2))
    commands.append('cp %s*.root %s'%(paths18[i],path18))
if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(WZPath).replace('ERA','2016'),pathRun2))
if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(WZPath).replace('ERA','2017'),pathRun2))
if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(WZPath).replace('ERA','2018'),pathRun2))
if ZZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(ZZPath).replace('ERA','2016'),pathRun2))
if ZZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(ZZPath).replace('ERA','2017'),pathRun2))
if ZZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(ZZPath).replace('ERA','2018'),pathRun2))

if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(WZPath).replace('ERA','2016'),path16))
if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(WZPath).replace('ERA','2017'),path17))
if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(WZPath).replace('ERA','2018'),path18))

if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(ZZPath).replace('ERA','2016'),path16))
if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(ZZPath).replace('ERA','2017'),path17))
if WZPath: commands.append('cp %s/*.root %s'%(os.path.dirname(ZZPath).replace('ERA','2018'),path18))

cardbasenames = []
listproc = glob.glob( "%s/*.txt" % paths16[0])
for card in listproc:
    cardbasename=card.split("/")[-1]
    cardbasenames.append(cardbasename)

for card in cardbasenames:
    excard16 = paths16[0] + card
    excard17 = paths17[0] + card.replace('2016','2017') 
    excard18 = paths18[0] + card.replace('2016','2018')
    outcard16 = (path16 + card).replace(channels[0], outChannel)
    outcard17 = (path17 + card.replace('2016','2017') ).replace(channels[0], outChannel)
    outcard18 = (path18 + card.replace('2016','2018') ).replace(channels[0], outChannel)
    outcardRun2 = (pathRun2 + card.replace('2016','Run2') ).replace(channels[0], outChannel)
    combineCommand16 = 'combineCards.py '
    combineCommand17 = 'combineCards.py '
    combineCommand18 = 'combineCards.py '
    combineCommandRun2 = 'combineCards.py '
    for i in range(len(channels)):
        ch = channels[i]
        temppath16 =paths16[i]
        temppath17 =paths17[i]
        temppath18 =paths18[i]
        tempcard16 = (temppath16 + card).replace(channels[0], ch)
        tempcard17 = (temppath17 + card.replace('2016','2017')).replace(channels[0], ch)
        tempcard18 = (temppath18 + card.replace('2016','2018')).replace(channels[0], ch)
        combineCommand16 = (combineCommand16 + "HH_%s_2016=%s "%(ch, tempcard16)).replace("//","/")
        combineCommand17 = (combineCommand17 + "HH_%s_2017=%s "%(ch, tempcard17)).replace("//","/")
        combineCommand18 = (combineCommand18 + "HH_%s_2018=%s "%(ch, tempcard18)).replace("//","/")
        combineCommandRun2 = (combineCommandRun2 + "HH_%s_2016=%s HH_%s_2017=%s HH_%s_2018=%s "%(ch, tempcard16, ch, tempcard17, ch, tempcard18)).replace("//","/")
    if WZPath: combineCommand16 = combineCommand16  + ' HH_WZCR_2016=%s'%(WZPath.replace('ERA','2016'))
    if WZPath: combineCommand17 = combineCommand17  + ' HH_WZCR_2017=%s'%(WZPath.replace('ERA','2017'))
    if WZPath: combineCommand18 = combineCommand18  + ' HH_WZCR_2018=%s'%(WZPath.replace('ERA','2018'))
    if WZPath: combineCommandRun2 = combineCommandRun2  + 'HH_WZCR_2016=%s HH_WZCR_2017=%s HH_WZCR_2018=%s'%(WZPath.replace('ERA','2016'), WZPath.replace('ERA','2017'), WZPath.replace('ERA','2018'))
    if ZZPath: combineCommand16 = combineCommand16  + ' HH_ZZCR_2016=%s'%(ZZPath.replace('ERA','2016'))
    if ZZPath: combineCommand17 = combineCommand17  + ' HH_ZZCR_2017=%s'%(ZZPath.replace('ERA','2017'))
    if ZZPath: combineCommand18 = combineCommand18  + ' HH_ZZCR_2018=%s'%(ZZPath.replace('ERA','2018'))
    if ZZPath: combineCommandRun2 = combineCommandRun2  + ' HH_ZZCR_2016=%s HH_ZZCR_2017=%s HH_ZZCR_2018=%s'%(ZZPath.replace('ERA','2016'), ZZPath.replace('ERA','2017'), ZZPath.replace('ERA','2018'))
    combineCommand16 = combineCommand16 + "> %s"%(outcard16)
    combineCommand17 = combineCommand17 + "> %s"%(outcard17)
    combineCommand18 = combineCommand18 + "> %s"%(outcard18)
    combineCommandRun2 = combineCommandRun2 + "> %s"%(outcardRun2)
    commands.append(combineCommand16)
    commands.append(combineCommand17)
    commands.append(combineCommand18)
    commands.append(combineCommandRun2)
    for i in range(len(channels)):
        commands.append("sed -i 's|%s||g' %s"%(paths16[i].replace("//","/"), outcardRun2))
        commands.append("sed -i 's|%s||g' %s"%(paths17[i].replace("//","/"), outcardRun2))
        commands.append("sed -i 's|%s||g' %s"%(paths18[i].replace("//","/"), outcardRun2))
        commands.append("sed -i 's|%s||g' %s"%(paths16[i].replace("//","/"), outcard16))
        commands.append("sed -i 's|%s||g' %s"%(paths17[i].replace("//","/"), outcard17))
        commands.append("sed -i 's|%s||g' %s"%(paths18[i].replace("//","/"), outcard18))
    if WZPath: 
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2016')), outcardRun2))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2017')), outcardRun2))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2018')), outcardRun2))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2016')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2017')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2018')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2016')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2017')), outcard17))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2018')), outcard18))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2016')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2017')), outcard17))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(WZPath.replace('ERA','2018')), outcard18))
    if ZZPath: 
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2016')), outcardRun2))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2017')), outcardRun2))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2018')), outcardRun2))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2016')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2017')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2018')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2016')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2017')), outcard17))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2018')), outcard18))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2016')), outcard16))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2017')), outcard17))
        commands.append("sed -i 's|%s/||g' %s"%(os.path.dirname(ZZPath.replace('ERA','2018')), outcard18))
for command in commands:
    print command
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print line.rstrip("\n")
    print 'done'
    retval = p.wait()


