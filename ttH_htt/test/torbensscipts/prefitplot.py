#!/usr/bin/env python                                                                                                                                                                                      
import math
import os, shlex
import subprocess
import glob
import shutil
import json
import ROOT
ROOT.gROOT.SetBatch(True)
from collections import OrderedDict
import CMS_lumi, tdrstyle
from optparse import OptionParser
from array import array
import json
import numpy as np
parser = OptionParser()
parser.add_option("--inputCard", type="string", dest="inputCard", help="Full path where the datacard is")
parser.add_option("--outPath", type="string", dest="outPath", help="Full path to store plot and ws")
parser.add_option("--Info", type="string", dest="analysisInfo", help="analysis info e.g. 3l_1tau_2016_nonResLO_SM")
parser.add_option("--log", action='store_true',dest="logy", default=False)
parser.add_option("--NLO", action='store_true',dest="NLO", default=False)
parser.add_option("--paper", action='store_true',dest="paper", default=False)
parser.add_option("--isCR", action='store_true',dest="isCR", default=False)
parser.add_option("--skipCombine", action='store_true',dest="skipCombine", default=False)
parser.add_option("--Bins", type="string", dest="Bins", help="Bin in datacard to plot")
parser.add_option("--sigDesc", type="string", dest="sigDesc", help="Additional sig description")
parser.add_option("--sigQuant", type="int", dest="sigQuant", help="Where to blind", default = -1)
parser.add_option("--sigScale", type="int", dest="sigScale", help="Signal scale for linear plots", default = -1)
parser.add_option("--post", action='store_true',dest="post", default=False)
parser.add_option("--largeRatio", action='store_true',dest="largeRatio", default=False)
parser.add_option("--unblindSig", action='store_true',dest="unblindSig", default=False)
parser.add_option("--ratio", action='store_true',dest="ratio", default=False)
parser.add_option("--xlabel", type="string", dest="xlabel", help="x axis label", default = None)
parser.add_option("--ylabel", type="string", dest="ylabel", help="y axis label", default = None)
parser.add_option("--lumilabel", type="string", dest="lumilabel", help="lumi label", default = None)
parser.add_option("--binfile", type="string", dest="binfile", help="File with original binning ", default = None)
parser.add_option("--binshapes", action='store_true',dest="binshapes", default=False)
parser.add_option("--fitfile", type="string", dest="fitfile", help="Fitdiagnostics file, sets skipCombine to true ", default = None)
parser.add_option("--minY", type="float", dest="minY", help="min y for log", default = 0.001)
parser.add_option("--unblind", action='store_true',dest="unblind", default=False)
parser.add_option("--hideSig", action='store_true',dest="hideSig", default=False)
(options, args) = parser.parse_args()
inputCard = options.inputCard   
outPath = options.outPath
ylabel = options.ylabel
logy = options.logy
signaldesc = options.sigDesc
Bins = options.Bins.split(":")
analysisInfo = options.analysisInfo
skipCombine=options.skipCombine 
isNLO = options.NLO
isCR = options.isCR
minY = options.minY
sigQuant = options.sigQuant
sigScale = options.sigScale
post = options.post
largeRatio = options.largeRatio
paper = options.paper
unblindSig = options.unblindSig
ratio = options.ratio
xlabel = options.xlabel
ylabel = options.ylabel
lumilabel = options.lumilabel
binfile = options.binfile
binshapes = options.binshapes
fitfile = options.fitfile
unblind = options.unblind
hideSig = options.hideSig
if fitfile: skipCombine = True

def transferHist(templatehist, hist, shapes=False):
    temphist = hist.Clone()
    temphist.Reset()
    edges = []
    for i in range(templatehist.GetNbinsX()+1):
        edges.append(hist.GetBinLowEdge(i+1))
    edges= np.array(edges)
    temphist = temphist.Rebin(len(edges)-1,temphist.GetName(),edges)
    if shapes:
        temphist = templatehist.Clone()
    for i in range(templatehist.GetNbinsX()+1):
        temphist.SetBinContent(i,hist.GetBinContent(i))
        temphist.SetBinError(i,hist.GetBinError(i))
    temphist.SetBinContent(templatehist.GetNbinsX()+1, hist.GetBinContent(hist.GetNbinsX()+1))
    temphist.SetBinError(templatehist.GetNbinsX()+1, hist.GetBinError(hist.GetNbinsX()+1))
    temphist.SetLineColor(hist.GetLineColor())
    temphist.SetFillColor(hist.GetFillColor())
    temphist.SetFillStyle(hist.GetFillStyle())
    temphist.SetLineWidth(hist.GetLineWidth())
    temphist.SetTitle(hist.GetTitle())
    temphist.SetName(hist.GetName())
    return temphist

oldhist = None
olddata = None
if binfile:
    oldfile = ROOT.TFile(binfile)
    oldhist = oldfile.Get("data_obs").Clone()
    if isCR:
        olddata = oldfile.Get("data_obs").Clone()
    oldhist.Reset()
# Bin = "HH_3l_1tau"                                                                                                                                                                                        
# logy = True                                                                                                                                                                                               
# ylabel="hh-multilepton 3l1tau (2016)"                                                                                                                                                                     
# signaldesc= "SM (1pb)"                                                                                                                                                                                    
# outPath=options.outPath                                                                                                                                                                                   


commands = []
wspath="%s/ws_%s.root"%(outPath,analysisInfo)
commands.append("text2workspace.py %s -o %s -m 125"%(inputCard,wspath))
commands.append("combineTool.py -M FitDiagnostics -d %s --skipBOnlyFit --saveShapes  --saveWithUncertainties --cminDefaultMinimizerType Minuit2 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,0:1.0 -n _%s -m 125 -v 5"%(wspath, analysisInfo))
commands.append("mv fitDiagnostics_%s.root %s"%(analysisInfo, outPath))
commands.append("mv higgsCombine_%s.FitDiagnostics.*.root %s"%(analysisInfo, outPath))
if not skipCombine:
    for command in commands:
        print command
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print line.rstrip("\n")
        print 'done'
        retval = p.wait()


if not fitfile: fitfile = ROOT.TFile("%s/fitDiagnostics_%s.root"%(outPath, analysisInfo))
else: fitfile = ROOT.TFile(fitfile)
print fitfile
postfitshapefolder=fitfile.Get("shapes_fit_s")
prefitshapefolder=fitfile.Get("shapes_prefit")
prefitshapes= prefitshapefolder.Get(Bins[0])
postfitshapes= postfitshapefolder.Get(Bins[0])
print prefitshapes
yieldDict = {}
total = None
data = None
if post:
    if not isCR: 
        total = postfitshapes.Get("total_background")
    else:
        total = postfitshapes.Get("total")
    data = postfitshapes.Get("data")
else:
    if not isCR: 
        total = prefitshapes.Get("total_background")
    else: 
        total = prefitshapes.Get("total")
    data = prefitshapes.Get("data")
total.SetLineColor(0)
total.SetFillColor(0)
err = ROOT.TH1D("err", "err", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
ZZ  = ROOT.TH1D("ZZ", "ZZ", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
ZZ.SetLineColor(634)
ZZ.SetFillColor(634)
ggZZ  = ROOT.TH1D("ggZZ", "ggZZ", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
ggZZ.SetLineColor(634)
ggZZ.SetFillColor(634)
qqZZ  = ROOT.TH1D("qqZZ", "qqZZ", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
qqZZ.SetLineColor(ROOT.kOrange)
qqZZ.SetFillColor(ROOT.kOrange)
WZ  = ROOT.TH1D("WZ", "WZ", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
WZ.SetFillColor(874)
WZ.SetLineColor(874)
singleH  = ROOT.TH1D("singleH", "singleH", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
singleH.SetLineColor(ROOT.kOrange-3)
singleH.SetFillColor(ROOT.kOrange-3)
TT  = ROOT.TH1D("TT", "TT", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
TT.SetFillColor(16)
TT.SetLineColor(16)
Other  = ROOT.TH1D("Other", "Other", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
Other.SetLineColor(851)
Other.SetFillColor(851)
DY  = ROOT.TH1D("DY", "DY", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
DY.SetLineColor(395)
DY.SetFillColor(395)
Flips  = ROOT.TH1D("Flips", "Flips", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
Flips.SetLineColor(1)
Flips.SetFillColor(1)
Flips.SetFillStyle(3004)
Convs  = ROOT.TH1D("Convs", "Convs", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
Convs.SetLineColor(ROOT.kBlack)
Convs.SetFillColor(ROOT.kBlack)
#Convs.SetFillStyle(3005)
TTX  = ROOT.TH1D("TTX", "TTX", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
TTX.SetLineColor(823)
TTX.SetFillColor(823)
W  = ROOT.TH1D("W", "W", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
W.SetLineColor(822)
W.SetFillColor(822)
WW  = ROOT.TH1D("WW", "WW", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
WW.SetLineColor(436)
WW.SetFillColor(436)
signal_4v  = ROOT.TH1D("HH_WWWW", "HH_WWWW", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
signal_4v.SetLineColor(ROOT.kBlue)
signal_4v.SetLineWidth(3)
signal_4v.SetFillColor(0)
signal_2v2t  = ROOT.TH1D("HH_WWTT", "HH_WWTT", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
signal_2v2t.SetLineColor(ROOT.kRed)
signal_2v2t.SetFillColor(0)
signal_2v2t.SetLineWidth(3)
signal_4t  = ROOT.TH1D("HH_TTTT", "HH_TTTT", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
signal_4t.SetLineColor(ROOT.kYellow)
signal_4t.SetFillColor(0)
signal_4t.SetLineWidth(3)
signal  = ROOT.TH1D("HH", "HH", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
signal.SetLineColor(1)
signal.SetFillColor(0)
signal.SetLineWidth(3)
signal_ggHH_WWWW  = ROOT.TH1D("ggHH_WWWW", "ggHH_WWWW", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
signal_qqHH_WWWW  = ROOT.TH1D("qqHH_WWWW", "qqHH_WWWW", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
signal_ggHH_TTTT  = ROOT.TH1D("ggHH_TTTT", "ggHH_TTTT", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
signal_qqHH_TTTT  = ROOT.TH1D("qqHH_TTTT", "qqHH_TTTT", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
signal_ggHH_WWTT  = ROOT.TH1D("ggHH_WWTT", "ggHH_WWTT", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
signal_qqHH_WWTT  = ROOT.TH1D("qqHH_WWTT", "qqHH_WWTT", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())

data_fakes  = ROOT.TH1D("data_fakes", "data_fakes", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
data_fakes.SetLineColor(2)
data_fakes.SetFillColor(2)
data_fakes.SetFillStyle(3005)
error = ROOT.Double(0.)
for Bin in Bins:
    bgshapes = None
    sgshapes = None
    if post:
        bgshapes = postfitshapefolder.Get(Bin)
    else: 
        bgshapes = prefitshapefolder.Get(Bin)
    if not unblindSig:
        sgshapes = prefitshapefolder.Get(Bin)
    else: 
        sgshapes = postfitshapefolder.Get(Bin)
    if Bin is not Bins[0]:
        data2 = bgshapes.Get("data")
        transferdatax = []
        transferdataexl = []
        transferdataexh = []
        transferdatay = []
        transferdataeyl = []
        transferdataeyh= []
        print data
        for i in range(total.GetNbinsX()):
            x = ROOT.Double()
            y = ROOT.Double()
            x2 = ROOT.Double()
            y2= ROOT.Double()
            data.GetPoint(i,x,y)
            data2.GetPoint(i,x2,y2)
            transferdatax.append(ROOT.Double(total.GetBinCenter(i+1)))
            transferdataexl.append(ROOT.Double(total.GetBinWidth(i+1))/2)
            transferdataexh.append(ROOT.Double(total.GetBinWidth(i+1))/2)
            transferdatay.append(y+y2)
            transferdataeyl.append(math.sqrt(data.GetErrorYlow(i)**2+data2.GetErrorYlow(i)**2))
            transferdataeyh.append(math.sqrt(data.GetErrorYhigh(i)**2+data2.GetErrorYhigh(i)**2))
        n = len(transferdatax)
        transferdatax = array('f', transferdatax)
        transferdataexl = array('f', transferdataexl)
        transferdataexh = array('f', transferdataexh)
        transferdatay = array('f', transferdatay)
        transferdataeyl = array('f', transferdataeyl)
        transferdataeyh = array('f', transferdataeyh)
        data = ROOT.TGraphAsymmErrors(n, transferdatax, transferdatay, transferdataexl, transferdataexh, transferdataeyl, transferdataeyh)
        if not isCR: 
            total.Add(bgshapes.Get("total_background"))
        else: 
            total.Add(bgshapes.Get("total"))
    for entry in bgshapes.GetListOfKeys():
        name = entry.GetName()
        if 'total' in name:
            continue
        elif ('ggH_' in name or 'qqH_' in name or 'TTH_' in name or 'tHq_' in name or 'tHW_' in name or 'WH_' in name or 'ZH_' in name or 'ttH_' in name):
            singleH.Add(bgshapes.Get(name))
        elif ('ggHH' in name or 'qqHH' in name or 'signal' in name):
            #if (isNLO and not ('kl_1_kt_1_' in name or 'CV_1_C2V_1_kl_1_' in name)): continue
            temphist =sgshapes.Get(name)
            signal.Add(temphist)
            if '_hwwhww' in name or '_hzzhzz' in name or '_hzzhww' in name:
                signal_4v.Add(temphist)
                if 'C2V' not in name or not isNLO:
                    signal_ggHH_WWWW.Add(temphist)
                else:
                    signal_qqHH_WWWW.Add(temphist)
            if '_htthww' in name or '_htthzz'in name:
                signal_2v2t.Add(temphist)
                if 'C2V' not in name or not isNLO:
                    signal_ggHH_WWTT.Add(temphist)
                else:
                    signal_qqHH_WWTT.Add(temphist)
            if '_htthtt' in name:
                signal_4t.Add(temphist)
                if 'C2V' not in name or not isNLO:
                    signal_ggHH_TTTT.Add(temphist)
                else:
                    signal_qqHH_TTTT.Add(temphist)
            yield_ = temphist.IntegralAndError(0,-1,error)
            if temphist.GetName() not in  yieldDict.keys():
                yieldDict[temphist.GetName()]=[str(yield_),str(error)]
            else:
                newval = float(yieldDict[temphist.GetName()][0]) + yield_
                newerr = math.sqrt(error**2+float(yieldDict[temphist.GetName()][1])**2)
                yieldDict[temphist.GetName()]=[str(newval),str(newerr)]
        elif  ('ggZZ'in name or'qqZZ' in name):
            ZZ.Add(bgshapes.Get(name))
            if 'ggZZ' in name:
                ggZZ.Add(bgshapes.Get(name))
            if 'qqZZ' in name:
                qqZZ.Add(bgshapes.Get(name))
        elif ('DY' in name):
            DY.Add(bgshapes.Get(name))
        elif ('Other' in name):
            Other.Add(bgshapes.Get(name))
        elif ('Flips' in name or 'data_flips' in name or 'flips_mc' in name):
            Flips.Add(bgshapes.Get(name))
        elif ('Convs' in name):
            Convs.Add(bgshapes.Get(name))
        elif( 'TTZ' in name or "TTW" in name):
            TTX.Add(bgshapes.Get(name))
        elif( 'TT' in name):
            TT.Add(bgshapes.Get(name))
        elif ('WZ' in name):
            WZ.Add(bgshapes.Get(name))
        elif ('WW' in name):
            WW.Add(bgshapes.Get(name))
        elif ('W' in name):
            W.Add(bgshapes.Get(name))
        elif ("data_fakes"  in name):
            data_fakes.Add(bgshapes.Get(name))
        #elif ("data" in name and "data_fakes" not in name and 'data_flips' not in name):
         #   print "hello"
         #   data = bgshapes.Get(name)
print signal.Integral(), signal.GetName()
print signal_4v.Integral(), signal_4v.GetName()
print signal_2v2t.Integral(), signal_2v2t.GetName()
print signal_4t.Integral(), signal_4t.GetName()
#if isCR:
#     yieldDict["data_obs"]=[str(data.Integral()),str(0)]
if binfile:
    total = transferHist(oldhist, total,binshapes) 
    err = transferHist(oldhist, err,binshapes) 
    ZZ = transferHist(oldhist, ZZ,binshapes) 
    ggZZ = transferHist(oldhist, ggZZ,binshapes) 
    qqZZ = transferHist(oldhist, qqZZ,binshapes) 
    WZ = transferHist(oldhist, WZ,binshapes) 
    W = transferHist(oldhist, W,binshapes) 
    WW = transferHist(oldhist, WW,binshapes) 
    data_fakes = transferHist(oldhist, data_fakes,binshapes) 
    Flips = transferHist(oldhist, Flips,binshapes) 
    Convs = transferHist(oldhist, Convs,binshapes) 
    TT = transferHist(oldhist, TT,binshapes) 
    TTX = transferHist(oldhist, TTX,binshapes) 
    singleH = transferHist(oldhist, singleH,binshapes) 
    DY = transferHist(oldhist, DY,binshapes) 
    Other = transferHist(oldhist, Other,binshapes) 
    signal = transferHist(oldhist, signal,binshapes) 
    signal_4v = transferHist(oldhist, signal_4v,binshapes) 
    signal_4t = transferHist(oldhist, signal_4t,binshapes) 
    signal_2v2t = transferHist(oldhist, signal_2v2t,binshapes) 
    transferdatax = []
    transferdataexl = []
    transferdataexh = []
    transferdatay = []
    transferdataeyl = []
    transferdataeyh= []
    for i in range(oldhist.GetNbinsX()):
        x = ROOT.Double()
        y = ROOT.Double()
        data.GetPoint(i,x,y)
        if binshapes:
            transferdatax.append(ROOT.Double(oldhist.GetBinCenter(i+1)))
            transferdataexl.append(ROOT.Double(oldhist.GetBinWidth(i+1))/2)
            transferdataexh.append(ROOT.Double(oldhist.GetBinWidth(i+1))/2)
        else:            
            transferdatax.append(ROOT.Double(total.GetBinCenter(i+1)))
            transferdataexl.append(ROOT.Double(total.GetBinWidth(i+1))/2)
            transferdataexh.append(ROOT.Double(total.GetBinWidth(i+1))/2)
        transferdatay.append(y)
        transferdataeyl.append(data.GetErrorYlow(i))
        transferdataeyh.append(data.GetErrorYhigh(i))
    n = len(transferdatax)
    transferdatax = array('f', transferdatax)
    transferdataexl = array('f', transferdataexl)
    transferdataexh = array('f', transferdataexh)
    transferdatay = array('f', transferdatay)
    transferdataeyl = array('f', transferdataeyl)
    transferdataeyh = array('f', transferdataeyh)
    data = ROOT.TGraphAsymmErrors(n, transferdatax, transferdatay, transferdataexl, transferdataexh, transferdataeyl, transferdataeyh)
if isCR and binfile:
    yieldDict["data_obs"]=[str(olddata.Integral()),str(0)]
yield_ = total.IntegralAndError(0,-1,error)
yieldDict['totalBG']=[str(yield_),str(error)]
print 'total', yield_,error
bglist=[]
if paper:
    bglist.append(ZZ)
    bglist.append(WZ)
    bglist.append(singleH)
    bglist.append(data_fakes)
    bglist.append(Flips)
    bglist.append(Convs)
    rare = Other.Clone()
    rare.Add(DY)
    rare.Add(W)
    rare.Add(WW)
    rare.Add(TT)
    rare.Add(TTX)
    bglist.append(rare)
else:
    bglist.append(ZZ)
    bglist.append(WZ)
    bglist.append(W)
    bglist.append(WW)
    bglist.append(data_fakes)
    bglist.append(Flips)
    bglist.append(Convs)
    bglist.append(TT)
    bglist.append(TTX)
    bglist.append(singleH)
    bglist.append(DY)
    bglist.append(Other)




datax = []
dataexl = []
dataexh = []
datay = []
dataeyl = []
dataeyh= []
blindarea = data.GetN()/2
print "1111elf", data.GetN(), sigQuant
if (sigQuant >= 0):
    blindarea = min(sigQuant,data.GetN())
if unblind:
    blindarea = data.GetN()
for i in range(blindarea):
    x = ROOT.Double()
    y = ROOT.Double()
    data.GetPoint(i,x,y)
    datax.append(x)
    dataexl.append(data.GetErrorXlow(i))
    dataexh.append(data.GetErrorXhigh(i))
    datay.append(y)
    dataeyl.append(data.GetErrorYlow(i))
    dataeyh.append(data.GetErrorYhigh(i))
n = len(datax)
datax = array('f', datax)
dataexl = array('f', dataexl)
dataexh = array('f', dataexh)
datay = array('f', datay)
dataeyl = array('f', dataeyl)
dataeyh = array('f', dataeyh)
data_blinded = ROOT.TGraphAsymmErrors(n, datax, datay, dataexl, dataexh, dataeyl, dataeyh)

bglist = sorted(bglist, key=lambda hist: hist.Integral())
bgstack = ROOT.THStack("bgs","bgs")
if not xlabel:
    xlabel = "BDTOutput in background quantiles"
    if sigQuant >= 0:
        xlabel = "BDTOutput in signal quantiles"
if not ylabel:
    ylabel = "Events"
bgstack.SetTitle(";%s; %s"%(xlabel,ylabel))
for hist in bglist:
    if hist.Integral()>0.:
        bgstack.Add(hist)
        err.Add(hist)
        yield_ = hist.IntegralAndError(0,-1,error)
        yieldDict[hist.GetName()]=[str(yield_),str(error)]
        print hist.GetName(), hist.Integral(), error

yield_ = signal_ggHH_WWWW.IntegralAndError(0,-1,error)
yieldDict["signal_ggHH_WWWW"]=[str(yield_),str(error)]
yield_ = signal_qqHH_WWWW.IntegralAndError(0,-1,error)
yieldDict["signal_qqHH_WWWW"]=[str(yield_),str(error)]
yield_ = signal_ggHH_WWTT.IntegralAndError(0,-1,error)
yieldDict["signal_ggHH_WWTT"]=[str(yield_),str(error)]
yield_ = signal_qqHH_WWTT.IntegralAndError(0,-1,error)
yieldDict["signal_qqHH_WWTT"]=[str(yield_),str(error)]
yield_ = signal_ggHH_TTTT.IntegralAndError(0,-1,error)
yieldDict["signal_ggHH_TTTT"]=[str(yield_),str(error)]
yield_ = signal_qqHH_TTTT.IntegralAndError(0,-1,error)
yieldDict["signal_qqHH_TTTT"]=[str(yield_),str(error)]

print total.Integral()
print signal.Integral(), signal.GetName()
print signal_4v.Integral(), signal_4v.GetName()
print signal_2v2t.Integral(), signal_2v2t.GetName()
print signal_4t.Integral(), signal_4t.GetName()
W = 800
H  = 600
T = 0.08*H
B = 0.12*H
L = 0.12*W
R = 0.04*W
c = ROOT.TCanvas("c","c",100,100,W,H)
c.SetFillColor(0)
c.SetBorderMode(0)
c.SetFrameFillStyle(0)
c.SetFrameBorderMode(0)
c.SetLeftMargin( L/W )
c.SetRightMargin( R/W )
c.SetTopMargin( T/H )
c.SetBottomMargin( B/H )
c.SetTickx(0)
c.SetTicky(0)
#c.SetGrid()
c.cd()


CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "       Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()
pad1 = None
pad2 = None
if ratio:
    pad1=ROOT.TPad("pad1","pad1", 0, 0.3,1,1.0)
    pad1.SetBottomMargin(0.025)
    pad1.SetTopMargin(0.1)
    pad1.Draw()
    c.cd()
    pad2=ROOT.TPad("pad2","pad2", 0, 0.05,1,0.3)
    pad2.SetTopMargin(0)
    pad2.SetBottomMargin(0.35)
    pad2.Draw()
    pad1.cd()
latex = ROOT.TLatex()
latex.SetNDC()
latex.SetTextAngle(0)
latex.SetTextColor(ROOT.kRed)    

bgstack.Draw("hist")
if post:
    if unblindSig and not hideSig:
        latex.DrawLatex(0.6,0.55, "postFit")
    else:
        latex.DrawLatex(0.6,0.55, "postFit (blinded signal)")
else:
    if hideSig:
        latex.DrawLatex(0.6,0.55, "preFit")
    else:
        latex.DrawLatex(0.6,0.55, "preFit (no sig)")
bgstack.GetYaxis().SetTitleOffset(1)
if total.GetNbinsX()< 30 and not binfile:
    for i in range(total.GetNbinsX()):
        bgstack.GetXaxis().SetBinLabel(bgstack.GetXaxis().FindBin(i),"bin"+str(i))
if logy:
    bgstack.SetMinimum(minY)
    bgstack.SetMaximum(5000*max(total.GetMaximum(),np.max(datay)))
    if ratio:
        pad1.SetLogy()
    else:
        c.SetLogy()
else:
    bgstack.SetMaximum(max(2*max(total.GetMaximum(),np.max(datay)),3))
if signal.Integral()>0 and not hideSig:
    sig1 = signal.Clone()
    sig2 = signal_4v.Clone()
    sig3 = signal_2v2t.Clone()
    sig4 = signal_4t.Clone()
    if sigScale > 0.:
        sig1.Scale(sigScale)
        sig2.Scale(sigScale)
        sig3.Scale(sigScale)
        sig4.Scale(sigScale)
    yield_ = sig2.IntegralAndError(0,-1,error)
    yieldDict["signal_4vscaled"]=[str(yield_),str(error)]
    yield_ = sig3.IntegralAndError(0,-1,error)
    yieldDict["signal_2v2tscaled"]=[str(yield_),str(error)]
    yield_ = sig4.IntegralAndError(0,-1,error)
    yieldDict["signal_4tscaled"]=[str(yield_),str(error)]
    sig1.Draw("histsame")
    sig2.Draw("histsame")
    sig3.Draw("histsame")
    sig4.Draw("histsame")
err.SetFillColorAlpha(ROOT.kBlack,0.5);
err.SetFillStyle(3018);
err.SetMarkerStyle(0);
err.SetLineColor(0);
err.Draw("E2SAME")
data_blinded.SetMarkerStyle(20)
data_blinded.Draw("e1psame")
#data_blinded.Draw("e1psame")
c.Update()
boxminX = total.GetBinLowEdge(blindarea+1)
boxmaxX = total.GetBinLowEdge(total.GetNbinsX()) + total.GetBinWidth(total.GetNbinsX())
boxmaxY = c.GetUymax()
if ratio: boxmaxY = pad1.GetUymax()
box = ROOT.TBox(boxminX,0.,boxmaxX, boxmaxY)
if logy:
    box = ROOT.TBox(boxminX,0.,boxmaxX, ROOT.TMath.Power(10,boxmaxY))
box.SetFillColorAlpha(ROOT.kGray, 0.5)
box.Draw("same")
legend = ROOT.TLegend(0.2,0.6,0.65,0.9)
if signal.Integral()<=0. or hideSig:
    legend = ROOT.TLegend(0.2,0.6,0.9,0.9)
    legend.SetNColumns(4)
else:
    legend.SetNColumns(3)
legend.SetFillStyle(0);                                                                                                                                                                                    legend.SetTextFont(42);                                                                                                                                                                                    legend.SetBorderSize(0); 
for i in range(len(bglist)):
    hist = bglist[len(bglist)-1-i]
    if hist.Integral()>0:
        tempname = hist.GetName()
        if "fakes" in tempname: tempname = "Fakes"
        if "singleH" in tempname: tempname = "Single Higgs"
        if "Convs" in tempname: tempname = "Conversions"
        if "Other" in tempname: tempname = "Other backgrounds"
        legend.AddEntry(hist, tempname,"F")
legend.AddEntry(err, "Uncertainty", "F")
legend.AddEntry(data_blinded, "data", "E1P")
legend.AddEntry(box, "Blinded", "F")
legend.Draw()


legend_sig = ROOT.TLegend(0.65,0.6,0.95,0.9)
legend_sig.SetFillStyle(0);
legend_sig.SetTextFont(42); 
legend_sig.SetBorderSize(0); 
legend_sig.AddEntry(signal, "Total HH %s"%(signaldesc), "L")
legend_sig.AddEntry(signal_4v, "4V HH %s"%(signaldesc), "L")
legend_sig.AddEntry(signal_2v2t, "2V2T HH %s"%(signaldesc), "L")
legend_sig.AddEntry(signal_4t, "4T HH %s"%(signaldesc), "L")
if signal.Integral()>0 and not hideSig:
    legend_sig.Draw()
data_ratio = None
if ratio:
    pad2.cd()
    r_datax = []
    r_dataexl = []
    r_dataexh = []
    r_datay = []
    r_dataeyl = []
    r_dataeyh= []
    for i in range(data.GetN()):
        x = ROOT.Double()
        y = ROOT.Double()
        data.GetPoint(i,x,y)
        div = ROOT.Double(err.GetBinContent(err.FindBin(x)))
        div = max(div,0.00001)
        print div, y, y/div
        r_datax.append(x)
        r_dataexl.append(data.GetErrorXlow(i))
        r_dataexh.append(data.GetErrorXhigh(i))
        r_datay.append(y/div)
        r_dataeyl.append(data.GetErrorYlow(i)/div)
        r_dataeyh.append(data.GetErrorYhigh(i)/div)
    r_n = len(datax)
    r_datax = array('f', r_datax)
    r_dataexl = array('f', r_dataexl)
    r_dataexh = array('f', r_dataexh)
    r_datay = array('f', r_datay)
    r_dataeyl = array('f', r_dataeyl)
    r_dataeyh = array('f', r_dataeyh)
    data_ratio = ROOT.TGraphAsymmErrors(r_n, r_datax, r_datay, r_dataexl, r_dataexh, r_dataeyl, r_dataeyh)
    err_ratio = err.Clone()
    err_ratio.Divide(err)
    err_ratio.Draw("E2")
    err_ratio.GetYaxis().SetTitleSize(20)
    err_ratio.GetYaxis().SetTitleFont(43)
    err_ratio.GetYaxis().SetTitleOffset(1.)
    err_ratio.GetYaxis().SetLabelSize(15)
    err_ratio.GetYaxis().SetLabelFont(43)
    err_ratio.GetXaxis().SetTitleSize(20)
    err_ratio.GetXaxis().SetTitleFont(43)
    err_ratio.GetXaxis().SetTitleOffset(4)
    err_ratio.GetXaxis().SetLabelSize(15)
    err_ratio.GetXaxis().SetLabelFont(43)
    err_ratio.GetYaxis().SetNdivisions(505)
    # if largeRatio:
    #     err_ratio.SetMaximum(2)
    #     err_ratio.SetMinimum(0)
    #     #if len(Bins)>2:
    #     #    err_ratio.SetMaximum(1.5)
    #     #    err_ratio.SetMinimum(0.5)
    # else:
    #     err_ratio.SetMaximum(1.5)
    #     err_ratio.SetMinimum(0.5)
    #     if len(Bins)>2:
    #         err_ratio.SetMaximum(1.25)
    #         err_ratio.SetMinimum(0.75)
    # if "1l_3tau" in Bin or "0l_4tau" in Bin:
    #         err_ratio.SetMaximum(3)
    #         err_ratio.SetMinimum(-1)
    ratioMax = min(3,max(1.7*err_ratio.GetMaximum(),1.3*max(r_datay)))
    ratioMin = max(-1, 1-abs(ratioMax-1))
    if logy and min(r_datay) == 0:
        ratioMin = 0
    err_ratio.SetMaximum(ratioMax)
    err_ratio.SetMinimum(ratioMin)
    
    err_ratio.SetTitle(";%s;Data/MC"%(bgstack.GetXaxis().GetTitle()))
    err_ratio.Draw("E2")
    # else:
    #     line = ROOT.TF1("line","1", err.GetXaxis().GetXmin(), err.GetXaxis().GetXmax())
    #     line.SetMaximum(1.3)
    #     line.SetMinimum(0.7)
    #     line.GetYaxis().SetTitleSize(20)
    #     line.GetYaxis().SetTitleFont(43)
    #     line.GetYaxis().SetTitleOffset(1.)
    #     line.GetYaxis().SetLabelSize(15)
    #     line.GetYaxis().SetLabelFont(43)
    #     line.GetXaxis().SetTitleSize(20)
    #     line.GetXaxis().SetTitleFont(43)
    #     line.GetXaxis().SetTitleOffset(4)
    #     line.GetXaxis().SetLabelSize(15)
    #     line.GetXaxis().SetLabelFont(43)
    #     line.GetYaxis().SetNdivisions(505)
    #     line.SetTitle(";%s;Data/MC"%(bgstack.GetXaxis().GetTitle()))
    #     line.Draw()
    bgstack.GetXaxis().SetTitleSize(0)
    bgstack.GetXaxis().SetLabelSize(0)
    data_ratio.SetMarkerStyle(20)
    data_ratio.Draw("E1P0")
    box2 = None
    # if "1l_3tau" in Bin or "0l_4tau" in Bin:
    #         box2 = ROOT.TBox(boxminX,-1.,boxmaxX, 3.)
    # elif largeRatio:
    #     if len(Bins)<3:
    #         box2 = ROOT.TBox(boxminX,0.,boxmaxX, 2.)
    #     else:
    #         box2 = ROOT.TBox(boxminX,0.,boxmaxX, 2.)
    # else:
    #     if len(Bins)<3:
    #         box2 = ROOT.TBox(boxminX,0.5,boxmaxX, 1.5)
    #     else:
    #         box2 = ROOT.TBox(boxminX,0.75,boxmaxX, 1.25)
    box2 = ROOT.TBox(boxminX,ratioMin,boxmaxX, ratioMax)
    box2.SetFillColorAlpha(ROOT.kGray, 0.5)
    box2.Draw("same")


CMS_lumi.lumi_sqrtS = lumilabel
if ratio:
    CMS_lumi.CMS_lumi(pad1,0,0)
else:
    CMS_lumi.CMS_lumi(c,0,0)
#ROOT.gPad.SetTicks(1,1)
outname = outPath + "/%s_preFit.pdf"%(analysisInfo )
if logy:
    outname = outPath + "/%s_preFit_log.pdf"%(analysisInfo )
if ratio:
    outname =outname.replace('.pdf','_ratio.pdf')
if post:
    outname =outname.replace('pre','post')
    print 'post!!!!'
c.SaveAs(outname)
c.SaveAs(outname.replace('.pdf','.root'))
c.SaveAs(outname.replace('.pdf','.png'))

yieldjson = json.dumps(yieldDict)
with open(outname.replace('pdf','json'), 'w') as outfile:
    json.dump(yieldjson, outfile)


