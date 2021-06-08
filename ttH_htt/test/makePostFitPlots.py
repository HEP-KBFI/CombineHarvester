#!/usr/bin/env python
import os, subprocess, sys
import os, sys, time,math
import ROOT
from optparse import OptionParser
from collections import OrderedDict
execfile("../python/data_manager.py")
ROOT.gStyle.SetOptStat(0)
#ROOT.gStyle.SetErrorX(0)
ROOT.gStyle.SetEndErrorSize(0)
from optparse import OptionParser
parser = OptionParser()
parser.add_option(
    "--input", type="string", dest="input",
    help="A valid file with the shapes as output of combine FitDiagnostics",
    default="/afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/posfit_3poi_ttVFromZero/ttH_fitDiagnostics.Test_shapes.root"
    )
parser.add_option(
    "--odir", type="string", dest="odir",
    help="Directory for the output plots",
    default="/afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/PostFitHavester_comb_2017v2_withCR_sanity/"
    )
parser.add_option(
    "--original", type="string", dest="original",
    help="The original datacard: used only to rebin",
    default="none"
    )
parser.add_option(
    "--channel", type="string", dest="channel",
    help="Name of the category as it is appear on the input file",
    default="ttH_1l_2tau_OS"
    )
parser.add_option(
    "--labelX", type="string", dest="labelX",
    help="To appear on final plot",
    default="BDT"
    )
parser.add_option(
    "--useLogPlot", action="store_true", dest="useLogPlot",
    help="Self explanatory",
    default=False
    )
parser.add_option(
    "--notFlips", action="store_true", dest="notFlips",
    help="Self explanatory",
    default=False
    )
parser.add_option(
    "--notConversions", action="store_true", dest="notConversions",
    help="Self explanatory",
    default=False
    )
parser.add_option(
    "--MC_IsSplit", action="store_true", dest="MC_IsSplit",
    help="If the MC components on card are separated as 'gentau' and 'faketau' ",
    default=False
    )
parser.add_option(
    "--divideByBinWidth", action="store_true", dest="divideByBinWidth",
    help="If final plot shall be done dividing bin content by bin width ",
    default=False
    )
parser.add_option(
    "--doMultilepCatPlot", action="store_true", dest="doMultilepCatPlot",
    help="Do subcategories from multilepton cards ",
    default=False
    )
parser.add_option(
    "--unblind", action="store_true", dest="unblind",
    help="Do subcategories from multilepton cards ",
    default=False
    )
parser.add_option(
    "--doPostFit", action="store_true", dest="doPostFit",
    help="Do the postfit instead of prefit ",
    default=False
    )
parser.add_option(
    "--minY", type="float", dest="minY",
    help="For the final plot",
    default=0.
    )
parser.add_option(
    "--maxY", type="float", dest="maxY",
    help="For the final plot",
    default=1.
    )
parser.add_option(
    "--fromHavester", action="store_true", dest="fromHavester",
    help="The input file is from CombineHavester. In this case you do not need to enter 'original' if you called the PostFitShapesFromWorkspace with the -d option",
    default=False
    )
(options, args) = parser.parse_args()

divideByBinWidth = options.divideByBinWidth
category = options.channel
print ("category", category)
#setTDRStyle()

labelY = "Events"
if divideByBinWidth : labelY = "Events / bin width"

if options.doPostFit :
    if not options.fromHavester and not options.doMultilepCatPlot :
        folder = "shapes_fit_s/"+category
        folder_data = "shapes_fit_s/"+category # it is a TGraphAsymmErrors, not histogram
        typeFit = "postfit"
    elif options.doMultilepCatPlot :
        folder = "shapes_fit_s/"
        folder_data = "shapes_fit_s/" # it is a TGraphAsymmErrors, not histogram
        typeFit = "postfit"
    else :
        folder = category+"_postfit"
        folder_data = category+"_postfit" # it is a histogram
        typeFit = "postfit"
else :
    if not options.fromHavester and not options.doMultilepCatPlot :
        folder = "shapes_prefit/"+category
        folder_data = "shapes_prefit/"+category # it is a TGraphAsymmErrors, not histogram
        typeFit = "prefit"
    elif options.doMultilepCatPlot :
        folder = "shapes_prefit/"
        folder_data = "shapes_prefit/" # it is a TGraphAsymmErrors, not histogram
        typeFit = "prefit"
    else :
        folder = category+"_prefit"
        folder_data = category+"_prefit" # it is a histogram
        typeFit = "prefit"
print ("folder", folder)
if not options.fromHavester : name_total = "total"
else : name_total = "TotalProcs"

if "0tau" in category or "4l" in category or "cr" in category :
    conversions = "Convs"
    fakes       = "data_fakes"
    flips       = "data_flips"
else :
    conversions = "conversions"
    fakes       = "fakes_data"
    flips       = "flips_data"

dprocs = OrderedDict()
if not options.MC_IsSplit :
    # if label == "none" it means that this process is to be merged with the anterior key
    #                      color, fillStype, label,       , make border
    if not "4l" in category :
        dprocs[fakes]        = [12,     3345,      "Non-prompt",        True]
        dprocs[flips]        = [1,     3006,      "Charge mis-m",       True]
    dprocs[conversions]  = [5,     1001,      "Conv.", True]
    dprocs["Rares"]      = [851,   1001,      "Rares",       True]
    if "3l_0tau" in category or "4l" in category or "crwz" in category :
        if not "4l" in category : dprocs["WZ"]        = [610,   1001,      "none",         True]
        dprocs["ZZ"]        = [610,   1001,      "EWK",         True]
    else :
        dprocs["EWK"]        = [610,   1001,      "EWK",         True]
    if not "4l" in category :
        dprocs["TTW"]        = [823,   1001,      "none",        False]
        dprocs["TTWW"]       = [823,   1001,      "ttW + ttWW",        True]
    dprocs["TTZ"]        = [822,   1001,      "ttZ",         True]
    if not "4l" in category :
        dprocs["ttH_hzg"]    = [2,     1001,      "none",        False]
        dprocs["ttH_hmm"]    = [2,     1001,      "none",        False]
    dprocs["ttH_hww"]    = [2,     1001,      "none",        False]
    dprocs["ttH_hzz"]    = [2,     1001,      "none",        False]
    if not "crzz" in category : dprocs["ttH_htt"]    = [2,     1001,      "ttH",     True]
    #})
else :
    # if label == "none" it means that this process is to be merged with the anterior key
    #                      color, fillStype, label,       , make border
    if not "4l" in category :
        dprocs[fakes]        = [12,     3345,      "Non-prompt",        True]
        dprocs[flips]        = [1,     3006,      "Charge mis-m",       True]
    dprocs[conversions]  = [5,     1001,      "Conv.", True]
    dprocs["Rares_faketau"]  = [851,   1001,      "none",       False]
    dprocs["Rares_gentau"]   = [851,   1001,      "Rares",       True]
    if not "0tau" in category :
        dprocs["EWK_faketau"]    = [610,   1001,      "none",       False]
        dprocs["EWK_gentau"]     = [610,   1001,      "EWK",         True]
    else :
        dprocs["ZZ_faketau"]    = [610,   1001,      "none",       False]
        dprocs["ZZ_gentau"]     = [610,   1001,      "EWK",         True]
        dprocs["WZ_faketau"]    = [610,   1001,      "none",       False]
        dprocs["WZ_gentau"]     = [610,   1001,      "EWK",         True]
    dprocs["TTWW_faketau"]    = [823,   1001,      "none",         False]
    dprocs["TTWW_gentau"]     = [823,   1001,      "none",         False]
    dprocs["TTW_faketau"]   = [823,   1001,      "none",        False]
    dprocs["TTW_gentau"]    = [823,   1001,      "ttW + ttWW",  True]
    dprocs["TTZ_faketau"]    = [822,   1001,      "none",       False]
    dprocs["TTZ_gentau"]     = [822,   1001,      "TTZ",         True]
    dprocs["ttH_fake"]       = [682,   1001,      "none",     False]
    dprocs["ttH_hzg_gentau"] = [2,   1001,      "none",     False]
    dprocs["ttH_hww_gentau"] = [2,   1001,      "none",     False]
    dprocs["ttH_hzz_gentau"] = [2,   1001,      "none",     False]
    dprocs["ttH_hmm_gentau"] = [2,   1001,      "none",     False]
    dprocs["ttH_htt_gentau"] = [2,   1001,      "ttH",     True]

label_head = ""
if "1l_2tau" in category :
    label_head = label_head+" 1l+2#tau"
    ## remove "fakes_data" from first entry and add as last
    del dprocs[fakes]
    dprocs[fakes] =      [1,     3005,      "Mis.",        True]
if "2l_2tau" in category : label_head = label_head+" 2l+2#tau"
if "3l_1tau" in category : label_head = label_head+" 3l+1#tau"
if "2lss_1tau" in category : label_head = label_head+" 2lss+1#tau"
##################
if "2lss_0tau" in category and not "3j" in category : label_head = label_head+" 2lss l^{#pm}l^{#pm}"
if "3l_0tau" in category and not "zpeak" in category : label_head = label_head+" 3l"
if "2lss_0tau" in category and "3j" in category : label_head = label_head+" 2lss l^{#pm}l^{#pm}, ttW CR"
if "3l_0tau" in category and "zpeak" in category : label_head = label_head+" 3l, ttZ CR"
##################
if "2lss_ee_neg" in category and not "3j" in category : label_head = label_head+" 2lss e-e-"
if "2lss_ee_pos" in category and not "3j" in category  : label_head = label_head+" 2lss e+e+"
if "2lss_em_bl_neg" in category and not "3j" in category  : label_head = label_head+" 2lss e-#mu- loose-b"
if "2lss_em_bl_pos" in category and not "3j" in category  : label_head = label_head+" 2lss e+#mu+ loose-b"
if "2lss_mm_bl_neg" in category and not "3j" in category  : label_head = label_head+" 2lss #mu-#mu- loose-b"
if "2lss_mm_bl_pos" in category and not "3j" in category  : label_head = label_head+" 2lss #mu+#mu+ loose-b"
if "2lss_em_bt_neg" in category and not "3j" in category  : label_head = label_head+" 2lss e-#mu- tight-b"
if "2lss_em_bt_pos" in category and not "3j" in category  : label_head = label_head+" 2lss e+#mu+ tight-b"
if "2lss_mm_bt_neg" in category and not "3j" in category  : label_head = label_head+" 2lss #mu-#mu- tight-b"
if "2lss_mm_bt_pos" in category and not "3j" in category  : label_head = label_head+" 2lss #mu+#mu+ tight-b"
#################
if "3l_bl_neg" in category and not "zpeak" in category : label_head = label_head+"3l neg. loose-b"
if "3l_bl_pos" in category and not "zpeak" in category : label_head = label_head+"3l pos. loose-b"
if "3l_bt_neg" in category and not "zpeak" in category : label_head = label_head+"3l neg. tight-b"
if "3l_bt_pos" in category and not "zpeak" in category : label_head = label_head+"3l pos. tight-b"
if "4l" in category : label_head = label_head+"4l"
#################
if "2lss_ee_neg_3j" in category : label_head = label_head+"\n 2lss e-e- (ttW CR)"
if "2lss_ee_pos_3j" in category : label_head = label_head+"\n 2lss e+e+ (ttW CR)"
if "2lss_em_bl_neg_3j" in category : label_head = label_head+"\n 2lss e-#mu- loose-b (ttW CR)"
if "2lss_em_bl_pos_3j" in category : label_head = label_head+"\n 2lss e+#mu+ loose-b (ttW CR)"
if "2lss_mm_bl_neg_3j" in category : label_head = label_head+"\n 2lss #mu-#mu- loose-b (ttW CR)"
if "2lss_mm_bl_pos_3j" in category : label_head = label_head+"\n 2lss #mu+#mu+ loose-b (ttW CR)"
if "2lss_em_bt_neg_3j" in category : label_head = label_head+"\n 2lss e-#mu- tight-b (ttW CR)"
if "2lss_em_bt_pos_3j" in category : label_head = label_head+"\n 2lss e+#mu+ tight-b (ttW CR)"
if "2lss_mm_bt_neg_3j" in category : label_head = label_head+"\n 2lss #mu-#mu- tight-b (ttW CR)"
if "2lss_mm_bt_pos_3j" in category : label_head = label_head+"\n 2lss #mu+#mu+ tight-b (ttW CR)"
##################
if "3l_bl_neg_zpeak" in category : label_head = label_head+"\n 3l neg. loose-b (ttZ CR)"
if "3l_bl_pos_zpeak" in category : label_head = label_head+"\n 3l pos. loose-b (ttZ CR)"
if "3l_bt_neg_zpeak" in category : label_head = label_head+"\n 3l neg. tight-b (ttZ CR)"
if "3l_bt_pos_zpeak" in category : label_head = label_head+"\n 3l pos. tight-b (ttZ CR)"
if "4l_crwz" in category : label_head = label_head+"4l (WZ CR)"
if "4l_crzz" in category : label_head = label_head+"4l (ZZ CR)"
#################

if typeFit == "prefit" : label_head = label_head+" "+typeFit
else : label_head = label_head+" #mu(ttH)=#hat{#mu}"
print label_head

if not "4l" in category :
    if options.notFlips : del dprocs[flips]
if options.notConversions : del dprocs[conversions]
print ("will draw processes", list(dprocs.keys()))

if options.doMultilepCatPlot :
    if "2lss" in category :
        nbins = 5
        binlabels = ["ee", "e#mu bl", "e#mu bt", "#mu#mu bl", "#mu#mu bt"]
        if not "3j" in category :
            bins = [
            ["ttH_2lss_ee_neg", "ttH_2lss_ee_pos"],
            ["ttH_2lss_em_bl_neg", "ttH_2lss_em_bl_pos"],
            ["ttH_2lss_em_bt_neg", "ttH_2lss_em_bt_pos"],
            ["ttH_2lss_mm_bl_neg", "ttH_2lss_mm_bl_pos"],
            ["ttH_2lss_mm_bt_neg", "ttH_2lss_mm_bt_pos"]
            ]
        else : bins = [
        ["ttH_2lss_ee_neg_3j", "ttH_2lss_ee_pos_3j"],
        ["ttH_2lss_em_bl_neg_3j", "ttH_2lss_em_bl_pos_3j"],
        ["ttH_2lss_em_bt_neg_3j", "ttH_2lss_em_bt_pos_3j"],
        ["ttH_2lss_mm_bl_neg_3j", "ttH_2lss_mm_bl_pos_3j"],
        ["ttH_2lss_mm_bt_neg_3j", "ttH_2lss_mm_bt_pos_3j"]
        ]
    if "3l" in category :
        nbins = 2
        binlabels = ["bl", "bt"]
        if not "zpeak" in category :
            bins = [
            ["ttH_3l_bl_neg", "ttH_3l_bl_pos"],
            ["ttH_3l_bt_neg", "ttH_3l_bt_pos"]
            ]
        else : bins = [
        ["ttH_3l_bl_neg_zpeak", "ttH_3l_bl_pos_zpeak"],
        ["ttH_3l_bt_neg_zpeak", "ttH_3l_bt_pos_zpeak"]
        ]
    template = ROOT.TH1D("", "", nbins, 0, nbins+1)
else :
    if not options.original == "none" :
        fileOrig = options.original
        readFrom = category+"/data_obs"
    else :
        fileOrig = options.input
        readFrom = folder+"/data_obs"
    print ("template on ", fileOrig, readFrom)
    fileorriginal = ROOT.TFile(fileOrig)
    template = fileorriginal.Get(readFrom)
template.GetYaxis().SetTitle(labelY)
template.SetTitle(" ")
template.SetMinimum(options.minY)
template.SetMaximum(options.maxY)
fin = ROOT.TFile(options.input)

legend_y0 = 0.650;
legend1 = ROOT.TLegend(0.2400, legend_y0, 0.9450, 0.9150);
legend1.SetNColumns(3)
legend1.SetFillStyle(0);
legend1.SetBorderSize(0);
legend1.SetFillColor(10);
legend1.SetTextSize(0.040);
legend1.SetHeader(label_head);

if options.unblind :
    if not options.doMultilepCatPlot :
        data = rebin_data(template, folder, fin, options.fromHavester, errorBar=False)
        data_err = rebin_data(template, folder, fin, options.fromHavester) # no marker if zero entries
    else :
        data = rebin_dataCats(template, bins, folder, fin, options.fromHavester)
        data_err = data
    dumb_data = template.Clone()
    dumb_data.SetMarkerColor(1);
    dumb_data.SetMarkerStyle(20);
    dumb_data.SetMarkerSize(1);
    dumb_data.SetLineColor(1);
    dumb_data.SetLineWidth(2);
    dumb_data.SetLineStyle(1)
    legend1.AddEntry(dumb_data, "Observed", "pe");
if not options.doMultilepCatPlot : hist_total = rebin_total(template, folder, fin, divideByBinWidth, name_total)
else : hist_total = rebin_totalCat(template, bins, folder, fin, divideByBinWidth, name_total)
legend1.AddEntry(hist_total, "Uncertainty", "f");

canvas = ROOT.TCanvas("canvas", "canvas", 600, 1500);
canvas.SetFillColor(10);
canvas.SetBorderSize(2);
dumb = canvas.Draw();
del dumb

topPad = ROOT.TPad("topPad", "topPad", 0.00, 0.34, 1.00, 0.995);
topPad.SetFillColor(10);
topPad.SetTopMargin(0.075);
topPad.SetLeftMargin(0.20);
topPad.SetBottomMargin(0.03);
topPad.SetRightMargin(0.04);
if options.useLogPlot : topPad.SetLogy();
bottomPad = ROOT.TPad("bottomPad", "bottomPad", 0.00, 0.01, 1.00, 0.34);
bottomPad.SetFillColor(10);
bottomPad.SetTopMargin(0.0);
bottomPad.SetLeftMargin(0.20);
bottomPad.SetBottomMargin(0.35);
bottomPad.SetRightMargin(0.04);
####################################
canvas.cd();
dumb = topPad.Draw();
del dumb
topPad.cd();
dumb = hist_total.Draw("axis")
del dumb
histogramStack_mc = ROOT.THStack()
print ("list of processes considered and their integrals")
for key in  dprocs.keys() :
    print key
    if not options.doMultilepCatPlot : histogram = rebin_hist(template, fin, key, dprocs[key], divideByBinWidth)
    else : histogram = doCategories(template, bins, fin, key, dprocs[key], divideByBinWidth)
    histogramStack_mc.Add(histogram)
    err = ROOT.Double()
    content = histogram.IntegralAndError(0, histogram.GetXaxis().GetNbins()+1, err, "")
    print (key, content, err)
dumb = histogramStack_mc.Draw("hist,same")
del dumb
dumb = hist_total.Draw("e2,same")
del dumb
if options.unblind :
    dumb = data.Draw("P,same")
    del dumb
    dumb = data_err.Draw("e,same")
    del dumb
hist_total.Draw("axis,same")
dumb = legend1.Draw("same")
del dumb
labels = addLabel_CMS_preliminary()
for label in labels :
    dumb = label.Draw("same")
    del dumb
## if do categories add bottom text
#################################
canvas.cd();
dumb = bottomPad.Draw();
del dumb
bottomPad.cd();
bottomPad.SetLogy(0);
print ("doing bottom pad")
if not options.doMultilepCatPlot : hist_total_err = do_hist_total_err(template, options.labelX, name_total, category)
else : hist_total_err = do_hist_total_errCats(hist_total, bins, binlabels, options.labelX, name_total, category)
dumb = hist_total_err.Draw("e2")
del dumb
if options.unblind :
    if not options.doMultilepCatPlot :
        dataerr = err_data(hist_total, folder, options.fromHavester)
        dataerr_point = err_data(hist_total, folder, options.fromHavester, errorBar=False) # no marker if zero entries
    else :
        dataerr = err_dataCat(hist_total, data, folder, options.fromHavester)
        dataerr_point = dataerr
    #if options.fromHavester : dataerr.SetErrorX(0)
    dumb = dataerr.Draw("E,same")
    del dumb
    dumb = dataerr_point.Draw("P,same")
    del dumb
line = ROOT.TF1("line","1", hist_total_err.GetXaxis().GetXmin(), hist_total_err.GetXaxis().GetXmax());
line.SetLineStyle(3);
line.SetLineColor(ROOT.kBlack);
dumb = line.Draw("same");
del dumb
##################################
oplin = "linear"
if options.useLogPlot : oplin = "log"
optbin = "plain"
if divideByBinWidth : optbin = "divideByBinWidth"
if not options.doMultilepCatPlot :
    nameplot = options.odir+category+"_"+typeFit+"_"+optbin+"_unblind"+str(options.unblind)+"_"+oplin+".pdf"
else : nameplot = options.odir+category+"_"+typeFit+"_"+optbin+"_unblind"+str(options.unblind)+"_"+oplin+"_cats.pdf"
dumb = canvas.SaveAs(nameplot)
dumb = canvas.SaveAs(nameplot.replace(".pdf",".C"))
del dumb
print ("saved",nameplot)
