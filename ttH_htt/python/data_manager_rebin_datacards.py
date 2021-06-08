import ROOT
from ROOT import *
import array as arr
import math
from math import sqrt, sin, cos, tan, exp
import sys, os, re, shlex
from subprocess import Popen, PIPE
import glob

global testPrint
def testPrint() :
    print ("loaded data_manager_rebin_datacards")

global runCombineCmd
def runCombineCmd(combinecmd, outfolder='.', saveout=None):
    print ("Command: ", combinecmd)
    try:
        p = Popen(shlex.split(combinecmd) , stdout=PIPE, stderr=PIPE, cwd=outfolder)
        comboutput = p.communicate()[0]
    except OSError:
        print ("command not known\n", combinecmd)
        comboutput = None
    if not saveout == None :
        if saveout.startswith("/") : saveTo = saveout
        else : saveTo = outfolder + "/" + saveout
        with open(saveTo, "w") as text_file:
            text_file.write(unicode(comboutput))
        print ("Saved result to: " + saveTo)
    print ("\n")
    return comboutput

global finMaxMin
def finMaxMin(histSource) :
    file = TFile(histSource+".root","READ")
    file.cd()
    hSum = TH1F()
    for keyO in file.GetListOfKeys() :
       obj =  keyO.ReadObj()
       if type(obj) is not TH1F : continue
       hSumDumb = obj.Clone()
       if not hSum.Integral()>0 : hSum=hSumDumb
       else : hSum.Add(hSumDumb)
    return [
    [hSum.GetBinLowEdge(1),  hSum.GetBinCenter(hSum.GetNbinsX())+hSum.GetBinWidth(hSum.GetNbinsX())/2.],
    [hSum.GetBinLowEdge(hSum.FindFirstBinAbove(0.0)),  hSum.GetBinCenter(hSum.FindLastBinAbove (0.0))+hSum.GetBinWidth(hSum.FindLastBinAbove (0.0))/2.]]
    return 0

global getQuantiles
def getQuantiles(histoP, ntarget, xmax) :
    histoP.Scale(1./histoP.Integral())
    histoP.GetCumulative()
    histoP.GetXaxis().SetRangeUser(0.,1.)
    histoP.GetYaxis().SetRangeUser(0.,1.)
    histoP.SetMinimum(0.0)
    xq    = arr.array('d', [0.] * (ntarget+1))
    yq    = arr.array('d', [0.] * (ntarget+1))
    yqbin = arr.array('d', [0.] * (ntarget+1)) # +2 if firsrt is not zero
    for  ii in range(0,ntarget) :
        xq[ii] = (float(ii)/(ntarget))
    xq[ntarget] = 0.999999999
    #xq = arr.array('d', [0, .16, .32, .48, .64, .80, .84, .88, .92, .96, .99999])
    histoP.GetQuantiles(ntarget, yq, xq)
    line = [None for point in range(ntarget)]
    line2 = [None for point in range(ntarget)]
    for  ii in range(1,ntarget+1) : yqbin[ii]=yq[ii]
    yqbin[ntarget] = xmax
    return yqbin
global rebinHistogram_binindex
def rebinHistogram_binindex(histogram) :
  numBins = histogram.GetNbinsX()
  histogram_rebinned = TH1F()
  histogram_rebinned = TH1F(histogram.GetName(), histogram.GetName(),  numBins, 0.5, numBins + 0.5)
  if not histogram_rebinned.GetSumw2N() : histogram_rebinned.Sumw2()
  histogram_rebinned.Reset()
  for idxBin in range(1, numBins+1) : # CV: include underflow and overflow bins
    binContent = histogram.GetBinContent(idxBin)
    binError = histogram.GetBinError(idxBin)
    histogram_rebinned.SetBinContent(idxBin, binContent)
    histogram_rebinned.SetBinError(idxBin, binError)
  return histogram_rebinned
global getHist_tobeFlat
def getHist_tobeFlat(hist_dict, histSource) :
    for key in hist_dict.keys() :
        print 'key========', key, histSource
        if 'LBN_%s' %key in histSource :
            print 'found key====== ', key
            return hist_dict[key]
        elif 'LBN_SingleTop' in histSource and 'ST' in key:
            return hist_dict['ST']
global rebinRegular
def rebinRegular(
    histSource,
    nbin,
    BINtype,
    do_signalFlat,
    merge_Wjets,
    originalBinning,
    doplots,
    bdtType,
    outdir,
    nameOutFileAddL,
    withFolder=False,
    partialCopy=False
    ) :
    print ("rebinRegular")
    nQuantMax = 36
    minmax = finMaxMin(histSource) # [[0], [1]], [0]=first, last bin above 0; [1]= their corresponding x-value
    errOcontTTLast=[]
    errOcontTTPLast=[]
    errOcontSUMLast=[]
    errOcontSUMPLast=[]
    #
    errTTLast=[]
    contTTLast=[]
    errSUMLast=[]
    contSUMLast=[]
    #
    realbins=[]
    xminbin=[]
    xmaxbin=[]
    xmaxLbin=[]
    #
    lastQuant=[]
    xmaxQuant=[]
    xminQuant=[]
    #
    if BINtype=="ranged" :
        xmin=minmax[1][0]
        xmax=minmax[1][1]
        xmindef=minmax[1][0]
        xmaxdef=minmax[1][1]
    else :
        if minmax[1][0] < 0 and not withFolder: xmin=-1.0
        else : xmin=0.0
        xmax=1.0
        xmaxdef=minmax[1][1]
        xmindef=minmax[1][0]
    #print ("enumerate(nbin): ",enumerate(nbin), ", nbin: ",nbin)
    isMoreThan02 = 0
    bin_isMoreThan02 = 0
    nonOther = ["TT", 'WJets', 'DY', 'ST', 'data_obs', 'Fakes', 'fakes_mc']
    if merge_Wjets: nonOther.remove('WJets')
    for nn,nbins in enumerate(nbin) :
        print ("nbins: %s" % nbins)
        file = TFile("%s.root" % histSource ,"READ");
        print ("Opened %s.root" % histSource)
        file.cd()
        histograms=[]
        histograms2=[]
        h2 = TH1F()
        hSum = TH1F()
        hFakes = TH1F()
        hSumAll = TH1F()
        hSumSignal = TH1F()
        ratiohSum=1.
        ratiohSumP=1.
        name = histSource.split("/")[len(histSource.split("/"))-1] + "_" + str(nbins) + nameOutFileAddL + ".root"
        nameOutFile = "%s/%s" % (outdir, name)
        fileOut  = TFile(nameOutFile, "recreate")
        print ("created %s" % nameOutFile)
        hist_dict = {}
        if withFolder :
            folders_Loop = file.GetListOfKeys()
        else :
            folders_Loop = ["none"]
        for nkey, keyF in enumerate(folders_Loop) :
            print ("nkey: ",nkey,", keyF: ",keyF)
            if withFolder :
                if partialCopy :
                    print str(source), '\t', str(keyF.GetName())
                    if str(source) not in str(keyF.GetName()) : continue
                obj =  keyF.ReadObj()
                loop_on = obj.GetListOfKeys()
                histograms=[]
                histograms2=[]
                h2 = TH1F()
                hSum = TH1F()
                hFakes = TH1F()
                hSumAll = TH1F()
                hSumSignal = TH1F()
                ratiohSum=1.
                ratiohSumP=1.
            else :
                loop_on = file.GetListOfKeys()
            print ("withFolder", withFolder)
            for keyO in loop_on :
               #print ("keys ", keyF.GetName(), keyO.GetName() )
               print ("keys ", keyO )
               if not withFolder :
                   #print "got histogram"
                   obj = keyO.ReadObj()
                   if type(obj) is not TH1F :
                       continue
                   h2  = obj.Clone()
                   #print h2.GetName()
               else :
                   print "got histogram"
                   obj = keyO.ReadObj()
                   if type(obj) is not TH1F :
                       continue
                   h2  = obj.Clone()
                   print (h2.GetName(), h2.Integral())
                   if h2.GetName().find('CMS') == -1 and h2.GetName().find('HH') == -1 and h2.GetName().find('hh') == -1:
                       print 'name=========== ', h2.GetName()
                       if h2.GetName() not in nonOther:
                           if "Other" not in hist_dict.keys() :
                               print 'other========= ', h2.GetName()
                               hist_dict["Other"] = h2
                               hist_dict["Other"].Sumw2()
                           else:
                               print 'other===========', h2.GetName()
                               hist_dict["Other"].Add(h2)
                       else:
                           dictkey = h2.GetName().replace('WJets', 'W')
                           hist_dict[dictkey] = h2
               factor=1.
               if  not h2.GetSumw2N() :
                   h2.Sumw2()
               if  not hSum.GetSumw2N() :
                   hSum.Sumw2()
               if withFolder :
                   h2.SetName(str(h2.GetName()))
               histograms.append(h2.Clone())
               if "fakes_data" in h2.GetName() : hFakes=h2.Clone()
               if (h2.GetName().find("HH") ==-1 or h2.GetName().find("hh") ==-1) and h2.GetName().find("data_obs") ==-1  and h2.GetName().find("fakes_mc") ==-1 and h2.GetName().find("CMS") ==-1: # and "DY" in h2.GetName()
                   #hSumDumb2 = obj # h2_rebin #
                   if BINtype=="quantiles" :
                       print ("sum to quantiles in BKG:", h2.GetName(), h2.Integral())
                   if not hSumAll.Integral()>0 :
                       hSumAll=h2.Clone()
                       hSumAll.Sumw2()
                       hSumAll.SetName("hSumAllBk1")
                   else :
                       hSumAll.Add(h2)
               if (h2.GetName().find("hh") != -1 or h2.GetName().find('HH') != -1) and h2.GetName().find("CMS") ==-1:
                    print 'signal=========', h2.GetName()
                    if not hSumSignal.Integral()>0 :
                        hSumSignal=h2.Clone()
                        hSumSignal.Sumw2()
                        hSumSignal.SetName("hSumSignal")
                    else:
                        hSumSignal.Add(h2)
            #################################################
            hist_dict["HH"] = hSumSignal
            print ("Sum of BKG: ", hSumAll.Integral(), ", hFakes.Integral: ",hFakes.Integral())
            if BINtype=="quantiles" :
                if do_signalFlat :
                    if histSource.find('LBN') != -1:
                        hist_tobeFlat = getHist_tobeFlat(hist_dict, histSource)
                        print 'tobeflat============ ', hist_tobeFlat.GetName()
                        nbinsQuant =  getQuantiles(hist_tobeFlat, nbins, xmax)
                    else :
                        nbinsQuant =  getQuantiles(hSumSignal, nbins, xmax)
                else  :
                    nbinsQuant =  getQuantiles(hSumAll, nbins, xmax)
            ## nbins+1 if first quantile is zero ## getQuantiles(hFakes,nbins,xmax) #
            #print ("Bins by quantiles ",nbins,nbinsQuant)
            if withFolder :
                fileOut.mkdir(keyF.GetName()+"/")
            hTTi = TH1F()
            hTTHi = TH1F()
            hTHi = TH1F()
            hEWKi = TH1F()
            hTTWi = TH1F()
            hRaresi = TH1F()
            histo = TH1F()
            for nn1, histogram in enumerate(histograms) :
                #print ("nn1: ",nn1,", histogram: ",histogram,", histo:",histo.GetName())
                #if BINtype=="quantiles" : ### fix that -- I do not want these written to the file
                histogramCopy=histogram.Clone()
                nameHisto=histogramCopy.GetName()
                histogram.SetName(histogramCopy.GetName())
                histogramCopy.SetName(histogramCopy.GetName())
                if BINtype=="none" :
                    histo=histogramCopy.Clone()
                    histo.SetName(nameHisto)
                elif BINtype=="ranged" or BINtype=="regular" :
                    histo= TH1F( nameHisto, nameHisto , nbins , xmin , xmax)
                elif BINtype=="quantiles" :
                    xmaxLbin=xmaxLbin+[nbinsQuant[nbins-2]]
                    histo=TH1F( nameHisto, nameHisto , nbins , nbinsQuant) # nbins+1 if first is zero
                elif BINtype=="mTauTauVis" :
                    histo= TH1F( nameHisto, nameHisto , nbins , 0. , 200.)
                histo.Sumw2()
                #if BINtype=="quantiles" : ### fix that -- I do not want these written to the file
                for place in range(0,histogramCopy.GetNbinsX() + 1) :
                    content =      histogramCopy.GetBinContent(place)
                    #if content < 0 : continue # print (content,place)
                    binErrorCopy = histogramCopy.GetBinError(place);
                    newbin =       histo.GetXaxis().FindBin(histogramCopy.GetXaxis().GetBinCenter(place))
                    binError =     histo.GetBinError(newbin);
                    contentNew =   histo.GetBinContent(newbin)
                    histo.SetBinContent(newbin, content+contentNew)
                    histo.SetBinError(newbin, sqrt(binError*binError+binErrorCopy*binErrorCopy))
                if do_signalFlat :
                    histo = rebinHistogram_binindex(histo)
                if "fakes_data" in histo.GetName() and nkey == 0 :
                    ratio=1.
                    ratioP=1.
                    hTTi=histo.Clone()
                    hTTi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                    if histo.GetBinContent(histo.GetNbinsX()) >0 : ratio=histo.GetBinError(histo.GetNbinsX())/histo.GetBinContent(histo.GetNbinsX())
                    if histo.GetBinContent(histo.GetNbinsX()-1) >0 : ratioP=histo.GetBinError(histo.GetNbinsX()-1)/histo.GetBinContent(histo.GetNbinsX()-1)
                    errOcontTTLast = errOcontTTLast+[ratio] if ratio<1.01 else errOcontTTLast+[1.0]
                    errOcontTTPLast = errOcontTTPLast+[ratioP] if ratioP<1.01 else errOcontTTPLast+[1.0]
                    errTTLast=errTTLast+[histo.GetBinError(histo.GetNbinsX())]
                    contTTLast=contTTLast+[histo.GetBinContent(histo.GetNbinsX())]
                if "TTZ" in histo.GetName() or "TTW" in histo.GetName()  :
                    if not hTTWi.Integral()>0 :
                        hTTWi=histo.Clone()
                        hTTWi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                    else : hTTWi.Add(histo.Clone())
                if "Rares" in histo.GetName()  :
                    hRaresi=histo.Clone()
                    hRaresi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                if "EWK" in histo.GetName()  :
                    hEWKi=histo.Clone()
                    hEWKi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                if "ttH_" in histo.GetName() and not "_fake" in histo.GetName():
                    if not hTTHi.Integral()>0 :
                        hTTHi=histo.Clone()
                        hTTHi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                    else : hTTHi.Add(histo.Clone())
                if  histo.GetName() == "tHW_hww" or histo.GetName() == "tHq_hww":
                    #h2.SetName(histo.GetName() + "_hww") ## Xanda: FIXME we do not need that if the card is well done
                    if not hTHi.Integral()>0 :
                        hTHi=histo.Clone()
                        hTHi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                    else : hTHi.Add(histo.Clone())
                if withFolder :
                    #print (histo.GetName(),histo.Integral(), BINtype)
                    fileOut.cd("/"+keyF.GetName()+"/")
                    histo.Write("",TObject.kOverwrite)
                    fileOut.cd()
                    print ("histo.Write("",TObject.kOverwrite) withFolder :: histoName: ",histo.GetName())
                else :
                    histogram.Write("",TObject.kOverwrite)
                    histo.Write("",TObject.kOverwrite)
                    print ("histo.Write("",TObject.kOverwrite) :: histoName: ",histo.GetName())
                    if "fakes_data" in histo.GetName():
                        histoClone1 = histo.Clone(histo.GetName()+"_Norm")
                        histoClone1.Scale(1./histoClone1.Integral())
                        histoCumulative = histoClone1.GetCumulative()
                        histoCumulative.Write("",TObject.kOverwrite)
            print (nameOutFile+" created")
            print ("nkey ", nkey )
            if nkey == 0 :
                if doplots :
                    print ("will make plot ", (isMoreThan02 == 1 or nbins==6), nbins )
                    if isMoreThan02 == 1 or nbins==6 :
                        if BINtype=="none" : namepdf=histSource
                        if BINtype=="regular" : namepdf=histSource+"_"+str(nbins-1)+"bins"
                        if BINtype=="ranged" : namepdf=histSource+"_"+str(nbins-1)+"bins_ranged"
                        if BINtype=="quantiles" :
                            namepdf=histSource+"_"+str(nbins-1)+"bins_quantiles"
                            label=str(nbins-1) + " bins \n" + BINtype + " \n" + bdtType.replace("2lss_output_NN_2lss_ttH_tH_4cat_onlyTHQ_v4_", "")  ## nbins+1 if it starts with 0
                        else : label=str(nbins-1)+" bins \n"+BINtype+" \n"+bdtType.replace("2lss_output_NN_2lss_ttH_tH_4cat_onlyTHQ_v4_", "")
                        doStackPlot(hTTi,hTTHi,hTTWi,hEWKi,hRaresi,hTHi,namepdf,label)
                        print (namepdf+" created")
                #hSumCopy=hSum.Clone()
                hSumCopy=hSumAll.Clone()
                print ("hSumCopy for rebinning:: hSumCopy.Name: ",hSumCopy.GetName())
                hSumi = TH1F()
                if BINtype=="ranged" or BINtype=="regular" : hSumi = TH1F( "hSumRebinned", "hSum" , nbins , xmin , xmax)
                elif BINtype=="quantiles" : hSumi = TH1F( "hSumRebinned", "hSum" , nbins , nbinsQuant)
                elif BINtype=="mTauTauVis" : hSumi = TH1F( "hSumRebinned", "hSum" , nbins , 0. , 200.)
                if not hSumi.GetSumw2N() : hSumi.Sumw2()
                for place in range(1,hSumCopy.GetNbinsX() + 2) :
                    content=hSumCopy.GetBinContent(place)
                    newbin=hSumi.FindBin(hSumCopy.GetBinCenter(place))
                    binErrorCopy = hSumCopy.GetBinError(place);
                    binError = hSumi.GetBinError(newbin);
                    hSumi.SetBinContent(newbin, hSumi.GetBinContent(newbin)+content)
                    hSumi.SetBinError(newbin,sqrt(binError*binError+ binErrorCopy*binErrorCopy))
                hSumi.SetBinErrorOption(1)
                if hSumi.GetBinContent(hSumi.GetNbinsX()) >0 :
                    ratiohSum=hSumi.GetBinError(hSumi.GetNbinsX())/hSumi.GetBinContent(hSumi.GetNbinsX())
                if hSumi.GetBinContent(hSumi.GetNbinsX()-1) >0 : ratiohSumP=hSumi.GetBinError(hSumi.GetNbinsX()-1)/hSumi.GetBinContent(hSumi.GetNbinsX()-1)
                errOcontSUMLast  = errOcontSUMLast+[ratiohSum] if ratiohSum<1.001 else errOcontSUMLast+[1.0]
                errOcontSUMPLast = errOcontSUMPLast+[ratiohSumP] if ratiohSumP<1.001 else errOcontSUMPLast+[1.0]
                errSUMLast       = errSUMLast+[hSumi.GetBinError(hSumi.GetNbinsX())]
                contSUMLast      = contSUMLast+[hSumi.GetBinContent(hSumi.GetNbinsX())]
                if ratiohSum > 0.199 or nbins > nQuantMax :
                    isMoreThan02 = isMoreThan02 + 1
                    if isMoreThan02 == 1 :
                        bin_isMoreThan02 = nbins
                fileOut.cd()
                #hSumCopy.Write()
                #hSumi.Write()
                if BINtype=="quantiles" :
                    print ("nbins: ",nbins)
                    print ("nbinsQuant: ",nbinsQuant)
                    lastQuant = lastQuant+[nbinsQuant[nbins]]   # original
                    xmaxQuant = xmaxQuant+[xmaxdef]
                    xminQuant = xminQuant+[xmindef]
                print ("it should be only one ",  nkey, errOcontTTLast)
    print ("min",xmindef,xmin)
    print ("max",xmaxdef,xmax)
    print ("isMoreThan02", isMoreThan02, bin_isMoreThan02)
    return [errOcontTTLast,errOcontTTPLast,errOcontSUMLast,errOcontSUMPLast,lastQuant,xmaxQuant,xminQuant, bin_isMoreThan02]

global ReadLimits
def ReadLimits(bdtType, nbin, BINtype,channel,local,nstart,ntarget, sendToCondor, toAdd):
    print ("ReadLimits:: bdtType: ",bdtType,", nbin:",nbin,", BINtype: ",BINtype,", channel: ",channel,", local: ",local,", ",nstart,", ntarget: ",ntarget)
    central=[]
    do1=[]
    do2=[]
    up1=[]
    up2=[]
    for nn,nbins in enumerate(nbin) :
        shapeVariable = "%s_%s%s" % (bdtType, str(nbins), nameOutFileAdd)
        #rint ("looking for ", os.path.join(local, "*%s*.log" % (shapeVariable)))
        if channel in [ "0l_2tau"] and sendToCondor :
            datacardFile_output = glob.glob(os.path.join(local, "%s*.out" % (shapeVariable)))[0]
        else :
            datacardFile_output = glob.glob(os.path.join(local, "*%s*.log" % (shapeVariable)))[0]
        if channel == "hh_3l":
            datacardFile_output = os.path.join(local, "hh_3l_%s.log" % shapeVariable)
        if nn==0 : print ("reading ", datacardFile_output)
        f = open(datacardFile_output, 'r+')
        lines = f.readlines() # get all lines as a list (array)
        for line in  lines:
          l = []
          tokens = line.split()
          if "Expected  2.5%"  in line : do2=do2+[float(tokens[4])]
          if "Expected 16.0%:" in line : do1=do1+[float(tokens[4])]
          if "Expected 50.0%:" in line : central=central+[float(tokens[4])]
          if "Expected 84.0%:" in line : up1=up1+[float(tokens[4])]
          if "Expected 97.5%:" in line : up2=up2+[float(tokens[4])]
    return [central,do1,do2,up1,up2]
