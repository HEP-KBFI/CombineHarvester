#!/usr/bin/env python                                                                                                                                                                                       
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
parser = OptionParser()
parser.add_option("--inputCard", type="string", dest="inputCard", help="Full path where the datacard is")
parser.add_option("--outPath", type="string", dest="outPath", help="Full path to store plot and ws")
parser.add_option("--Info", type="string", dest="analysisInfo", help="analysis info e.g. 3l_1tau_2016_nonResLO_SM")
parser.add_option("--ylabel", type="string", dest="ylabel", help="plot label")
parser.add_option("--log", action='store_true',dest="logy", default=False)
parser.add_option("--NLO", action='store_true',dest="NLO", default=False)
parser.add_option("--skipCombine", action='store_true',dest="skipCombine", default=False)
parser.add_option("--Bin", type="string", dest="Bin", help="Bin in datacard to plot")
parser.add_option("--sigDesc", type="string", dest="sigDesc", help="Additional sig description")
(options, args) = parser.parse_args()
inputCard = options.inputCard   
outPath = options.outPath
ylabel = options.ylabel
logy = options.logy
signaldesc = options.sigDesc
Bin = options.Bin
analysisInfo = options.analysisInfo
skipCombine=options.skipCombine 
isNLO = options.NLO
# Bin = "HH_3l_1tau"                                                                                                                                                                                        
# logy = True                                                                                                                                                                                               
# ylabel="hh-multilepton 3l1tau (2016)"                                                                                                                                                                     
# signaldesc= "SM (1pb)"                                                                                                                                                                                    
# outPath=options.outPath                                                                                                                                                                                   


commands = []
wspath="%s/ws_%s.root"%(outPath,analysisInfo)
commands.append("text2workspace.py %s -o %s -m 125"%(inputCard,wspath))
commands.append("combineTool.py -M FitDiagnostics -d %s --saveShapes --saveWithUncertainties  --saveNormalization  --skipBOnlyFit -n _%s -m 125"%(wspath, analysisInfo))
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

fitfile = ROOT.TFile("%s/fitDiagnostics_%s.root"%(outPath, analysisInfo))

prefitshapefolder=fitfile.Get("shapes_prefit")
prefitshapes= prefitshapefolder.Get(Bin)
yieldDict = {}
total = fitfile.Get("shapes_prefit/%s/total_background"%(Bin))
error = ROOT.Double(0.)
yield_ = total.IntegralAndError(0,-1,error)
yieldDict['totalBG']=[str(yield_),str(error)]
print 'total', yield_,error
total.SetLineColor(0)
total.SetFillColor(0)
ZZ  = ROOT.TH1D("ZZ", "ZZ", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
ZZ.SetLineColor(634)
ZZ.SetFillColor(634)
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
Flips.SetLineColor(0)
Flips.SetFillColor(1)
Flips.SetFillStyle(3004)
Convs  = ROOT.TH1D("Convs", "Convs", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
Convs.SetLineColor(0)
Convs.SetFillColor(1)
Convs.SetFillStyle(3005)
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
data_fakes  = ROOT.TH1D("data_fakes", "data_fakes", total.GetNbinsX(),total.GetXaxis().GetXmin(),total.GetXaxis().GetXmax())
data_fakes.SetLineColor(0)
data_fakes.SetFillColor(2)
data_fakes.SetFillStyle(3005)

bglist=[]
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
data = None
for entry in prefitshapes.GetListOfKeys():
    name = entry.GetName()
    if 'total' in name:
        continue
    elif ('ggH_' in name or 'qqH_' in name or 'TTH_' in name or 'tHq_' in name or 'tHW_' in name or 'WH_' in name or 'ZH_' in name):
        singleH.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif ('ggHH' in name or 'qqHH' in name or 'signal' in name):
        if (isNLO and not ('kl_1_kt_1_' in name or 'CV_1_C2V_1_kl_1_' in name)): continue
        temphist =fitfile.Get("shapes_prefit/%s/%s"%(Bin,name))
        signal.Add(temphist)
        if '_hwwhww' in name or '_hzzhzz' in name or '_hzzhww' in name:
            signal_4v.Add(temphist)
        if '_htautauhww' in name or '_htautauhzz'in name:
            signal_2v2t.Add(temphist)
        if '_htautauhtautau' in name:
            signal_4t.Add(temphist)
        yield_ = temphist.IntegralAndError(0,-1,error)
        yieldDict[temphist.GetName()]=[str(yield_),str(error)]
    elif  ('ggZZ'in name or'qqZZ' in name):
        ZZ.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif ('DY' in name):
        DY.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif ('Other' in name):
        Other.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif ('Flips' in name):
        Flips.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif ('Convs' in name):
        Flips.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif( 'TTZ' in name or "TTW" in name):
        TTX.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif( 'TT' in name):
        TT.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif ('WZ' in name):
        WZ.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif ('WW' in name):
        WW.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif ('W' in name):
        W.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)) )
    elif ("data_fakes"  in name):
        data_fakes.Add(fitfile.Get("shapes_prefit/%s/%s"%(Bin,name)))
    elif ("data" in name and "data_fakes" not in name):
        print "hello"
        data = fitfile.Get("shapes_prefit/%s/%s"%(Bin,name))

datax = []
dataexl = []
dataexh = []
datay = []
dataeyl = []
dataeyh= []
maxx = 0
for i in range(data.GetN()/2):
    x = ROOT.Double()
    y = ROOT.Double()
    data.GetPoint(i,x,y)
    maxx=x
    datax.append(x)
    print i, x, y
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
bgstack.SetTitle(";BDTOutput in BG quantiles; Events")
for hist in bglist:
    if hist.Integral()>0.:
        bgstack.Add(hist)
        yield_ = hist.IntegralAndError(0,-1,error)
        yieldDict[hist.GetName()]=[str(yield_),str(error)]
    print hist.GetName(), hist.Integral()
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
c.SetGrid()
c.cd()


CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "       Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()
bgstack.Draw("hist")
bgstack.GetYaxis().SetTitleOffset(1)
for i in range(total.GetNbinsX()):
    bgstack.GetXaxis().SetBinLabel(bgstack.GetXaxis().FindBin(i),"bin"+str(i))
if logy:
    bgstack.SetMinimum(0.001)
    bgstack.SetMaximum(5000*total.GetMaximum())
    c.SetLogy()
else:
    bgstack.SetMaximum(4*total.GetMaximum())
signal.Draw("histsame")
signal_4v.Draw("histsame")
signal_2v2t.Draw("histsame")
signal_4t.Draw("histsame")
total.SetFillColorAlpha(ROOT.kBlack,0.8);
total.SetFillStyle(3013);
total.SetMarkerStyle(0);
total.SetLineColor(0);
total.Draw("E2SAME");
data_blinded.SetMarkerStyle(20)
data_blinded.Draw("e1psame")
#data_blinded.Draw("e1psame")
c.Update()
box = ROOT.TBox(maxx+0.5,0.,data.GetN(), c.GetUymax())
if logy:
    box = ROOT.TBox(maxx+0.5,0.,data.GetN(), ROOT.TMath.Power(10,c.GetUymax()))
box.SetFillColorAlpha(ROOT.kGray, 0.5)
box.Draw("same")
legend = ROOT.TLegend(0.2,0.6,0.55,0.9)
legend.SetNColumns(3)
legend.SetFillStyle(0);                                                                                                                                                                                    legend.SetTextFont(42);                                                                                                                                                                                    legend.SetBorderSize(0); 
for i in range(len(bglist)):
    hist = bglist[len(bglist)-1-i]
    if hist.Integral()>0:
        legend.AddEntry(hist, hist.GetName(),"F")
legend.AddEntry(total, "BG Error", "F")
legend.AddEntry(data_blinded, "data", "E1P")
legend.AddEntry(box, "Blinded Window", "F")
legend.Draw()


legend_sig = ROOT.TLegend(0.55,0.6,0.9,0.9)
legend_sig.SetFillStyle(0);
legend_sig.SetTextFont(42); 
legend_sig.SetBorderSize(0); 
legend_sig.AddEntry(signal, "Total HH %s signal"%(signaldesc), "L")
legend_sig.AddEntry(signal_4v, "4V HH %s signal"%(signaldesc), "L")
legend_sig.AddEntry(signal_2v2t, "2V2T HH %s signal"%(signaldesc), "L")
legend_sig.AddEntry(signal_4t, "4T HH %s signal"%(signaldesc), "L")
legend_sig.Draw()
CMS_lumi.lumi_sqrtS = ylabel
CMS_lumi.CMS_lumi(c,0,0)
ROOT.gPad.SetTicks(1,1)
outname = outPath + "/%s_preFit.pdf"%(analysisInfo)
if logy:
    outname = outPath + "/%s_preFit_log.pdf"%(analysisInfo)
c.SaveAs(outname)
c.SaveAs(outname.replace('.pdf','.root'))

yieldjson = json.dumps(yieldDict)
with open(outname.replace('pdf','json'), 'w') as outfile:
    json.dump(yieldjson, outfile)


