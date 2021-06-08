#!/usr/bin/env python
import os, shlex
from subprocess import Popen, PIPE
import glob
import shutil
import ROOT
import math
from collections import OrderedDict
import numpy as np
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputPath", type="string", dest="inputPath", help="Full path of where prepareDatacards.root are ")
parser.add_option("--card",      type="string", dest="card",      help="name of prepareDatacards.root. In not given will pick all from the inputPath", default="none")
parser.add_option("--threshold",      type="float", dest="threshold",      help="relativ bin error threshold", default=0.3)
parser.add_option("--quantSig", action='store_true',dest="quantSig", default=False)
(options, args) = parser.parse_args()

inputPath = options.inputPath
card      = options.card
threshold = options.threshold
quantSig = options.quantSig
def checkIfLabeledHistogram(hist):
    areAllLabelled = True
    nofBins = hist.GetNbinsX() + 1
    for i in range(1,nofBins+1):
        binLabel = hist.GetXaxis().GetBinLabel(i)
        if not binLabel: areAllLabelled = False
    return areAllLabelled

def compIntegral(hist, und, ov):
    nBins = hist.GetNbinsX()
    first = 1
    last = nBins
    if und: first = 0
    if ov: last = last +1
    content = 0
    for i in range(first, last+1):
        content = content + hist.GetBinContent(i)
    return content

def makeBinContentsPositive(hist):
    integral_original = max(0.,compIntegral(hist,False, False))
    isLabelled = checkIfLabeledHistogram(hist)
    initBin = 0
    if isLabelled: initBin = 1
    endBin = hist.GetNbinsX()+2
    if isLabelled: endBin = endBin -1
    changedBin = False
    for i in range(initBin,endBin):
        binContent_original = hist.GetBinContent(i)
        binError2_original = hist.GetBinError(i)*hist.GetBinError(i)
        if binContent_original < 0.:
            print "Correcting possible negative bins in:" + hist.GetName()
            print "Changing bin content"
            changedBin = True
            binContent_modified = 0.
            binError2_modified = binError2_original + (binContent_original - binContent_modified)*(binContent_original - binContent_modified)
            hist.SetBinContent(i, binContent_modified)
            hist.SetBinError(i,math.sqrt(binError2_modified))
    integral_modified = max(0.,compIntegral(hist, False, False))
    if integral_original > 0. and integral_modified > 0.:
        if not (integral_original==integral_modified):
            sf = integral_original / integral_modified
            for i in range(initBin, endBin):
                binContent = hist.GetBinContent(i)
                hist.SetBinContent(i, sf*binContent)
    elif ('dats_obs' not in hist.GetName()):
        for i in range(initBin, endBin):
            hist.SetBinContent(i, 0.001/((endBin - 1) - initBin))
    if changedBin: print "integral old,new,corrected",integral_original,integral_modified,compIntegral(hist, False, False)
    return hist

def getQuantiles(inputShapesL):
    tfilein = ROOT.TFile(inputShapesL, "READ")
    bgs = ROOT.TH1F()
    sig = ROOT.TH1F()
    x_final = np.array([0.])
    bestscore = 0
    nb = 0
    ns = 0
    for nkey, key in enumerate(tfilein.GetListOfKeys()) :
        name = key.GetName()
        if not ('signal' in name or 'CMS' in name or 'fakes_mc' in name or 'data_obs' in name or 'flips_mc' in name):
            obj = key.ReadObj()
            obj.Sumw2()
            if nb is 0:
                bgs = obj.Clone()
            else:
                bgs.Add(obj)
            nb = nb + 1
        if ('signal' in name and 'CMS' not in name):
            obj = key.ReadObj()
            if ns is 0:
                sig = obj.Clone()
            else:
                sig.Add(obj)
            ns = ns + 1
    possible_quantiles=[]
    possible_quantiles_errors=[]
    for i in range(30):
        nq = 30-i
        if nq < 5: continue
        bgs_test=bgs.Clone()
        sig_test=sig.Clone()
        y = []
        x = []
        for j in range(nq):
            y.append(j*(1./nq))
            x.append(0.)
        y = np.array(y)
        x = np.array(x)
        quant = None
        if quantSig:
            quant= sig_test.GetQuantiles(nq,x,y)
        else:
            quant= bgs_test.GetQuantiles(nq,x,y)
        x = np.append(x,np.array([1.]))
        print 'x============ ', x
        low_bins = []
        for en in range(len(x)-1):
            low_bins.append(bgs_test.FindBin(x[en]))
        print 'low========', low_bins
        if nq < 10:
            for b in low_bins[:]:
                if low_bins.count(b)>1: low_bins.append(b+1)
        low_bins = sorted(list(set(low_bins)))
        print 'af======= ', low_bins
        better_x = []
        for b in low_bins:
            better_x.append(bgs_test.GetBinLowEdge(b))
        better_x[0] = 0.
        better_x=np.array(better_x)
        x = np.append(better_x,np.array([1.]))
        quantileOk= True
        bgs_test= bgs_test.Rebin(len(x)-1,bgs_test.GetName() ,x)
        sig_test= sig_test.Rebin(len(x)-1,sig_test.GetName() ,x)
        temp_binerrors = []
        for j in range(bgs_test.GetNbinsX()):
            if(bgs_test.GetBinContent(j+1)>0):
                quantileOk = quantileOk and bgs_test.GetBinError(j+1)/bgs_test.GetBinContent(j+1)<threshold
                temp_binerrors.append(bgs_test.GetBinError(j+1)/bgs_test.GetBinContent(j+1))
            else:
                quantileOk = False
        if quantileOk or len(x)<=6:
            possible_quantiles.append(x)
            possible_quantiles_errors.append(temp_binerrors)
        del bgs_test, x,y
    binerrors_final =[]
    for b, binning in enumerate(possible_quantiles):
        bgs_test=bgs.Clone()
        sig_test=sig.Clone()
        bgs_test= bgs_test.Rebin(len(binning)-1,bgs_test.GetName() ,binning)
        sig_test= sig_test.Rebin(len(binning)-1,sig_test.GetName() ,binning)
        score = 0
        for j in range(bgs_test.GetNbinsX()):
            if (bgs_test.GetBinContent(j+1)>0): score = score + sig_test.GetBinContent(j+1)*sig_test.GetBinContent(j+1)/bgs_test.GetBinContent(j+1)
        score = math.sqrt(score)
        if score > bestscore:
            bestscore = score
            x_final = binning
            binerrors_final = possible_quantiles_errors[b]
    tfilein.Close()
    print 'Final bin errors:', binerrors_final
    return x_final

def rebin (inputShapesL, inputShapesLnew, bins) :
    tfilein1 = ROOT.TFile(inputShapesL, "READ")
    tfileout2 = ROOT.TFile(inputShapesLnew, "RECREATE")
    tfilein1.cd()
    for nkey, key in enumerate(tfilein1.GetListOfKeys()) :
        obj =  key.ReadObj()
        obj_name = key.GetName()
        if type(obj) is not ROOT.TH1F :
            if type(obj) is ROOT.TH1 :
                print ("data_obs can be be TH1")
                continue
            else :
                print ("WARNING: All the histograms that are not data_obs should be TH1F - otherwhise combine will crash!!!")
                sys.exit()
        tfileout2.cd()
        nominal  = ROOT.TH1F()
        nominal = obj.Rebin(len(bins)-1,obj.GetName() , bins)
        if not ('data_obs' in key.GetName()):  nominal = makeBinContentsPositive(nominal)
        nominal.Write()
        tfilein1.cd()
    tfilein1.Close()
    tfileout2.Close()


inputPathNew = "%s/rebinned_quantile/" % (inputPath)
try :
    os.mkdir( inputPathNew )
except :
    print ("already exists: ", inputPathNew)
print ("\n copied \n %s to \n %s \nto have cards with renamed processes" % (inputPath, inputPathNew))

if card == "none" :
    listproc = glob.glob( "%s/*.root" % inputPath)
else :
    listproc = [ "%s/%s" % (inputPath, card) ]

for prepareDatacard in listproc :
    prepareDatacardNew = prepareDatacard.replace(inputPath, inputPathNew)
    if ('MVAOutput' in str(prepareDatacardNew)):
        bins = getQuantiles(prepareDatacard)
        print bins, len(bins)
        rebin(prepareDatacard,prepareDatacardNew, bins)
    print ("done", prepareDatacardNew)
