import ROOT
import array
import math

def run_cmd(command):
  print "executing command = '%s'" % command
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout

def getCats(dirToLook, fileToLook, fromHavester) :
    catcats = []
    dirlist = fileToLook.GetListOfKeys()
    iter = dirlist.MakeIterator()
    key = iter.Next()
    dirs = {}
    td = ROOT.TDirectoryFile ()
    while key:
        if  key.GetClassName() == 'TDirectoryFile':
            td = key.ReadObj()
            dirName = td.GetName()
            if fromHavester :
                catcats += [dirName]
                key = iter.Next()
                continue
            print "found directory", dirName
            if dirName != dirToLook :
                key = iter.Next()
                continue
            print (key)
            dirs[dirName] = td
            iter2 = td.GetNkeys()
            print("Number of subcategories on the plot: ", iter2)
            for nkey, key2 in enumerate(td.GetListOfKeys()) :
                    #tfileout.get()
                    obj =  key2.ReadObj()
                    obj_name = key2.GetName()
                    print (obj_name)
                    catcats += [obj_name]
        key = iter.Next()
    return catcats


def GetNonZeroBins(template) :
    nbins = 0
    for ii in xrange(1, template.GetXaxis().GetNbins()+1) :
        binContent_original = template.GetBinContent(ii)
        if binContent_original > 0 : nbins += 1
    return nbins

def GetNonZeroPoints(dataTGraph) :
    nbins = 0
    for ii in xrange(1, dataTGraph.GetN()+1) :
        xp = ROOT.Double()
        yp = ROOT.Double()
        dataTGraph.GetPoint(ii, xp, yp)
        if yp > 0 : nbins += 1
    return nbins

def rebin_total(hist, folder, fin, divideByBinWidth, name_total, lastbin, do_bottom, labelX, catbins) :
    total_hist = fin[0].Get(folder + "/" + name_total)
    if not total_hist:
      return total_hist, 0
    hist = total_hist.Clone()
    print(len(fin))
    if len(fin) == 3 :
        for eraa in [1,2] :
            if eraa == 1 : folderRead = folder.replace("2018", "2017")
            if eraa == 2 : folderRead = folder.replace("2018", "2016")
            print ("reading ", eraa, folderRead + "/" + name_total)
            print(folderRead + "/" + name_total)
            total_hist.Add(fin[eraa].Get(folderRead + "/" + name_total))
    print (folder + "/" + name_total)
    allbins = catbins #total_hist.GetNbinsX() #GetNonZeroBins(total_hist)# total_hist.GetXaxis().GetNbins() # GetNonZeroBins(total_hist)
    #hist.Sumw2() ## if prefit
    hist.SetMarkerSize(0)
    hist.SetMarkerColor(16)
    hist.SetFillColorAlpha(12, 0.40)
    hist.SetLineWidth(0)
    hist.SetMinimum(minY)
    hist.SetMaximum(maxY)
    #hist.Sumw2() ## if prefit
    try :
        total_hist.GetBinContent(0)
    except :
        return -100
    for ii in xrange(1, allbins + 1) :
        #print ("total content", total_hist.GetBinContent(ii), total_hist.GetBinError(ii))
        bin_width = 1.
        if divideByBinWidth : bin_width = total_hist.GetXaxis().GetBinWidth(ii)
        hist.SetBinContent(ii + lastbin, 0.03 + total_hist.GetBinContent(ii)/bin_width)
        hist.SetBinError(  ii + lastbin, 0.03 + total_hist.GetBinError(ii)/bin_width)
    if not hist.GetSumw2N() : hist.Sumw2()
    if not do_bottom :
        hist.GetXaxis().SetTitle(labelX)
        hist.GetXaxis().SetTitleOffset(1.2)
        hist.GetXaxis().SetTitleSize(0.05)
        hist.GetXaxis().SetLabelSize(0.05)
        hist.GetXaxis().SetLabelColor(1)
    else :
        hist.GetXaxis().SetLabelColor(10)
        hist.GetXaxis().SetTitleOffset(0.7)
        hist.GetXaxis().SetTickLength(0.04)
        hist.GetYaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleSize(0.055)
    hist.GetYaxis().SetTickLength(0.04)
    hist.GetYaxis().SetLabelSize(0.050)
    return hist, allbins

def rebin_hist(hist_rebin_local, fin, folder, name, itemDict, divideByBinWidth, addlegend, lastbin, catbin, original, firstHisto) :
    print folder+"/"+name
    hist = fin[0].Get(folder+"/"+name)
    allbins = catbin #hist.GetNbinsX() #GetNonZeroBins(hist)
    try  :
        hist.Integral()
    except :
        print ("Doesn't exist " + folder+"/"+name, "in 2018")
        if len(fin) > 1 :
            hist = firstHisto.Clone()
            ## find the histogram in any of the three eras file (it shall be an smarter way to write)
            """hist = fin[1].Get(folder.replace("2018", "2017")+"/"+name)
            try  : hist.Integral()
            except :
                print ("Doesn't exist " + folder.replace("2018", "2017")+"/"+name, "in 2017")
                if len(fin) > 2 :
                    hist = fin[2].Get(folder.replace("2018", "2016")+"/"+name)
                    try  : hist.Integral()
                    except :
                        print ("Doesn't exist " + folder.replace("2018", "2016")+"/"+name, "in 2016")
                        hist = firstHisto.Clone()
                    hist = firstHisto.Clone()"""
        else :
            print ("Doesn't exist " + folder+"/"+name)
            return {
                "lastbin" : allbins,
                "binEdge" : lastbin - 0.5 , # if lastbin > 0 else 0
                "labelPos" : 0 if not original == "none" else float(allbins/2)
                }
    if not firstHisto.Integral() > 0 :
        firstHisto = hist.Clone()
        for ii in xrange(1, firstHisto.GetNbinsX() + 1) :
            firstHisto.SetBinError(  ii, 0.001)
            firstHisto.SetBinContent(ii, 0.001)
    if len(fin) == 3 :
        for eraa in [1,2] :
            if eraa == 1 : folderRead = folder.replace("2018", "2017")
            if eraa == 2 : folderRead = folder.replace("2018", "2016")
            try :
                print ("era" + str(eraa))
                hist.Add(fin[eraa].Get(folderRead+"/"+name))
            except :
                if name == "data_fakes" :
                    try :
                        hist.Add(fin[eraa].Get(folderRead+"/fakes_mc"))
                    except :
                        print ("did not found fakes")
                        continue
                if name == "fakes_mc" :
                    try :
                        hist.Add(fin[eraa].Get(folderRead+"/data_fakes"))
                    except :
                        print ("did not found fakes")
                        continue
                else :
                    continue
    hist_rebin_local.SetMarkerSize(0)
    hist_rebin_local.SetFillColor(itemDict["color"])
    if not itemDict["fillStype"] == 0 :
        hist_rebin_local.SetFillStyle(itemDict["fillStype"])
    #print("signal HH stack inside", key, hist_rebin_local.Integral())
    if "none" not in itemDict["label"] and addlegend :
        legend1.AddEntry(hist_rebin_local, itemDict["label"], "f")
    if itemDict["make border"] == True :  hist_rebin_local.SetLineColor(1)
    else : hist_rebin_local.SetLineColor(itemDict["color"])
    for ii in xrange(1, allbins + 1) :
        bin_width = 1.
        if divideByBinWidth : bin_width = hist.GetXaxis().GetBinWidth(ii)
        ### remove negatives
        binContent_original = hist.GetBinContent(ii)
        binError2_original = hist.GetBinError(ii)**2
        if binContent_original < 0. :
            binContent_modified = 0.
            print ("bin with negative entry: ", ii, '\t', binContent_original)
            binError2_modified = binError2_original + math.pow((binContent_original-binContent_modified),2)
            if not binError2_modified >= 0. : print "Bin error negative!"
            hist_rebin_local.SetBinError(  ii + lastbin, math.sqrt(binError2_modified)/bin_width)
            hist_rebin_local.SetBinContent(ii + lastbin, 0.)
            print 'binerror_original= ', binError2_original, '\t',  'bincontent_original', '\t', binContent_original,'\t', 'bincontent_modified', '\t', binContent_modified, '\t', 'binerror= ', hist_rebin.GetBinError(ii)
        else :
            hist_rebin_local.SetBinError(  ii + lastbin,   hist.GetBinError(ii)/bin_width)
            hist_rebin_local.SetBinContent(ii + lastbin, hist.GetBinContent(ii)/bin_width)
    if not hist.GetSumw2N() : hist.Sumw2()
    return {
        "lastbin" : allbins,
        "binEdge" : hist.GetXaxis().GetBinLowEdge(lastbin) + hist.GetXaxis().GetBinWidth(lastbin) - 0.5 , # if lastbin > 0 else 0
        "labelPos" : float(allbins/2)
        }

def set_histproperty(hist_rebin_local, itemDict, divideByBinWidth, addlegend=True):
  hist_rebin_local.SetMarkerSize(0)
  hist_rebin_local.SetFillColor(itemDict["color"])
  if not itemDict["fillStype"] == 0 :
    hist_rebin_local.SetFillStyle(itemDict["fillStype"])
  if "none" not in itemDict["label"] and addlegend :
        legend1.AddEntry(hist_rebin_local, itemDict["label"], "f")
  if itemDict["make border"] == True :  
    hist_rebin_local.SetLineColor(1)
  else : 
    hist_rebin_local.SetLineColor(itemDict["color"])
  for ii in xrange(1, hist_rebin_local.GetNbinsX() + 1) :
    bin_width = 1.
    if divideByBinWidth : bin_width = hist.GetXaxis().GetBinWidth(ii)
    ### remove negatives                                                                                                                                                                                
    binContent_original = hist.GetBinContent(ii)
    binError2_original = hist.GetBinError(ii)**2
    if binContent_original < 0. :
      binContent_modified = 0.
      print ("bin with negative entry: ", ii, '\t', binContent_original)
      binError2_modified = binError2_original + math.pow((binContent_original-binContent_modified),2)
      if not binError2_modified >= 0. : print "Bin error negative!"
      hist_rebin_local.SetBinError(  ii + lastbin, math.sqrt(binError2_modified)/bin_width)
      hist_rebin_local.SetBinContent(ii + lastbin, 0.)
      print 'binerror_original= ', binError2_original, '\t',  'bincontent_original', '\t', binContent_original,'\t', 'bincontent_modified', '\t', binContent_modified, '\t', 'binerror= ', hist_rebin_local.GetBinError(ii)
    else :
      hist_rebin_local.SetBinError(  ii + lastbin,   hist.GetBinError(ii)/bin_width)
      hist_rebin_local.SetBinContent(ii + lastbin, hist.GetBinContent(ii)/bin_width)
      if not hist.GetSumw2N() : hist.Sumw2()

def rebin_data(template, dataTGraph1, folder, fin, fromHavester, lastbin, histtotal, catbin, unblind) :
    if not fromHavester :

        dataTGraph = fin[0].Get(folder + "/data")
        dataTGraph1 = dataTGraph.Clone()
        print("adding", folder + "/data")
        allbins = catbin #histtotal.GetNbinsX() #GetNonZeroBins(histtotal)
        #if not unblind:
          #allbins -= 2
        if len(fin) == 3 :
            for eraa in [1,2] :
                if eraa == 1 : folderRead = folder.replace("2018", "2017")
                if eraa == 2 : folderRead = folder.replace("2018", "2016")
                dataTGraph2 = fin[eraa].Get(folderRead + "/data")
                print("adding", folderRead + "/data", lastbin)
                #dataTGraph.Merge(dataTGraph2)
                #"""
                for ii in xrange(0, allbins) :
                    xp = ROOT.Double()
                    yp = ROOT.Double()
                    dataTGraph.GetPoint(ii, xp, yp)
                    xp2 = ROOT.Double()
                    yp2 = ROOT.Double()
                    dataTGraph2.GetPoint(ii, xp2, yp2)
                    #print(folderRead, "sum data", ii, xp, yp, yp2, yp + yp2)
                    #dataTGraph.Add(fin[eraa].Get(folderRead + "/data"))
                    dataTGraph.SetPoint(      ii ,  xp , (yp + yp2))
                    dataTGraph.SetPointEYlow( ii ,  math.sqrt(dataTGraph.GetErrorYlow(ii)*dataTGraph.GetErrorYlow(ii) + dataTGraph2.GetErrorYlow(ii)*dataTGraph2.GetErrorYlow(ii)))
                    dataTGraph.SetPointEYhigh(ii ,  math.sqrt(dataTGraph.GetErrorYhigh(ii)*dataTGraph.GetErrorYhigh(ii) + dataTGraph2.GetErrorYhigh(ii)*dataTGraph2.GetErrorYhigh(ii)))
                    dataTGraph.SetPointEXlow( ii ,  template.GetBinWidth(ii+1)/2.)
                    dataTGraph.SetPointEXhigh(ii ,  template.GetBinWidth(ii+1)/2.)
                #"""
                del dataTGraph2
        #del dataTGraph
        for ii in xrange(0, allbins) :
            xp = ROOT.Double()
            yp = ROOT.Double()
            dataTGraph.GetPoint(ii, xp, yp)
            if ii in [allbins-1, allbins-2] and not unblind:
              #dataTGraph1.SetPoint(      ii + lastbin, template.GetBinCenter(ii + lastbin + 1), 0)
              dataTGraph1.SetPoint(      ii + lastbin, 0, 0)
              continue
            bin_width = 1.
            if divideByBinWidth :
                bin_width = histtotal.GetXaxis().GetBinWidth(ii+1)
            #xp = ROOT.Double()
            #yp = ROOT.Double()
            #dataTGraph.GetPoint(ii, xp, yp)
            dataTGraph1.SetPoint(      ii + lastbin,  xp , yp/bin_width)
            dataTGraph1.SetPointEYlow( ii + lastbin,  dataTGraph.GetErrorYlow(ii)/bin_width)
            dataTGraph1.SetPointEYhigh(ii + lastbin,  dataTGraph.GetErrorYhigh(ii)/bin_width)
            dataTGraph1.SetPointEXlow( ii + lastbin,  template.GetBinWidth(ii+1)/2.)
            dataTGraph1.SetPointEXhigh(ii + lastbin,  template.GetBinWidth(ii+1)/2.)
        del dataTGraph
    else :
        dataTGraph = fin[0].Get(folder + "/data_obs")
        print("adding", folder + "/data_obs")
        if len(fin) == 3 :
            for eraa in [1,2] :
                if eraa == 1 : folderRead = folder.replace("2018", "2017")
                if eraa == 2 : folderRead = folder.replace("2018", "2016")
                dataTGraph.Add(fin[eraa].Get(folderRead + "/data_obs"))
        allbins = histtotal.GetNbinsX() #GetNonZeroBins(histtotal)
        for ii in xrange(1, allbins+1) :
            bin_width = 1.
            if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii)
            ## if we would like to blind the last 10 bins
            #if ii > template.GetXaxis().GetNbins()-10 :
            #  dataTGraph1.SetBinContent(ii + lastbin, 0)
            #  dataTGraph1.SetBinError(  ii + lastbin, 0)
            #else :
            #  dataTGraph1.SetBinContent(ii + lastbin, dataTGraph.GetBinContent(ii)/bin_width)
            #  dataTGraph1.SetBinError(  ii + lastbin, dataTGraph.GetBinError(ii)/bin_width)
            dataTGraph1.SetBinContent(ii + lastbin, dataTGraph.GetBinContent(ii)/bin_width)
            dataTGraph1.SetBinError(  ii + lastbin, dataTGraph.GetBinError(ii)/bin_width)
        #del dataTGraph
        dataTGraph.Reset()
    dataTGraph1.SetMarkerColor(1)
    dataTGraph1.SetMarkerStyle(20)
    dataTGraph1.SetMarkerSize(0.8)
    dataTGraph1.SetLineColor(1)
    dataTGraph1.SetLineWidth(1)
    dataTGraph1.SetLineStyle(1)
    dataTGraph1.SetMinimum(minY)
    dataTGraph1.SetMaximum(maxY)
    return dataTGraph1, allbins

def err_data(dataTGraph1, template, dataTGraph, fromHavester, histtotal, folder, fin, unblind) :
    print(" do unblided bottom pad")
    dataTGraph = fin.Get(folder + "/data")
    dataTGraph1 = dataTGraph.Clone()
    if not fromHavester :
        allbins = histtotal.GetXaxis().GetNbins() #GetNonZeroBins(histtotal)
        #if not unblind:
         # allbins -= 2
        print("allbins", allbins)
        for ii in range(0, allbins) :
            if ii in [allbins-1, allbins-2] and not unblind:
              dataTGraph1.SetPoint(ii, 0, 0)
              continue
            #if ii == histtotal.GetXaxis().GetNbins() -1 or ii == histtotal.GetXaxis().GetNbins()-2 :
            #    continue
            bin_width = 1.
            if divideByBinWidth :
                bin_width = histtotal.GetXaxis().GetBinWidth(ii+1)
            if histtotal.GetBinContent(ii+1) == 0 : continue
            dividend = histtotal.GetBinContent(ii+1)*bin_width
            xp = ROOT.Double()
            yp = ROOT.Double()
            dataTGraph.GetPoint(ii,xp,yp)
            if yp > 0 :
                if dividend > 0 :
                    #dataTGraph1.SetPoint(ii + lastbin, template.GetBinCenter(ii + lastbin + 1) , yp/dividend-1)
                  dataTGraph1.SetPoint(ii +lastbin, template.GetBinCenter(ii+1) , yp/dividend-1)
                else :
                    #dataTGraph1.SetPoint(ii + lastbin, template.GetBinCenter(ii + lastbin + 1) , -1.)
                  dataTGraph1.SetPoint(ii + lastbin, template.GetBinCenter(ii+1) , -1.)
            else :
                #dataTGraph1.SetPoint(ii + lastbin, template.GetBinCenter(ii + lastbin +1) , -1.)
              dataTGraph1.SetPoint(ii + lastbin, template.GetBinCenter(ii+1) , -1.)
            dataTGraph1.SetPointEYlow(ii + lastbin,  dataTGraph.GetErrorYlow(ii)/dividend)
            dataTGraph1.SetPointEYhigh(ii + lastbin, dataTGraph.GetErrorYhigh(ii)/dividend)
            dataTGraph1.SetPointEXlow(ii + lastbin,  histtotal.GetBinWidth(ii+1)/2.)
            dataTGraph1.SetPointEXhigh(ii + lastbin, histtotal.GetBinWidth(ii+1)/2.)
            #print ("err", ii + lastbin, template.GetBinCenter(ii + lastbin + 1), dataTGraph.GetErrorYlow(ii)/dividend, dataTGraph.GetErrorYhigh(ii)/dividend)
    else :
        allbins = histtotal.GetNbinsX() #GetNonZeroBins(histtotal)
        for ii in xrange(1, allbins + 1) :
            ## if we would like to blind the last 2 bins
            #if ii == template.GetXaxis().GetNbins() or ii == template.GetXaxis().GetNbins()-1 : continue
            bin_width = 1.
            if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii)
            dividend = template.GetBinContent(ii)*bin_width
            if dataTGraph.GetBinContent(ii) > 0 :
              if dividend > 0 :
                dataTGraph1.SetBinContent(ii , (dataTGraph.GetBinContent(ii)/dividend)-1)
                dataTGraph1.SetBinError(  ii , dataTGraph.GetBinError(ii)/dividend) #
            else :
                dataTGraph1.SetBinContent(ii , -1.)
        if not dataTGraph1.GetSumw2N() : dataTGraph1.Sumw2()
    dataTGraph1.SetMarkerColor(1)
    dataTGraph1.SetMarkerStyle(20)
    dataTGraph1.SetMarkerSize(0.8)
    dataTGraph1.SetLineColor(1)
    dataTGraph1.SetLineWidth(1)
    dataTGraph1.SetLineStyle(1)
    return dataTGraph1,allbins

def do_hist_total_err(hist_total_err, labelX, total_hist, minBottom, maxBottom, era) :
    allbins = total_hist.GetNbinsX() #GetNonZeroBins(total_hist)
    hist_total_err = total_hist.Clone()
    hist_total_err.SetTitle('')
    hist_total_err.GetYaxis().SetTitle("#frac{Data - Expectation}{Expectation}")
    hist_total_err.GetXaxis().SetTitleOffset(1.25)
    hist_total_err.GetYaxis().SetTitleOffset(1.2)
    hist_total_err.GetXaxis().SetTitleSize(0.14)
    hist_total_err.GetYaxis().SetTitleSize(0.075)
    hist_total_err.GetYaxis().SetLabelSize(0.090)
    hist_total_err.GetXaxis().SetLabelSize(0.10)
    hist_total_err.GetYaxis().SetTickLength(0.04)
    hist_total_err.GetXaxis().SetLabelColor(1)
    hist_total_err.GetXaxis().SetTitle(labelX)
    hist_total_err.SetMarkerSize(0)
    hist_total_err.SetFillColorAlpha(12, 0.40)
    hist_total_err.SetLineWidth(0)
    if era == 0 :
        minBottom = minBottom #*3/2
        maxBottom = maxBottom
    hist_total_err.SetMinimum(minBottom)
    hist_total_err.SetMaximum(maxBottom)
    for bin in xrange(0, allbins) :
        hist_total_err.SetBinContent(bin+1, 0)
        if total_hist.GetBinContent(bin+1) > 0. :
          hist_total_err.SetBinError(bin + 1, total_hist.GetBinError(bin+1)/total_hist.GetBinContent(bin+1))
    return hist_total_err, allbins

def addLabel_CMS_preliminary(era) :
    x0 = 0.2
    y0 = 0.953
    ypreliminary = 0.95
    xlumi = 0.67
    label_cms = ROOT.TPaveText(x0, y0, x0 + 0.0950, y0 + 0.0600, "NDC")
    label_cms.AddText("CMS")
    label_cms.SetTextFont(61)
    label_cms.SetTextAlign(13)
    label_cms.SetTextSize(0.0575)
    label_cms.SetTextColor(1)
    label_cms.SetFillStyle(0)
    label_cms.SetBorderSize(0)
    label_preliminary = ROOT.TPaveText(x0 + 0.12, y0 - 0.005, x0 + 0.0980 + 0.12, y0 + 0.0600 - 0.005, "NDC")
    label_preliminary.AddText("Preliminary")
    label_preliminary.SetTextFont(50)
    label_preliminary.SetTextAlign(13)
    label_preliminary.SetTextSize(0.048)
    label_preliminary.SetTextColor(1)
    label_preliminary.SetFillStyle(0)
    label_preliminary.SetBorderSize(0)
    label_luminosity = ROOT.TPaveText(xlumi, y0 + 0.0035, xlumi + 0.0900, y0 + 0.040, "NDC")
    if era == 2016 : lumi = "35.92"
    if era == 2017 : lumi = "41.53"
    if era == 2018 : lumi = "59.74"
    if era == 0    : lumi = "137"
    label_luminosity.AddText(lumi + " fb^{-1} (13 TeV)")
    label_luminosity.SetTextFont(42)
    label_luminosity.SetTextAlign(13)
    label_luminosity.SetTextSize(0.045)
    label_luminosity.SetTextColor(1)
    label_luminosity.SetFillStyle(0)
    label_luminosity.SetBorderSize(0)

    return [label_cms, label_preliminary, label_luminosity]

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

def getQuantiles(histoP,ntarget,xmax) :
    histoP.Scale(1./histoP.Integral())
    histoP.GetCumulative()#.Draw()
    histoP.GetXaxis().SetRangeUser(0.,1.)
    histoP.GetYaxis().SetRangeUser(0.,1.)
    histoP.SetMinimum(0.0)
    xq= array.array('d', [0.] * (ntarget+1))
    yq= array.array('d', [0.] * (ntarget+1))
    yqbin= array.array('d', [0.] * (ntarget+1)) # +2 if firsrt is not zero
    for  ii in range(0,ntarget) : xq[ii]=(float(ii)/(ntarget))
    xq[ntarget]=0.999999999
    histoP.GetQuantiles(ntarget,yq,xq)
    line = [None for point in range(ntarget)]
    line2 = [None for point in range(ntarget)]
    for  ii in range(1,ntarget+1) : yqbin[ii]=yq[ii]
    yqbin[ntarget]=xmax # +1 if first is not 0
    #print yqbin
    return yqbin

def rebinRegular(local, histSource, nbin, BINtype) :
    minmax = finMaxMin(local+"/"+histSource)
    # to know the real min and max of the distribution
    xmindef=minmax[1][0]
    xmaxdef=minmax[1][1]
    if BINtype=="ranged" :
        xmin=minmax[1][0]
        xmax=minmax[1][1]
    else :
        xmin=minmax[0][0]
        xmax=minmax[0][1]
    file = TFile(local+"/"+histSource+".root","READ")
    file.cd()
    histograms=[]
    histograms2=[]
    h2 = TH1F()
    hFakes = TH1F()
    hSumAll = TH1F()
    for nkey, keyO in enumerate(file.GetListOfKeys()) :
       obj =  keyO.ReadObj()
       if type(obj) is not TH1F : continue
       h2 = obj.Clone()
       factor=1.
       if  not h2.GetSumw2N() : h2.Sumw2()
       histograms.append(h2.Clone())
       if keyO.GetName() == "fakes_data" : hFakes=obj.Clone()
       if keyO.GetName() == "fakes_data" or keyO.GetName() =="TTZ" or keyO.GetName() =="TTW" or keyO.GetName() =="TTWW" or keyO.GetName() == "EWK" or keyO.GetName() == "tH" or keyO.GetName() == "Rares" :
           hSumDumb2 = obj
           if not hSumAll.Integral()>0 : hSumAll=hSumDumb2.Clone()
           else : hSumAll.Add(hSumDumb2)
    name=histSource+"_"+str(nbin)+"bins_"+BINtype
    fileOut  = TFile(local+"/"+name+".root", "recreate")
    histo = TH1F()
    for nn, histogram in enumerate(histograms) :
        histogramCopy=histogram.Clone()
        nameHisto=histogramCopy.GetName()
        histogram.SetName(histogramCopy.GetName()+"_"+str(nn)+BINtype)
        histogramCopy.SetName(histogramCopy.GetName()+"Copy_"+str(nn)+BINtype)
        if BINtype=="ranged" or BINtype=="regular" :
            histo= TH1F( nameHisto, nameHisto , nbin , xmin , xmax)
        elif "quantile" in BINtype :
            if "Fakes" in BINtype : nbinsQuant=getQuantiles(hFakes,nbin,xmax)
            if "All" in BINtype : nbinsQuant=getQuantiles(hSumAll ,nbin,xmax)
            histo=TH1F(nameHisto, nameHisto , nbin , nbinsQuant) # nbins+1 if first is zero
        else :
            print "not valid bin type"
            return
        histo.Sumw2()
        for place in range(0,histogramCopy.GetNbinsX() + 1) :
            content =      histogramCopy.GetBinContent(place)
            binErrorCopy = histogramCopy.GetBinError(place)
            newbin =       histo.GetXaxis().FindBin(histogramCopy.GetXaxis().GetBinCenter(place))
            binError =     histo.GetBinError(newbin)
            contentNew =   histo.GetBinContent(newbin)
            histo.SetBinContent(newbin, content+contentNew)
            histo.SetBinError(newbin, sqrt(binError*binError+binErrorCopy*binErrorCopy))
        histo.Write()
    fileOut.Write()
    print (local+"/"+name+".root"+" created")
    print ("calculated between: ",xmin,xmax)
    print ("there is MC data between: ",xmindef,xmaxdef)
    return name

def ReadLimits(limits_output):
    f = open(limits_output, 'r+')
    lines = f.readlines() # get all lines as a list (array)
    for line in  lines:
      l = []
      tokens = line.split()
      if "Expected  2.5%"  in line : do2=float(tokens[4])
      if "Expected 16.0%:" in line : do1=float(tokens[4])
      if "Expected 50.0%:" in line : central=float(tokens[4])
      if "Expected 84.0%:" in line : up1=float(tokens[4])
      if "Expected 97.5%:" in line : up2=float(tokens[4])
    print("read", limits_output, central)
    return [do2,do1,central,up1,up2]


###########################################################
# doYields

def AddSystQuad(list):
    ell = []
    for element in list : ell = ell + [math.pow(element, 2.)]
    quad =  math.sqrt(sum(ell))
    return quad

def PrintTable(cmb, uargs, filey, blinded, labels, type, ColapseCat = []):

    conversions = "Convs"
    flips = 'data_flips'
    fakes_data = 'data_fakes'

    signals = [
        'ttH_hzz',
        'ttH_hww',
        'ttH_htt',
        'ttH_hmm',
        'ttH_hzg'
        ]

    TTWX = [
        'TTW',
        'TTWW'
        ]

    tH = [
    'tHW_htt',
    'tHq_htt',
    'tHW_hww',
    'tHq_hww',
    'tHW_hzz',
    'tHq_hzz',
    #
    'VH_htt',
    'VH_hzz',
    'VH_hww',
    #
    'WH_htt',
    'WH_hzz',
    'WH_hww',
    #
    'ZH_htt',
    'ZH_hzz',
    'ZH_hww',
    #
    'qqH_htt',
    'qqH_hzz',
    'qqH_hww',
    #
    'ggH_htt',
    'ggH_hzz',
    'ggH_hww',
    #
    "TTWH",
    'TTWH_htt',
    'TTWH_hzz',
    'TTWH_hww',
    #
    "TTZH",
    'TTZH_htt',
    'TTZH_hzz',
    'TTZH_hww',
    "HH",
    "HH_tttt", "HH_zzzz", "HH_wwww", "HH_ttzz", "HH_ttww", "HH_zzww"

    ]

    EWK = [
        'ZZ',
        'WZ',
        "ZZ",
        "DY",
        "TT"
    ]

    singleCompMC = [
        'TTZ',
        fakes_data,
        conversions,
        flips,
        "fakes_mc",
        "MC_fakes",
        'Rares',
        "flips_mc",
        "MC_flips",
        "data_obs",
    ]

    sum_proc = []
    err_sum_proc = []
    listTosum = [signals, TTWX, tH, EWK, singleCompMC]
    for label in labels :
        #label = "ttH_4l_2018"
        print (label)
        filey.write("%s\n" % label)
        filey.write("process central error \n")
        for todo in listTosum :
            for ss, signal in enumerate(todo) :
                try :
                    thissig = cmb.cp().bin([label]).cp().process([signal]).GetRate()
                except :
                    continue
                thissigErr = cmb.cp().bin([label]).cp().process([signal]).GetUncertainty(*uargs)
                print (signal, thissig, thissigErr)
                filey.write("%s %s %s\n" % (signal, str(thissig), str(thissigErr)))

def PrintTables(cmb, uargs, filey, blinded, labels, type, ColapseCat = []):

    c_cat = []
    sum_proc = []
    err_sum_proc = []
    for label in labels :
        c_cat = c_cat  + [cmb.cp().bin(['ttH_'+label])]
        sum_proc = sum_proc + [0]
        err_sum_proc = err_sum_proc + [0]

    header = r'\begin{tabular}{|l|'
    bottom = r'Observed data & '
    for ll in xrange(len(labels)) :
        header = header + r'r@{$ \,\,\pm\,\, $}l|'
        if blinded : bottom = bottom + r' \multicolumn{2}{c|}{$-$} '
        else : bottom = bottom + r' \multicolumn{2}{c|}{$%g$} ' % (c_cat[ll].cp().GetObservedRate())
        if ll == len(labels) - 1 : bottom = bottom + r' \\'
        else : bottom = bottom + ' &'
    header = header +"} \n"
    bottom = bottom +"\n"
    filey.write(header)

    if type == 'tau' :
        conversions = "conversions"
        flips = 'flips'
        fakes_data = 'fakes_data'

        filey.write(r"""
        \hline
        Process & \multicolumn{2}{c|}{$1\Plepton + 2\tauh$} & \multicolumn{2}{c|}{$2\Plepton + 2\tauh$} & \multicolumn{2}{c|}{$3\Plepton + 1\tauh$} & \multicolumn{2}{c|}{$2\Plepton ss + 1\tauh$} \\
        \hline
        \hline"""+"\n")

    if type == 'multilep2lss' :
        conversions = "Convs"
        flips = 'data_flips'
        fakes_data = 'data_fakes'

        filey.write(r"""
        \hline
        Process & \multicolumn{20}{c|}{$2\Plepton ss$}  \\ \hline
        B-tag  & \multicolumn{4}{c|}{no req.}  & \multicolumn{8}{c|}{Loose}  & \multicolumn{8}{c|}{Tight}   \\ \hline
        Leptons  & \multicolumn{4}{c|}{$ee$} & \multicolumn{4}{c|}{$em$} & \multicolumn{4}{c|}{$mm$} & \multicolumn{4}{c|}{$em$} & \multicolumn{4}{c|}{$mm$}  \\ \hline
        Signal & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} \\ \hline
        \hline
        \hline"""+"\n")

    if type == 'multilepCR2lss' :
        conversions = "Convs"
        flips = 'flips_data'
        fakes_data = 'data_fakes'

        filey.write(r"""
        \hline
        Process & \multicolumn{20}{c|}{$2\Plepton ss$}  \\ \hline
        B-tag   & \multicolumn{4}{c|}{no req.} & \multicolumn{8}{c|}{Loose}  & \multicolumn{8}{c|}{Tight}  \\ \hline
        Leptons  & \multicolumn{4}{c|}{$ee$} & \multicolumn{4}{c|}{$em$}  & \multicolumn{4}{c|}{$mm$} & \multicolumn{4}{c|}{$em$}  & \multicolumn{4}{c|}{$mm$} \\ \hline
        Signal & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} \\ \hline
        \hline
        \hline"""+"\n")

    if type == 'multilepCR3l4l' :
        conversions = "Convs"
        flips = 'flips_data'
        fakes_data = 'data_fakes'

        filey.write(r"""
        \hline
        Process & \multicolumn{10}{c|}{$3\Plepton$} & \multicolumn{2}{c|}{$4\Plepton$}  \\ \hline
        CR & \multicolumn{8}{c|}{$\PcZ$-peak} & \multicolumn{2}{c|}{$WZ$ enrich.}  & \multicolumn{2}{c|}{$ZZ$ enrich.} \\ \hline
        B-tag  & \multicolumn{4}{c|}{Loose}  & \multicolumn{4}{c|}{Tight}  & \multicolumn{4}{c|}{no req.}   \\ \hline
        Signal & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & & \multicolumn{4}{c|}{no req.} \\ \hline
        \hline
        \hline"""+"\n")

    if type == 'multilep3l4l' :
        conversions = "Convs"
        flips = 'flips_data'
        fakes_data = 'data_fakes'

        filey.write(r"""
        \hline
        Process &  \multicolumn{8}{c|}{$3\Plepton$} & \multicolumn{2}{c|}{$4\Plepton + 1\tauh$}  \\ \hline
        B-tag  & \multicolumn{4}{c|}{no req.}  & \multicolumn{8}{c|}{Loose}  & \multicolumn{8}{c|}{Tight}  & \multicolumn{4}{c|}{Loose}  & \multicolumn{4}{c|}{Tight} & \multicolumn{2}{c|}{no req.}  \\ \hline
        Signal & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} & \multicolumn{2}{c|}{$-$} & \multicolumn{2}{c|}{$+$} \\ \hline
        \hline
        \hline"""+"\n")

    signals = [
        'ttH_hzz',
        'ttH_hww',
        'ttH_htt',
        'ttH_hmm',
        'ttH_hzg'
        ]

    TTWX = [
        'TTW',
        'TTWW'
        ]

    if 'multilep' in type :
        tH = [
        'tHW_htt',
        'tHq_htt',
        'tHW_hww',
        'tHq_hww',
        'tHW_hzz',
        'tHq_hzz'
        ]
        signalslabel_tH = [
            r'$\cPqt\PHiggs q$ $\PHiggs \to \Pgt\Pgt$& ',
            r'$\cPqt\PHiggs\PW$ $\PHiggs \to \Pgt\Pgt$& ',
            r'$\cPqt\PHiggs q$ $\PHiggs \to \PW\PW$ & ',
            r'$\cPqt\PHiggs\PW$ $\PHiggs \to \PW\PW$ & ',
            r'$\cPqt\PHiggs q$ $\PHiggs \to \cPZ\cPZ$  & ',
            r'$\cPqt\PHiggs\PW$ $\PHiggs \to \cPZ\cPZ$  & '
            ]

    if type == 'tau' :
        tH = [
        'tHq',
        'tHW'
        ]
        signalslabel_tH = [
            r'$\cPqt\PHiggs q$ & ',
            r'$\cPqt\PHiggs\PW$ & '
            ]

    EWK = [
        'ZZ',
        'WZ'
    ]

    singleCompMC = []
    if type == 'tau' : singleCompMC = singleCompMC + ['EWK']
    singleCompMC = singleCompMC + [
        'TTZ',
        fakes_data,
        conversions,
        flips,
        'Rares'
    ]

    singleCompMClabels = []
    if type == 'tau' : singleCompMClabels = singleCompMClabels + ['$\PW\cPZ + \cPZ\cPZ$']
    singleCompMClabels = singleCompMClabels + [
        '$\cPqt\cPaqt\cPZ$',
        'Misidentified',
        'Conversions',
        'signal flip',
        'Other'
    ]

    if type == 'tau' : listTosum = [signals, TTWX, tH]
    if 'multilep' in type : listTosum = [signals, TTWX, tH, EWK]
    for todo in listTosum :

        sigsum = [0.0 for i in xrange(len(labels))]
        sigsumErr = [0.0 for i in xrange(len(labels))]

        if todo == signals :
            linesigsum = 'ttH (sum) &'
            signalslabel = [
                r'$\cPqt\cPaqt\PHiggs$, $\PHiggs \to \cPZ\cPZ$ & ',
                r'$\cPqt\cPaqt\PHiggs$, $\PHiggs \to \PW\PW$ & ',
                r'$\cPqt\cPaqt\PHiggs$, $\PHiggs \to \Pgt\Pgt$ & ',
                r'$\cPqt\cPaqt\PHiggs$, $\PHiggs \to \mu\mu$ & ',
                r'$\cPqt\cPaqt\PHiggs$, $\PHiggs \to \cPZ\gamma$& ',
                ]
        elif todo == TTWX :
            linesigsum = 'ttW + ttWW &'
            signalslabel = [
                r'$\cPqt\cPaqt\PW$ & ',
                r'$\cPqt\cPaqt\PW\PW$ & '
                ]
        elif todo == tH :
            linesigsum = '$\cPqt\PHiggs$ (sum) &'
            signalslabel = signalslabel_tH
        if todo == EWK :
            linesigsum = '$\PW\cPZ + \cPZ\cPZ$ &'
            signalslabel = [
                r'$\cPZ\cPZ$ & ',
                r'$\PW\cPZ$ & '
                ]

        for ss, signal in enumerate(todo) :
            linesig = signalslabel[ss]
            for ll, label in enumerate(labels) :
                if "2lss_1tau" in label or  "3l_1tau" in label :
                    thissig = c_cat[ll].cp().process([signal+'_faketau']).GetRate() + c_cat[ll].cp().process([signal+'_gentau']).GetRate()
                    thissigErr = AddSystQuad({c_cat[ll].cp().process([signal+'_faketau']).GetUncertainty(*uargs), c_cat[ll].cp().process([signal+'_gentau']).GetUncertainty(*uargs)})
                else :
                    thissig = c_cat[ll].cp().process([signal]).GetRate()
                    thissigErr = c_cat[ll].cp().process([signal]).GetUncertainty(*uargs)
                if not thissig + thissigErr < 0.05:
                    linesig = linesig + ' $%.2f$ & $%.2f$ ' % (thissig, thissigErr)
                else : linesig = linesig + r' \multicolumn{2}{c|}{$< 0.05$} '
                if ll == len(labels) - 1 : linesig = linesig + r' \\'
                else : linesig = linesig + ' &'
                sigsum[ll] = sigsum[ll] + thissig
                sigsumErr[ll] = AddSystQuad({sigsumErr[ll], thissigErr})
                sum_proc[ll] = sum_proc[ll] + thissig
                err_sum_proc[ll] = AddSystQuad({err_sum_proc[ll], thissigErr})
            filey.write(linesig+"\n")
        filey.write(r'\hline'+"\n")

        for ll, label in enumerate(labels) :
            if not sigsum[ll] +  sigsumErr[ll] < 0.05:
                linesigsum = linesigsum + ' $%.2f$ & $%.2f$ ' % (sigsum[ll], sigsumErr[ll])
            else :  linesigsum = linesigsum + r' \multicolumn{2}{c|}{$< 0.05$} '
            if ll == len(labels) - 1 : linesigsum = linesigsum + r' \\'
            else : linesigsum = linesigsum + ' &'
        filey.write(linesigsum+"\n")
        filey.write(r'\hline'+"\n")

    for ss, signal in enumerate(singleCompMC) :
        lineTTZ = singleCompMClabels[ss]+' & '
        for ll, label in enumerate(labels) :
            if ("2lss_1tau" in label or  "3l_1tau" in label ) and signal not in ['fakes_data', 'flips']:
                thissig = c_cat[ll].cp().process([signal+'_faketau']).GetRate() + c_cat[ll].cp().process([signal+'_gentau']).GetRate()
                thissigErr = AddSystQuad({c_cat[ll].cp().process([signal+'_faketau']).GetUncertainty(*uargs), c_cat[ll].cp().process([signal+'_gentau']).GetUncertainty(*uargs)})
            else :
                thissig = c_cat[ll].cp().process([signal]).GetRate()
                thissigErr = c_cat[ll].cp().process([signal]).GetUncertainty(*uargs)
            if not thissig + thissigErr < 0.05:
                lineTTZ = lineTTZ + ' $%.2f$ & $%.2f$ ' % (thissig, thissigErr)
            else : lineTTZ = lineTTZ + r' \multicolumn{2}{c|}{$< 0.05$} '
            sum_proc[ll] = sum_proc[ll] + thissig
            err_sum_proc[ll] = AddSystQuad({err_sum_proc[ll], thissigErr})
            if ll == len(labels) - 1 : lineTTZ = lineTTZ + r' \\ '+"\n"
            else : lineTTZ = lineTTZ + ' &'
        filey.write(lineTTZ+"\n")

    lineSUM = r'\hline\hline'+"\n"+' SM expectation & '
    for ll, label in enumerate(labels) :
        if not sum_proc[ll] + err_sum_proc[ll] < 0.05:
            lineSUM = lineSUM + ' $%.2f$ & $%.2f$ ' % (sum_proc[ll] , err_sum_proc[ll] )
        else : lineSUM = lineSUM + r' \multicolumn{2}{c|}{$< 0.05$} '
        if ll == len(labels) - 1 : lineSUM = lineSUM + r' \\ '+"\n"
        else : lineSUM = lineSUM + ' &'
    filey.write(lineSUM+"\n")

    filey.write(r'\hline'+"\n")
    filey.write(bottom)
    filey.write(r"""\hline
    \end{tabular}"""+"\n")
