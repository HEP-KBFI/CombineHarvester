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
def getLimits(file_name): 
    file = ROOT.TFile(file_name)
    tree = file.Get("limit")
    limits = [ ]
    for quantile in tree:
        limits.append(tree.limit)
    return limits[:6]

A13tev = [62.5088, 345.604, 9.63451, 4.34841, 39.0143, -268.644, -44.2924, 96.5595, 53.515, -155.793, -23.678, 54.5601, 12.2273, -26.8654, -19.3723, -0.0904439, 0.321092, 0.452381, -0.0190758, -0.607163, 1.27408, 0.364487, -0.499263] # from https://github.com/pmandrik/VSEVA/blob/master/HHWWgg/reweight/reweight_HH.C#L117

def functionGF(kl,kt,c2,cg,c2g,A): 
    return A[0] * kt**4 + \
    A[1] * c2**2 + \
    A[2] * kt**2 * kl**2 + \
    A[3] * cg**2 * kl**2 + \
    A[4] * c2g**2 + \
    A[5] * c2 * kt**2 + \
    A[6] * kl * kt**3 + \
    A[7] * kt * kl * c2 + \
    A[8] * cg * kl * c2 + \
    A[9] * c2 * c2g + \
    A[10] * cg * kl * kt**2 + \
    A[11] * c2g * kt**2 + \
    A[12] * kl**2 * cg * kt + \
    A[13] * c2g * kt * kl + \
    A[14] * cg * c2g * kl + \
    A[15] * kt**3 * cg + \
    A[16] * kt * c2 * cg + \
    A[17] * kt * cg**2 * kl + \
    A[18] * cg * kt * c2g + \
    A[19] * kt**2 * cg**2 + \
    A[20] * c2 * cg**2 + \
    A[21] * cg**3 * kl + \
    A[22] * cg**2 * c2g


def getTotalXS(kl, kt, c2, cg, c2g):
    return functionGF(kl,kt,c2,cg,c2g,A13tev)*1.115/1000.


def plotUpperLimits(resultdict, xlabel, ylabel,outpath):
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
    values = []
    for key in resultdict.keys():
        values.append(float(key))
    N = len(values)
    values = sorted(values)
    yellow = ROOT.TGraph(2*N)    # yellow band
    green = ROOT.TGraph(2*N)     # green band
    median = ROOT.TGraph(N)      # median line
    theo = ROOT.TGraph(N)      # theo line
 
    up2s = [ ]
    indx = 0
    i = 0
    for v in values:
        limit = resultdict[str(v)]
        for j in range(len(limit)): limit[j]=limit[j]*getTotalXS(1,1,float(v),0,0)
        print str(v)
        up2s.append(limit[4])
        yellow.SetPoint(    i,    values[i], limit[4] ) # + 2 sigma
        green.SetPoint(     i,    values[i], limit[3] ) # + 1 sigma
        median.SetPoint(    i,    values[i], limit[2] ) # median
        theo.SetPoint(    i,    values[i], getTotalXS(1,1,float(v),0,0) ) # median
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
    frame.GetYaxis().SetTitleOffset(0.95)
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    frame.GetYaxis().SetTitle("95% upper limit on #sigma (gg#rightarrow HH) [pb]")
    frame.GetXaxis().SetTitle(xlabel)
    frame.SetMinimum(miny)
    frame.SetMaximum(max(up2s)*1.05)
    if logy:
        frame.SetMaximum(max(up2s)*15)
    frame.GetXaxis().SetLimits(min(values),max(values))
    yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    theo.SetLineColor(ROOT.kRed)
    theo.SetLineWidth(3)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')
    yellow.Draw('F')
    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')
    theo.Draw('Lsame')
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
    legend.AddEntry(theo,"theo",'L')
    legend.Draw()
    print " "
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
    c2=float((result.split('_')[-1].split('.')[0].replace('m','-')).replace('p','.'))
    #c2 = result.split('_')[-1].split('.')[0]
    resultdict[str(c2)]=getLimits(result)
    
plotUpperLimits(resultdict, 'C2', ylabel, outPath)
