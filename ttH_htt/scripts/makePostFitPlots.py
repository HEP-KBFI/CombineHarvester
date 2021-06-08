#!/usr/bin/env python

import os, subprocess, sys, time, math, re, shlex
import ROOT
from optparse import OptionParser
from collections import OrderedDict
from subprocess import Popen, PIPE
from CombineHarvester.ttH_htt.data_manager import *

from optparse import OptionParser
parser = OptionParser()
parser.add_option(
    "--inputDatacard", type="string", dest="inputDatacard",
    help="Output of combine to draw the shapes from (full or relative path)"
    )
parser.add_option(
    "--original", type="string", dest="original",
    help="if the datacard.txt is entered it rebin the plot with the datacard bins.",
    default="none"
    )
parser.add_option(
    "--channel", type="string", dest="channel",
    help="Name of the category as it is appear on the input file",
    default="1l_2tau"
    )
parser.add_option(
    "--labelX", type="string", dest="labelX",
    help="To appear on final plot",
    default="BDT"
    )
parser.add_option(
    "--divideByBinWidth", action="store_true", dest="divideByBinWidth",
    help="If final plot shall be done dividing bin content by bin width ",
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
parser.add_option("--analysis",       type="string",       dest="analysis",    
    help="Analysis type = 'ttH' or 'HH' (to know what to take as Higgs procs and naming convention of systematics), Default ttH", 
    default="ttH"
    )
parser.add_option("--era",       type="string",       dest="era",    
    help="Era to consider (important for list of systematics and labeling). Default: 2017", 
    default="2017"
    )
parser.add_option("--shapeSyst",      action="store_true", dest="shapeSyst",   
    help="Do apply the shape systematics. Default: False", 
    default=False
    )
(options, args) = parser.parse_args()

#ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
sys.stdout.flush()

plainBins        = options.original == "none"
divideByBinWidth = options.divideByBinWidth
channel          = options.channel
doPostFit        = options.doPostFit
analysis     = options.analysis

opt_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/plot_options.py"
execfile(opt_file)
print ("plot options taken from: " +  opt_file)

info_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/list_channels.py"
execfile(info_file)
print ("list of signals/bkgs by channel taken from: " +  info_file)
higgs_procs        = list_channels(analysis)["higgs_procs"]
decays             = list_channels(analysis)["decays"]
list_channel_opt   = list_channels(analysis)["info_bkg_channel"]
bkg_proc_from_data = list_channel_opt[channel]["bkg_proc_from_data"]
bkg_procs_from_MC  = list_channel_opt[channel]["bkg_procs_from_MC"]

fileDatacard, odir = splitPath(options.inputDatacard)

labelY = "Events"
if divideByBinWidth : labelY = "Events / bin width"

labelX = options.labelX
if plainBins : labelX += " bin#"

folder      = analysis + '_'
if options.doPostFit :
    folder      += channel + "_postfit"
    typeFit     = "postfit"
else :
    folder      += channel + "_prefit"
    typeFit     = "prefit"
print ("folder", folder)

name_total = "TotalProcs"

all_procs = sum(higgs_procs,[]) + bkg_proc_from_data + bkg_procs_from_MC
proc_draw_options = options_plot(analysis, channel, all_procs, decays) 

label_head = "%s fit," % str(options.era)
label_head = label_head + " " + channel.replace("tau", "#tau").replace("_", " ").replace("ttZctrl", "ttZ CR").replace("ttWctrl", "ttW CR").replace("WZ", "WZ CR").replace("ZZ", "ZZ CR")

if typeFit == "prefit" : 
    label_head = label_head+" "+typeFit
else : 
    label_head = label_head+" #mu(ttH)=#hat{#mu}"
    
print ("Plotting: " +  label_head)
print ("will draw processes", list(proc_draw_options.keys()))

print ("Taking shapes from: %s" % options.original.replace(".txt", ".root"))
fin           = ROOT.TFile("%s/%s" % (odir, fileDatacard))

if not plainBins :
    # take histogram template from original datacard
    fileOrig = "%s"             % options.original.replace(".txt", ".root")
    readFrom = "%s_%s/data_obs" % (analysis, channel)
else :
    fileOrig = "%s/%s" % (odir, fileDatacard)
    readFrom = folder+"/data_obs"

print ("template histogram on ", fileOrig, readFrom)
fileorriginal = ROOT.TFile(fileOrig)
template      = fileorriginal.Get(readFrom)
template.GetYaxis().SetTitle(labelY)
template.SetTitle(" ")

legend_y0 = 0.650
legend1 = ROOT.TLegend(0.2400, legend_y0, 0.9450, 0.9150)
legend1.SetNColumns(3)
legend1.SetFillStyle(0)
legend1.SetBorderSize(0)
legend1.SetFillColor(10)
legend1.SetTextSize(0.040)
legend1.SetHeader(label_head)

fromHavester = True
## FIXME -- if we ever need to make plots from combine (not Havester)
plot_ranges = options_plot_ranges(analysis)[channel]
if options.unblind :
    data = rebin_data(template, folder, fin, fromHavester, plot_ranges)
    legend1.AddEntry(data, "Observed", "p")
hist_total = rebin_total(template, folder, fin, divideByBinWidth, name_total, plot_ranges)
legend1.AddEntry(hist_total, "Uncertainty", "f")

canvas = ROOT.TCanvas("canvas", "canvas", 1200, 1500)
canvas.SetBatch(ROOT.kTRUE)
canvas.SetFillColor(10)
canvas.SetBorderSize(2)

topPad = ROOT.TPad("topPad", "topPad", 0.00, 0.34, 1.00, 0.995)
topPad.SetBatch(ROOT.kTRUE)
topPad.SetFillColor(10)
topPad.SetTopMargin(0.075)
topPad.SetLeftMargin(0.20)
topPad.SetBottomMargin(0.00)
topPad.SetRightMargin(0.04)
if plot_ranges["useLogPlot"] : topPad.SetLogy()
dumb = topPad.Draw()
del dumb

bottomPad = ROOT.TPad("bottomPad", "bottomPad", 0.00, 0.01, 1.00, 0.34)
bottomPad.SetBatch(ROOT.kTRUE)
bottomPad.SetFillColor(10)
bottomPad.SetTopMargin(0.0)
bottomPad.SetLeftMargin(0.20)
bottomPad.SetBottomMargin(0.35)
bottomPad.SetRightMargin(0.04)
dumb = bottomPad.Draw()
del dumb

topPad.cd()
dumb = hist_total.Draw("axis")
del dumb
histogramStack_mc = ROOT.THStack()
print ("list of processes considered and their integrals")
for key in  proc_draw_options.keys() :
    histogram = rebin_hist(template, folder, fin, key, proc_draw_options[key], divideByBinWidth, legend1)
    dumb = histogramStack_mc.Add(histogram)
    del dumb
    print (key, histogram.Integral())
dumb = histogramStack_mc.Draw("hist,same")
del dumb
dumb = hist_total.Draw("e2,same")
del dumb
if options.unblind :
    dumb = data.Draw("e1P,same")
    del dumb
dumb = hist_total.Draw("axis,same")
del dumb
dumb = legend1.Draw("same")
del dumb
labels = addLabel_CMS_preliminary()
for label in labels :
    dumb = label.Draw("same")
    del dumb
#################################

bottomPad.cd()
bottomPad.SetLogy(0)
print ("doing bottom pad")
hist_total_err = do_hist_total_err(fin, template, folder, labelX, name_total, channel, plot_ranges)
dumb = hist_total_err.Draw("e2")
del dumb
if options.unblind :
    dataerr = err_data(fin, hist_total, folder, fromHavester)
    dumb = dataerr.Draw("e1P,same")
    del dumb
line = ROOT.TF1("line","1", hist_total_err.GetXaxis().GetXmin(), hist_total_err.GetXaxis().GetXmax())
line.SetLineStyle(3)
line.SetLineColor(ROOT.kBlack)
dumb = line.Draw("same")
del dumb
print ("done bottom pad")
##################################
oplin = "linear"
if plot_ranges["useLogPlot"] : oplin = "log"
if divideByBinWidth   : oplin += "_divideByBinWidth"

print ("made log")

outputPlot       = "%s/%s"        % (odir, fileDatacard.replace(".root",""))

nameOutputPlot = outputPlot + "_" + oplin + "_unblind" + str(options.unblind) + ".pdf" 
print (nameOutputPlot)

dumb = canvas.SaveAs(nameOutputPlot)
del dumb
canvas.Close()
ROOT.gSystem.ProcessEvents()
sys.stdout.flush()