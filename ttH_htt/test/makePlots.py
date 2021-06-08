#!/usr/bin/env python
import os, subprocess, sys
import os, sys, time,math
import ROOT
from optparse import OptionParser
from collections import OrderedDict

sys.stdout.flush()
sys.stdout.flush()

from ROOT import gROOT
#gROOT.SetBatch(1)

from optparse import OptionParser
parser = OptionParser()
parser.add_option(
    "--nameOut", type="string",
    dest="nameOut",
    help="To appear on the name of the file with the final plot",
    default="test"
    )
parser.add_option(
    "--input", type="string", dest="input",
    help="A valid file with the shapes as output of combine FitDiagnostics"#,
    #default="/afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/posfit_3poi_ttVFromZero/ttH_fitDiagnostics.Test_shapes.root"
    )
parser.add_option(
    "--odir", type="string", dest="odir",
    help="Directory for the output plots",
    default="/afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/posfit_3poi_ttVFromZero/"
    )
parser.add_option(
    "--original", type="string", dest="original",
    help="The original datacard: used only to rebin (the datacard.root)",
    default="none"
    )
parser.add_option(
    "--channel", type="string", dest="channel",
    help="Name of the category as it is appear on the input file",
    default="ttH_1l_2tau_OS"
    )
parser.add_option(
    "--typeCat", type="string", dest="typeCat",
    help="Name of the category as it is appear on the input file",
    default="none"
    )
parser.add_option(
    "--labelX", type="string", dest="labelX",
    help="To appear on final plot",
    default="none"
    )
parser.add_option(
    "--nameLabel", type="string", dest="nameLabel",
    help="To appear on final plot",
    default="none"
    )
parser.add_option(
    "--useLogPlot", action="store_true", dest="useLogPlot",
    help="Self explanatory",
    default=False
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
parser.add_option(
    "--do_bottom", action="store_true", dest="do_bottom",
    help="If do bottom pad",
    default=False
    )
parser.add_option(
    "--IHEP", action="store_true", dest="IHEP",
    help="IHEP cards do not have directories",
    default=False
    )
parser.add_option(
    "--HH", action="store_true", dest="HH",
    help="is HH",
    default=False
    )
parser.add_option(
    "--era", type="int",
    dest="era",
    help="To appear on the name of the file with the final plot. If era == 0 it assumes you gave the path for the 2018 era and it will use the same naming convention to look for the 2017/2016.",
    default=2017
    )
parser.add_option(
    "--binToRead", type="string", dest="binToRead",
    help="Folder to read on the input root file -- if none it will try yo read all and put side by side.",
    default="none"
    )
parser.add_option(
    "--binToReadOriginal", type="string", dest="binToReadOriginal",
    help="Folder to read on the input root file -- if none it will try yo read all and put side by side.",
    default="none"
    )
parser.add_option(
    "--signal_type",    type="string",       dest="signal_type",
    help="Options: \"noresLO\" | \"nonresNLO\" | \"res\" ",
    default="none"
    )
parser.add_option(
    "--mass",           type="string",       dest="mass",
    help="Options: \n nonresNLO = it will be ignored \n noresLO = \"SM\", \"BM12\", \"kl_1p00\"... \n \"spin0_900\", ...",
    default="none"
    )
parser.add_option(
    "--HHtype",         type="string",       dest="HHtype",
    help="Options: \"bbWW\" | \"multilep\" ",
    default="none"
    )
parser.add_option(
    "--renamedHHInput", action="store_true", dest="renamedHHInput",
    help="If used input already renamed.",
    default=False
    )
(options, args) = parser.parse_args()

divideByBinWidth = options.divideByBinWidth
category         = options.channel
if options.typeCat == "none" :
    typeCat          = category
else :
    typeCat          = options.typeCat
print ("category", category, typeCat)
do_bottom = options.do_bottom
shapes_input = options.input
HH           = options.HH
signal_type  = options.signal_type
mass         = options.mass
HHtype       = options.HHtype
renamedHHInput         = options.renamedHHInput

binToRead = options.binToRead
if binToRead == "none" :
    binToRead = "ttH_" +  category
print ("binToRead", binToRead)

binToReadOriginal = options.binToReadOriginal
if binToReadOriginal == "none" :
    binToReadOriginal = "ttH_" + category
print ("binToReadOriginal", binToReadOriginal)

print ("nameOut", options.nameOut)
labelY = "Events"
if divideByBinWidth : labelY = "Events / bin width"

if options.doPostFit :
    if not options.fromHavester :
        folder = "shapes_fit_s"
        folder_data = "shapes_fit_s" # it is a TGraphAsymmErrors, not histogram
        typeFit = "postfit"
    else :
        folder = binToRead + "_postfit"
        folder_data = binToRead + "_postfit" # it is a histogram
        typeFit = "postfit"
else :
    if not options.fromHavester :
        folder = "shapes_prefit"
        folder_data = "shapes_prefit" # it is a TGraphAsymmErrors, not histogram
        typeFit = "prefit"
    else :
        folder = binToRead + "_prefit"
        folder_data = binToRead + "_prefit" # it is a histogram
        typeFit = "prefit"
print ("folder", folder)

if not options.fromHavester :
    if not HH :
        name_total = "total"
    else :
        name_total = "total_background"
else : name_total = "TotalProcs"

execfile("python/data_manager_makePostFitPlots.py")
ROOT.gStyle.SetOptStat(0)
###ROOT.gROOT.SetBatch(0) ---> it still does not solve in batch if 1, and break in iterative if 0

flips       = "data_flips"
conversions = "Convs"
fakes       = "data_fakes"

if HH :
    info_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/list_channels_HH.py"
    execfile(info_file)
    print ("list of HH signals by channel taken from: %s" % info_file)
    higgs_procs_to_draw = list_channels( fakes, signal_type, mass, HHtype, renamedHHInput )["higgs_procs_to_draw"]
    print("higgs_procs_to_draw ", higgs_procs_to_draw)

info_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/configs/plot_options_HH.py"
execfile(info_file)
print ("list of signals/bkgs by channel taken from: " +  info_file)
procs  = list_channels_draw("ttH")[category]
print procs
leading_minor_H = list_channels_draw("ttH")[category]["leading_minor_H"]
print ("leading_minor_H", leading_minor_H)
leading_minor_tH = list_channels_draw("ttH")[category]["leading_minor_tH"]
print ("leading_minor_tH", leading_minor_tH)
if not HH :
    dprocs = options_plot ("ttH", category, procs["bkg_proc_from_data"] + procs['bkg_procs_from_MC'] + procs["signal"], leading_minor_H, leading_minor_tH, False)
else :
    dprocs = options_plot ("ttH", category, procs["bkg_proc_from_data"] + procs['bkg_procs_from_MC'], leading_minor_H, leading_minor_tH, False)
    #dprocsHH = options_plot ("ttH", category,  procs["signal_HH"], "HH", False, leading_minor_tH)

label_head = options_plot_ranges("ttH")[typeCat]["label"]
print (options_plot_ranges("ttH")[typeCat])
if options.doPostFit :
    list_cats = options_plot_ranges("ttH")[typeCat]["list_cats"]
else :
    list_cats = options_plot_ranges("ttH")[typeCat]["list_cats_original"]

if not options.nameLabel == "none" :
    label_head += options.nameLabel

if typeFit == "prefit" :
    label_head = label_head+", \n"+typeFit
else :
    label_head = label_head+", #mu(t#bar{t}H)=#hat{#mu}"

if not options.labelX == "none" :
    labelX = options.labelX
elif typeCat in options_plot_ranges("ttH").keys() :
    labelX = options_plot_ranges("ttH")[typeCat]["labelX"]
else : labelX = "BDT"

print ("will draw processes", list(dprocs.keys()))

if not options.original == "none" :
    fileOrig = options.original
else :
    fileOrig = shapes_input
print ("template on ", fileOrig)

era = options.era

minY = 1
if options.maxY == 1 :
    if typeCat in options_plot_ranges("ttH").keys() : minY = options_plot_ranges("ttH")[typeCat]["minY"]
else : minY = options.minY

maxY = 1
if options.maxY == 1 :
    if typeCat in options_plot_ranges("ttH").keys() :
        maxY = options_plot_ranges("ttH")[typeCat]["maxY"]
else : maxY = options.maxY
if options.era == 0 :
    maxY = 2 * maxY

print("reading shapes from: ", shapes_input)
fin = [ROOT.TFile(shapes_input, "READ")]
if options.era == 0 :
    fin = fin + [ROOT.TFile(shapes_input.replace("2018", "2017"), "READ")]
    fin = fin + [ROOT.TFile(shapes_input.replace("2018", "2016"), "READ")]
    print ("will sum up " + str(len(fin)) + " eras")
    print (shapes_input.replace("2018", "2017"))
    print (shapes_input.replace("2018", "2016"))

if not options.original == "none" :
    if not binToRead == "none" :
        catcats =  [binToRead]
    else :
        catcats = getCats(folder, fin[0], options.fromHavester)
    if options.IHEP :
        readFrom = ""
    elif not binToReadOriginal == "none" :
        readFrom =  binToReadOriginal + "/"
    else :
        readFrom =  "ttH_" + category + "/"
    print ("original readFrom ", readFrom)
    fileorriginal = ROOT.TFile(fileOrig, "READ")
    if options.IHEP :
        histRead = "x_TTZ"
    elif HH :
        histRead = "TTH"
    else :
        histRead = "TTW" #"ttH_htt"
    template = fileorriginal.Get(readFrom + histRead )
    template.GetYaxis().SetTitle(labelY)
    template.SetTitle(" ")
    nbinscatlist = [template.GetNbinsX()]
    datahist = fileorriginal.Get(readFrom + "data_obs")
else :
    if not binToRead == "none" :
        if len(list_cats) <= 1 :
            catcats = [binToRead] #[folder]
        else :
            if not options.era == 0 :
                catcats = [ cat.replace("2018", str(era)) for cat in list_cats]
            else :
                catcats = [ cat for cat in list_cats]
    else :
        if len(list_cats) == 0 :
            catcats = getCats(folder, fin[0], options.fromHavester)
        else :
            if options.era == 0 :
                catcats = list_cats
            else :
                catcats = [ cat.replace("2018", str(era)) for cat in list_cats]
    #catcats = [binToRead]
    print("Drawing: ", catcats)
    nbinstotal = 0
    nbinscatlist = []
    for catcat in catcats :
        if not options.fromHavester :
            readFrom = folder + "/" + catcat
        else :
            readFrom = catcat
            readFrom += "_prefit"
        hist = fin[0].Get(readFrom + "/" + name_total )
        print ("reading shapes", readFrom + "/" + name_total)
        print (hist.Integral())
        nbinscat =  GetNonZeroBins(hist)
        nbinscatlist += [nbinscat]
        print (readFrom, nbinscat)
        nbinstotal += nbinscat
        datahist = fin[0].Get(readFrom + "/data")
    template = ROOT.TH1F("my_hist", "", nbinstotal, 0 - 0.5 , nbinstotal - 0.5)
    template.GetYaxis().SetTitle(labelY)
    print (nbinscatlist)

legend_y0 = 0.645
legend1 = ROOT.TLegend(0.2400, legend_y0, 0.9450, 0.910)
legend1.SetNColumns(3)
legend1.SetFillStyle(0)
legend1.SetBorderSize(0)
legend1.SetFillColor(10)
legend1.SetTextSize(0.040)
print label_head
legend1.SetHeader(label_head)
header = legend1.GetListOfPrimitives().First()
header.SetTextSize(.05)
header.SetTextColor(1)
header.SetTextFont(62)

if options.unblind :
    dataTGraph1 = "NoneType"
    if not options.fromHavester :
        dataTGraph1 = ROOT.TGraphAsymmErrors()
        dataTGraph1.Set(template.GetXaxis().GetNbins())
    else :
        dataTGraph1 = template.Clone()
    lastbin = 0
    for cc, catcat in enumerate(catcats) :
        if not options.fromHavester :
            readFrom = folder + "/" + catcat
        else :
            readFrom = catcat
            readFrom += "_prefit"
        print( " histtotal ", readFrom + "/" + name_total )
        histtotal = fin[0].Get(readFrom + "/" + name_total )
        lastbin += rebin_data(
            template,
            dataTGraph1,
            readFrom,
            fin,
            options.fromHavester,
            lastbin,
            histtotal,
            nbinscatlist[cc]
            )
    dataTGraph1.Draw()
    legend1.AddEntry(dataTGraph1, "Data", "p")
hist_total = template.Clone()

lastbin = 0
for cc, catcat in enumerate(catcats) :
    if not options.fromHavester :
        readFrom = folder + "/" + catcat
    else :
        readFrom = catcat
        readFrom += "_prefit"
    print ("read the hist with total uncertainties", readFrom, catcat)
    lastbin += rebin_total(
        hist_total,
        readFrom,
        fin,
        divideByBinWidth,
        name_total,
        lastbin,
        do_bottom,
        labelX,
        nbinscatlist[cc]
        )

if do_bottom :
    canvas = ROOT.TCanvas("canvas", "canvas", 600, 1500)
else :
    canvas = ROOT.TCanvas("canvas", "canvas", 900, 900)
canvas.SetFillColor(10)
canvas.SetBorderSize(2)
dumb = canvas.Draw()
del dumb

if do_bottom :
    topPad = ROOT.TPad("topPad", "topPad", 0.00, 0.34, 1.00, 0.995)
    topPad.SetFillColor(10)
    topPad.SetTopMargin(0.075)
    topPad.SetLeftMargin(0.20)
    topPad.SetBottomMargin(0.053)
    topPad.SetRightMargin(0.04)
    if options.useLogPlot or options_plot_ranges("ttH")[typeCat]["useLogPlot"]:
        topPad.SetLogy()

    bottomPad = ROOT.TPad("bottomPad", "bottomPad", 0.00, 0.05, 1.00, 0.34)
    bottomPad.SetFillColor(10)
    bottomPad.SetTopMargin(0.036)
    bottomPad.SetLeftMargin(0.20)
    bottomPad.SetBottomMargin(0.35)
    bottomPad.SetRightMargin(0.04)
else :
    topPad = ROOT.TPad("topPad", "topPad", 0.00, 0.05, 1.00, 0.995)
    topPad.SetFillColor(10)
    topPad.SetTopMargin(0.075)
    topPad.SetLeftMargin(0.20)
    topPad.SetBottomMargin(0.1)
    topPad.SetRightMargin(0.04)
    if options.useLogPlot or options_plot_ranges("ttH")[typeCat]["useLogPlot"]:
        topPad.SetLogy()
####################################
canvas.cd()
dumb = topPad.Draw()
del dumb
topPad.cd()
del topPad
dumb = hist_total.Draw("axis")

del dumb
histogramStack_mc = ROOT.THStack()
print ("list of processes considered and their integrals")

linebin = []
linebinW = []
poslinebinW_X = []
pos_linebinW_Y = []
y0 = options_plot_ranges("ttH")[typeCat]["position_cats"]
if options.era == 0 :
    y0 = 2 * y0

## ugly hand fix to have the correct legend for 2lss_0tau in the ttH analysis
dumbhist = template.Clone()
if "2lss_0tau" in category :
    dumbhist.SetMarkerSize(0)
    dumbhist.SetFillColor(1)
    dumbhist.SetFillStyle(3006)
    dumbhist.SetLineColor(1)
if "3lctrl" in category :
    dumbhist.SetMarkerSize(0)
    dumbhist.SetFillColor(5)
    dumbhist.SetFillStyle(1001)
    dumbhist.SetLineColor(1)

for kk, key in  enumerate(dprocs.keys()) :
    hist_rebin = template.Clone()
    lastbin = 0
    addlegend = True
    print("Stacking ", key)
    for cc, catcat in enumerate(catcats) :
        if not cc == 0 :
            addlegend = False
        if kk == 0 :
            firstHisto = ROOT.TH1F()
        if not options.fromHavester :
            readFrom = folder + "/" + catcat
        else :
            readFrom = catcat
            readFrom += "_prefit"
        info_hist = rebin_hist(
            hist_rebin,
            fin,
            readFrom,
            key,
            dprocs[key],
            divideByBinWidth,
            addlegend,
            lastbin,
            nbinscatlist[cc],
            options.original,
            firstHisto
            )
        print (info_hist["lastbin"] , lastbin, nbinscatlist[cc] )
        lastbin += info_hist["lastbin"]
        if kk == 0 :
            print (info_hist)
            print ("info_hist[binEdge]", info_hist["binEdge"])
            if info_hist["binEdge"] > 0 :
                linebin += [ROOT.TLine(info_hist["binEdge"], 0., info_hist["binEdge"], y0*1.1)] # (legend_y0 + 0.05)*maxY
            x0 = float(lastbin - info_hist["labelPos"] - 1)
            sum_inX = 0.1950
            if len(catcat) > 2 :
                if len(catcat) == 3 :
                    sum_inX = 5.85
                else :
                    sum_inX = 4.0
            if len(catcat) == 0 :
                poslinebinW_X += [x0 - sum_inX]
            else :
                poslinebinW_X += [options_plot_ranges("ttH")[typeCat]["catsX"][cc]]
            pos_linebinW_Y += [y0]
    if hist_rebin == 0 or not hist_rebin.Integral() > 0 or (info_hist["labelPos"] == 0 and not options.original == "none" )  : # : (info_hist["labelPos"] == 0 and not options.original == "none" )
        continue
    print (key,  0 if hist_rebin == 0 else hist_rebin.Integral() )
    dumb = histogramStack_mc.Add(hist_rebin)
    del dumb

if HH :
    colorsH = [1, 4, 8, 5, 6]
    histogramsHH = [ROOT.TH1F(), ROOT.TH1F(), ROOT.TH1F(), ROOT.TH1F(), ROOT.TH1F()]
    for hh, Hproc in enumerate(higgs_procs_to_draw) :
        histHH = template.Clone()
        lastbin = 0
        if type(histHH) is not ROOT.TH1F :
            print ("Did not found %s" % Hproc)
            continue
        for cc, catcat in enumerate(catcats) :
            if not options.fromHavester :
                readFrom = folder + "/" + catcat
            else :
                readFrom = catcat
                readFrom += "_prefit"
            print ("read the hist with total uncertainties", readFrom, catcat)
            lastbin += rebin_total(
                histHH,
                readFrom,
                fin,
                divideByBinWidth,
                Hproc,
                lastbin,
                do_bottom,
                labelX,
                nbinscatlist[cc]
                )
        if lastbin == -100 :
            print ("Did not found %s" % Hproc)
            continue
        histHH.SetMarkerSize(0)
        histHH.SetLineWidth(3)
        histHH.SetFillColor(colorsH[hh])
        histHH.SetLineColor(colorsH[hh])
        histHH.SetFillStyle(3315)
        #histHH.Scale(1.18)
        histogramsHH[hh] = histHH.Clone()
        legend1.AddEntry(histogramsHH[hh], Hproc.replace("signal", "").replace("_", " ").replace("hh", "").replace("spin0", "").replace("ggf", "").replace("nonresonant", "").replace("kl", "").replace("1p00", "SM"), "f")
        print(Hproc.replace("signal", "").replace("_", ""), histHH.Integral())

for line1 in linebin :
    line1.SetLineColor(1)
    line1.SetLineStyle(3)
    line1.Draw()

dumb = hist_total.Draw("axis,same")
dumb = histogramStack_mc.Draw("hist,same")
del dumb
dumb = hist_total.Draw("e2,same")
del dumb
if HH :
    for histoHHdraw in histogramsHH :
        if histoHHdraw.Integral() > 0 :
            dumb = histoHHdraw.Draw("hist,same")
            del dumb
if options.unblind :
    dumb = dataTGraph1.Draw("e1P,same")
    del dumb
dumb = hist_total.Draw("axis,same")
del dumb

dumb = legend1.Draw("same")
del dumb

labels = addLabel_CMS_preliminary(options.era)
for ll, label in enumerate(labels) :
    print ("printing label", ll)
    if ll == 0 :
        dumb = label.Draw("same")
        del dumb
    else :
        dumb = label.Draw()
        del dumb

for cc, cat in enumerate(options_plot_ranges("ttH")[typeCat]["cats"]) :
    print ("Draw label cat", cat, cc)
    sumBottom = 0
    for ccf, cf in enumerate(cat) :
        linebinW = ROOT.TLatex()
        linebinW.DrawLatex(poslinebinW_X[cc], pos_linebinW_Y[cc] + sumBottom, cf)
        linebinW.SetTextFont(50)
        linebinW.SetTextAlign(12)
        linebinW.SetTextSize(0.05)
        linebinW.SetTextColor(1)
        if era == 0 :
            sumBottom += -4.4
        else :
            sumBottom += -2.4

legend1.AddEntry(hist_total, "Uncertainty", "f")

#################################
if do_bottom :
    canvas.cd()
    dumb = bottomPad.Draw()
    del dumb
    bottomPad.cd()
    bottomPad.SetLogy(0)
    print ("doing bottom pad")
    hist_total_err = template.Clone()
    lastbin = 0
    for cc, catcat in enumerate(catcats) :
        if not options.fromHavester :
            readFrom = folder + "/" + catcat
        else :
            readFrom = catcat
        histtotal = hist_total
        lastbin += do_hist_total_err(
            hist_total_err,
            labelX, histtotal  ,
            options_plot_ranges("ttH")[typeCat]["minYerr"],
            options_plot_ranges("ttH")[typeCat]["maxYerr"],
            era
            )
        print (readFrom, lastbin)
    dumb = hist_total_err.Draw("e2")
    del dumb
    if options.unblind :
        if not options.fromHavester :
            dataTGraph2 = ROOT.TGraphAsymmErrors()
        else :
            dataTGraph2 = template.Clone()
        lastbin = 0
        for cc, catcat in enumerate(catcats) :
            if not options.fromHavester :
                readFrom = folder + "/" + catcat
            else :
                readFrom = catcat
            histtotal = fin[0].Get((readFrom + "/" + name_total).replace("2018", str(era)) )
            lastbin += err_data(
                dataTGraph2,
                hist_total,
                dataTGraph1,
                options.fromHavester,
                hist_total,
                readFrom,
                fin[0])
        dumb = dataTGraph2.Draw("e1P,same")
        del dumb
    line = ROOT.TF1("line", "0", hist_total_err.GetXaxis().GetXmin(), hist_total_err.GetXaxis().GetXmax())
    line.SetLineStyle(3)
    line.SetLineColor(ROOT.kBlack)
    dumb = line.Draw("same")
    del dumb
    print ("done bottom pad")
    del bottomPad
##################################
oplin = "linear"
if options.useLogPlot :
    oplin = "log"
    print ("made log")
optbin = "plain"
if divideByBinWidth :
    optbin = "divideByBinWidth"

savepdf = options.odir+category+"_"+typeFit+"_"+optbin+"_"+options.nameOut+"_unblind"+str(options.unblind)+"_"+oplin + "_" + options.typeCat
print ("saving...", savepdf )
dumb = canvas.SaveAs(savepdf + ".pdf")
print ("saved", savepdf + ".pdf")
del dumb

dumb = canvas.Print(savepdf + ".root")
print ("saved", savepdf + ".root")
del dumb
canvas.IsA().Destructor(canvas)
#dumb = canvas.SaveAs(savepdf + ".png")
#print ("saved", savepdf + ".png")
#del dumb
#print ("saved", savepdf)
