#!/usr/bin/env python
import os, shlex
import subprocess
import glob
import shutil
import ROOT
ROOT.gROOT.SetBatch(True)
from collections import OrderedDict
import CMS_lumi, tdrstyle
from optparse import OptionParser
parser = OptionParser()


parser.add_option("--inputPath", type="string", dest="inputPath", help="Full path of where combine results are")
parser.add_option("--outPath", type="string", dest="outPath", help="Full path to store plot ")
parser.add_option("--spinCase", type="string", dest="spinCase", help="spin case")
parser.add_option("--ylabel", type="string", dest="ylabel", help="plot label")
parser.add_option("--log", action='store_true',dest="logy", default=False)
parser.add_option("--min", type="float", dest="miny", help="min y", default = 0.0)
(options, args) = parser.parse_args()
inputPath = options.inputPath
outPath = options.outPath
spinCase = options.spinCase
ylabel = options.ylabel
logy = options.logy
miny = options.miny

print "outPath: %s" % (outPath)
if outPath.endswith((".pdf", ".root")):
    print 'outPath.endswith((.pdf, .root))'
    outPath0 = outPath[:outPath.rfind('/')]
    print "outPath0: %s" % (outPath0)
    if not os.path.exists(outPath0):
        print "mkdir %s" % (outPath0)
        os.makedirs(outPath0)
    '''elif not os.path.exists(outPath):
        os.makedirs(outPath)'''

def getLimits(file_name): 
    file = ROOT.TFile(file_name)
    tree = file.Get("limit")
    limits = [ ]
    for quantile in tree:
        limits.append(tree.limit)
    return limits[:6]

def plotUpperLimits(resultdict, xlabel, ylabel,outpath):
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
    values = []
    for key in resultdict.keys():
        values.append(int(key))
    N = len(values)
    values = sorted(values)
    yellow = ROOT.TGraph(2*N)    # yellow band
    green = ROOT.TGraph(2*N)     # green band
    median = ROOT.TGraph(N)      # median line
 
    up2s = [ ]
    indx = 0
    i = 0
    for v in values:
        limit = resultdict[str(v)]
        print str(v)
        up2s.append(limit[4])
        yellow.SetPoint(    i,    values[i], limit[4] ) # + 2 sigma
        green.SetPoint(     i,    values[i], limit[3] ) # + 1 sigma
        median.SetPoint(    i,    values[i], limit[2] ) # median
        green.SetPoint(  2*N-1-i, values[i], limit[1] ) # - 1 sigma
        yellow.SetPoint( 2*N-1-i, values[i], limit[0] ) # - 2 sigma
        i = i + 1
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
    frame = c.DrawFrame(1.4,0.001, 4.1, 10)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    frame.GetYaxis().SetTitle("95% upper limit on #sigma (#Chi#rightarrow hh) [pb]")
    frame.GetXaxis().SetTitle(xlabel)
    frame.SetMinimum(miny)
    frame.SetMaximum(max(up2s)*1.05)
    if logy:
        frame.SetMaximum(max(up2s)*15)
    frame.GetXaxis().SetLimits(min(values),max(values))
    yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')
    yellow.Draw('F')
    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')
    if logy:
        c.SetLogy()
    median.SetLineColor(1)
    median.SetLineWidth(2)
    median.SetLineStyle(2)
    median.Draw('Lsame')
    CMS_lumi.lumi_sqrtS = ylabel
    CMS_lumi.CMS_lumi(c,0,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')
 
    x1 = 0.55
    x2 = x1 + 0.24
    y2 = 0.76
    y1 = 0.60
    legend = ROOT.TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.AddEntry(median, "Asymptotic CL_{s} expected",'L')
    legend.AddEntry(green, "#pm 1 std. deviation",'f')
    legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    legend.Draw()
    print outpath
    c.SaveAs(outpath)
    c.SaveAs(outpath.replace('.pdf','.root'))
    c.Close()
 

# CMS style
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()

listproc = glob.glob( "%s/*.root" % inputPath)
resultdict = {}
for result in listproc:
    if 'WS' in result: continue
    if 'overlap' in result:
        mass = result.split('/')[-1].split('.')[0][12:15]
        resultdict[mass+'_overlap']=getLimits(result)
        continue
    mass = result.split('/')[-1].split('.')[0][12:15]
    if mass == '100': mass = '1000'
    resultdict[mass]=getLimits(result)
plotUpperLimits(resultdict, 'm#Chi [GeV] (%s)'%spinCase, ylabel, outPath)
