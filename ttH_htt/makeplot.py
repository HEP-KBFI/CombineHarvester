import argparse
import ROOT as r
import collections
import ROOT
import math
import os
import collections

parser = argparse.ArgumentParser()
parser.add_argument("--input_path", type=str, dest="input_path", help="path of datacard text file")
parser.add_argument("--fitdir", dest="fitdir", help="which directory prefit or postfit", nargs='+',default=['shapes_prefit', 'shapes_fit_s'], choices=['shapes_prefit', 'shapes_fit_s'])
parser.add_argument("--unblind", dest="unblind", help="unblinding", action='store_true', default=True)
parser.add_argument("--mass", dest="mass", help="which mass point to be considered", nargs='+', default='800')

options = parser.parse_args()
input_path = options.input_path
fitdir = options.fitdir
unblind = options.unblind
mass = options.mass

output_path = input_path[:input_path.rfind('/')]
fittype = 'all' if 'all' in input_path else 'bkg'
era = '2016' if '2016' in input_path else '2017' if '2017' in input_path else '2018'
yield_file = output_path + '/event_yield_%s_1.txt' %fittype

dprocs = collections.OrderedDict()
dprocs["data_fakes"]   = {"color" :  1, "fillStype" : 3345, "label" : "Fakes"  ,    "make border" : True}
dprocs["Fakes"]   = {"color" :  1, "fillStype" : 3345, "label" : "Fakes"  ,    "make border" : True}
dprocs["Convs"]      = {"color" :   800, "fillStype" : 1001, "label" : "Conversions", "make border" :  True}
dprocs["TT"]         = {"color" : 822, "fillStype" : 1001, "label" : 't#bar{t} + jets'   , "make border" : True}
dprocs["ST"]         = {"color" : 823, "fillStype" : 1001, "label" : 'ST'   , "make border" : True}
dprocs["Other"]      = {"color" : 851, "fillStype" : 1001, "label" : "Other_bbWW"       , "make border":True}
dprocs["Other_bbWW"]      = {"color" : 851, "fillStype" : 1001, "label" : "Other_bbWW"       , "make border":True}
dprocs["W"]          = {"color" : 634, "fillStype" : 1001, "label" : "WJets"         , "make border" :True}
dprocs["WJets"]          = {"color" : 634, "fillStype" : 1001, "label" : "WJets"         , "make border" :True}
dprocs["VV"]         = {"color" : 16,   "fillStype" : 1001, "label" : "VV+VVV"          , "make border" : True}
dprocs["VVV"]        = {"color" : 822, "fillStype" : 1001, "label" : "VVV"          , "make border" : True}
dprocs["ttW"]        = {"color" : 823, "fillStype" : 1001, "label" : "none"        , "make border" : False}
dprocs["TTWW"]       = {"color" : 823, "fillStype" : 1001, "label" : "t#bar{t}(W)"  , "make border" : True}
dprocs["DY"]         = {"color" : 610, "fillStype" : 1001, "label" : "DY"         , "make border" : True}
dprocs["SH"]         = {"color" : 628, "fillStype" : 1001, "label" : "Single H"         , "make border" : False}

higgs_procs_w_BR = []
higgs_proc_no_BR = ["ttH", "tHq","tHW", "WH","ZH","qqH", "ggH"]
for proc in higgs_proc_no_BR:
  higgs_procs_w_BR.append(proc+"_hww")
  higgs_procs_w_BR.append(proc+"_hzz")
  higgs_procs_w_BR.append(proc+"_htt")
  higgs_procs_w_BR.append(proc+"_hbb")
  higgs_procs_w_BR.append(proc+"_hgg")

def create_legend():
  legend_y0 = 0.75
  legendPosX = 0.570
  legendPosY = 0.510
  legendSizeX = 0.360
  legendSizeY = 0.420
  legend1 = ROOT.TLegend(0.1800, legend_y0, 0.90, 0.94)
  legend1.SetNColumns(3)
  legend1.SetFillStyle(0)
  legend1.SetBorderSize(0)
  legend1.SetFillColor(10)
  legend1.SetTextSize(0.030)
  return legend1

def create_canvas():
  canvas = ROOT.TCanvas("canvas", "canvas", 800, 900);
  canvas.SetFillColor(10);
  canvas.SetFillStyle(4000)
  canvas.SetTicky()
  canvas.SetBorderSize(2);
  canvas.SetLeftMargin(0.12);
  canvas.SetBottomMargin(0.12)
  return canvas

def create_Pad(y1=0, y2=1, topmargin=0.055, leftmargin=0.12, bottommargin=0.03, rightmargin=0.12, logy=True):
  topPad = ROOT.TPad("topPad", "topPad", 0.00, y1, 1.00, y2);
  topPad.SetFillColor(10);
  topPad.SetTopMargin(topmargin)
  topPad.SetLeftMargin(leftmargin)
  topPad.SetBottomMargin(bottommargin)
  topPad.SetRightMargin(rightmargin)
  topPad.SetLogy(logy)
  return topPad

def set_axis(axis, title='', titleoffset=1.25, labelsize=10, labeloffset=1000, labelcolor=10, titlecolor=10):
   axis.SetTitle(title)
   axis.SetTitleOffset(titleoffset)
   axis.SetLabelSize(labelsize)
   axis.SetLabelOffset(labeloffset)
   axis.SetLabelColor(labelcolor)
   axis.SetTitleColor(titlecolor)

def addLabel_CMS_preliminary(era) :
    x0 = 0.2
    y0 = 0.97
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
    if era == '2016' : lumi = "35.92"
    if era == '2017' : lumi = "41.53"
    if era == '2018' : lumi = "59.74"
    if era == '0'    : lumi = "137"
    label_luminosity.AddText(lumi + " fb^{-1} (13 TeV)")
    label_luminosity.SetTextFont(42)
    label_luminosity.SetTextAlign(13)
    label_luminosity.SetTextSize(0.045)
    label_luminosity.SetTextColor(1)
    label_luminosity.SetFillStyle(0)
    label_luminosity.SetBorderSize(0)

    return [label_cms, label_preliminary, label_luminosity]
yield_line = []

def createFile(fileName, lines, nofNewLines = 2):
    """Auxiliary function to write new config file,
       containg the lines given as argument. 
    """
    content = "\n".join(lines)
    content += nofNewLines * "\n"
    with open(fileName, "w") as f:
      f.write(content)

def print_yield(eyield):
  for k in eyield.keys():
    yield_line.append('%s\n' %k)
    if type(eyield[k][eyield[k].keys()[0]]) == collections.OrderedDict:
      newdict = eyield[k]
      print_yield(newdict)
    else:
      maxlen = max(map(lambda x:len(x), eyield[k].keys()))
      for kk, vv in eyield[k].items():
        yield_line.append('{:>{len}} {:0.5}'.format(kk,vv, len=maxlen))
    yield_line.append('\n')
  createFile(yield_file, yield_line)

def print_inclusiveyield(eyield):
  y_sorted = list(sorted([(kk, vv) for kk, vv in eyield.items()], key = lambda kv: kv[1], reverse = True))
  maxlen = max(map(lambda x:len(x), eyield.keys()))
  for kk, vv in y_sorted:
    yield_line.append('{:>{len}} {:0.5} +- {:0.3}'.format(kk,vv[0],math.sqrt(vv[1]), len=maxlen))
  createFile(yield_file, yield_line)

def set_histproperty(hist_rebin_local, itemDict, addlegend=True):
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

f = r.TFile.Open(input_path)
eyield = collections.OrderedDict()
inclu_eyield = collections.OrderedDict()
for d in fitdir:
 dir_ = f.Get(d)
 plotdir = output_path + '/%s/' %d
 if not os.path.exists(plotdir):
   os.makedirs(plotdir)
 eyield[d] = collections.OrderedDict()
 for evtcat in [cat.GetName() for cat in dir_.GetListOfKeys()]:
   eyield[d][evtcat] = collections.OrderedDict()
   print '**************', evtcat
   sd = dir_.Get(evtcat)
   if type(sd) != ROOT.TDirectoryFile: continue
   legend1 = create_legend()
   found_SH = False
   found_ttv = False
   found_VV = False
   signal_hists = []
   hists = []
   samples = [s.GetName() for s in sd.GetListOfKeys() if not 'total_cov' in s]#s.GetName().endswith(('_fake', '_Convs', 'fakes_mc'))]# and 'signal' not in s.GetName() ]
   for sample in samples:
     print '**************', sample
     if 'data' in sample:
       data_hist = sd.Get(sample)
       continue
     if 'signal' in sample and 'total' not in sample:
         signal_hists.append(sd.Get(sample))
         continue     
     if 'total' in sample:
       if 'total_background' in sample:
         total_hist = sd.Get(sample)
         continue
       else: continue
     hist = sd.Get(sample)
     #if rebin: hist.Rebin(10)
     if sample in ['TTH', 'ttH', 'tHq', 'tHW', 'ggH', 'qqH', 'TTWH', 'TTZH', 'ZH', 'WH'] + higgs_procs_w_BR:
       if not found_SH:
         set_histproperty(hist, dprocs['SH'], True)
         SH = hist
         SH.SetName('SingleHiggs')
         SH.Sumw2()
         found_SH = True
       else:
         set_histproperty(hist, dprocs['SH'], False)
         SH.Add(hist)
     elif sample in ['TTZ', 'TTW', 'TTWW']:
       if not found_ttv:
         set_histproperty(hist, dprocs['TTWW'], True)
         ttv = hist
         ttv.Sumw2()
         found_ttv = True
       else:
         set_histproperty(hist, dprocs['TTWW'], False)
         ttv.Add(hist)
     elif sample in ['VV', 'VVV']:
       if not found_VV:
         set_histproperty(hist, dprocs['VV'], True)
         VV = hist
         VV.Sumw2()
         found_VV = True
       else:
         set_histproperty(hist, dprocs['VV'], False)
         VV.Add(hist)
     else:
       print '**************',
       set_histproperty(hist, dprocs[sample], True)
       hists.append(hist)
   hists.append(SH)
   if found_ttv: hists.append(ttv)
   if found_VV: hists.append(VV)
   hists = sorted(hists, key=lambda x: x.Integral())

   histogramStack_mc = ROOT.THStack()
   print '**************creating stack',
   totalhist = False
   for hist in hists:
     histogramStack_mc.Add(hist)
     if hist.GetName() not in eyield[d][evtcat]:
       error = r.Double()
       eyield[d][evtcat][hist.GetName()] = (hist.IntegralAndError(0,-1,error), error)
     else:
      print 'same hist found twice'
      sys.exit()
     tot_err = r.Double()
     if hist.GetName() not in inclu_eyield.keys():
       inclu_eyield[hist.GetName()] = (hist.IntegralAndError(0,-1,tot_err), tot_err**2)
     else:
       inclu_eyield[hist.GetName()] = (inclu_eyield[hist.GetName()][0]+hist.Integral(), inclu_eyield[hist.GetName()][1]+tot_err**2)

   canvas = create_canvas()
   topPad =    create_Pad(y1=0.35, y2=1.0, topmargin=0.055, leftmargin=0.12, bottommargin=0.03, rightmargin=0.12, logy=True)
   bottomPad = create_Pad(y1=0.0,  y2=0.35,topmargin=0.02,  leftmargin=0.12, bottommargin=0.31, rightmargin=0.12, logy=False)
   canvas.cd()
   topPad.Draw()
   topPad.cd()

   xAxis_top = total_hist.GetXaxis();
   set_axis(xAxis_top, title='DNN Score in %s' %evtcat, titleoffset=1.25, labelsize=10, labeloffset=1000, labelcolor=10, titlecolor=10)
   yAxis_top = total_hist.GetYaxis()
   #set_axis(xAxis_top, title='DNN Score in %s' %evtcat, titleoffset=0.70, labelsize=0.05, labeloffset=1000)
   yAxis_top.SetTitle("dN/d DNN Score")
   yAxis_top.SetTitleOffset(0.70)
   yAxis_top.SetTitleSize(0.06)
   yAxis_top.SetLabelSize(0.05)
   yAxis_top.SetTickLength(0.04)
   
   max_ = 100*total_hist.GetMaximum()
   total_hist.GetYaxis().SetRangeUser(0.1, max_)
   total_hist.SetStats(False)
   total_hist.SetTitle('')
   total_hist.SetMarkerColor(16)#0)
   #total_hist.SetMarkerStyle(20)
   total_hist.SetMarkerSize(0)
   total_hist.SetLineWidth(0)
   total_hist.SetFillColorAlpha(12, 0.40)
   total_hist.Draw("e2,same")
   legend1.AddEntry(total_hist, "Uncertainty", "f")
   
   histogramStack_mc.Draw("hist same")
   total_hist.Draw("e2,same")
   data_hist.SetMarkerSize(2);
   data_hist.SetMarkerColor(r.kBlack);
   data_hist.SetLineColor(r.kBlack);
   data_hist.SetMarkerStyle(20);
   
   if unblind: data_hist.Draw("e1P same")
   legend1.Draw("same")

   colorsH = [1, 4, 8, 5, 6]
   for i, signal_hist in enumerate(signal_hists):
     signal_hist.SetMarkerSize(0)
     signal_hist.SetLineWidth(3)
     signal_hist.SetLineColor(colorsH[i])
     signal_hist.Draw("hist same")
     legend1.AddEntry(signal_hist, signal_hist.GetName().replace('signal_', '').replace('ggf_', '').replace('spin0_', ''), "f")

   labels = addLabel_CMS_preliminary(era)
   for ll, label in enumerate(labels) :
    if ll == 0 :
        label.Draw("same")
    else :
        label.Draw()

   canvas.cd()
   bottomPad.Draw()
   bottomPad.cd()
   bottomPad.SetLogy(0)
  
   err_hist = total_hist.Clone("err")

   for ibin in range(1, err_hist.GetNbinsX()+1):
     err_hist.SetBinContent(ibin,0)
     if total_hist.GetBinContent(ibin) > 0.:
      binerr = total_hist.GetBinError(ibin)/total_hist.GetBinContent(ibin)
      err_hist.SetBinError(ibin, binerr)

   err_hist.SetMinimum(-0.8)
   err_hist.SetMaximum(0.8)
   xAxis_bottom = err_hist.GetXaxis();
   xAxis_bottom.SetTitle(xAxis_top.GetTitle());
   xAxis_bottom.SetLabelColor(1);
   xAxis_bottom.SetTitleColor(1);
   xAxis_bottom.SetTitleOffset(1.20);
   xAxis_bottom.SetTitleSize(0.12);
   xAxis_bottom.SetLabelOffset(0.02);
   xAxis_bottom.SetLabelSize(0.10);
   xAxis_bottom.SetTickLength(0.055);

   yAxis_bottom = err_hist.GetYaxis();
   yAxis_bottom.SetTitle("#frac{Data - Simulation}{Simulation}");
   yAxis_bottom.SetTitleOffset(0.60);
   yAxis_bottom.SetLabelSize(0.06)
   yAxis_bottom.SetNdivisions(505);
   yAxis_bottom.CenterTitle();
   yAxis_bottom.SetTitleSize(0.09);

   err_hist.Draw("e2, same")
   line = r.TF1("line","0", xAxis_bottom.GetXmin(), xAxis_bottom.GetXmax());
   line.SetLineStyle(3);
   line.SetLineColor(r.kBlack);
   line.Draw("same");

   histogramRatio = data_hist.Clone("histogramRatio");
   for ibin in range(0, total_hist.GetNbinsX()):
     x = r.Double()
     y = r.Double()
     histogramRatio.GetPoint(ibin, x, y)
     bincontent = total_hist.GetBinContent(ibin+1)
     if bincontent == 0: continue
     if bincontent >0:
       histogramRatio.SetPoint(ibin, total_hist.GetBinCenter(ibin+1), y/bincontent -1)
     else:
       histogramRatio.SetPoint(ibin, total_hist.GetBinCenter(ibin+1), -1)
     histogramRatio.SetPointEYlow(ibin,  data_hist.GetErrorYlow(ibin)/total_hist.GetBinContent(ibin+1))
     histogramRatio.SetPointEYhigh(ibin, data_hist.GetErrorYhigh(ibin)/total_hist.GetBinContent(ibin+1))
     histogramRatio.SetPointEXlow(ibin,  total_hist.GetBinWidth(ibin+1)/2.)
     histogramRatio.SetPointEXhigh(ibin, total_hist.GetBinWidth(ibin+1)/2.)

   histogramRatio.SetMarkerStyle(data_hist.GetMarkerStyle());
   histogramRatio.SetMarkerSize(data_hist.GetMarkerSize());
   histogramRatio.SetMarkerColor(data_hist.GetMarkerColor());
   histogramRatio.SetLineColor(data_hist.GetLineColor());

   histogramRatio.Draw("e1psame")
   plot = '%s/%s_%s_%s.pdf' %(plotdir, evtcat, mass, fittype)
   canvas.SaveAs(plot)
   del canvas
   del histogramStack_mc
   #print eyield
#print_yield(eyield)
print_inclusiveyield(inclu_eyield)
