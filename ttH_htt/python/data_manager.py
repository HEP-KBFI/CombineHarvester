import ROOT
import array
import math
from math import sqrt, sin, cos, tan, exp
import sys, os, re, shlex
from subprocess import Popen, PIPE
import glob

def checkSyst(syst) :
    print ("if do = up or do = nom:  do nom/up")
    if syst.type() != "shape" :
        print ("lnN ", syst.name(), syst.value_u(), syst.value_d())
        return
    print (syst.type())
    old_hd  = syst.shape_d()
    old_hu  = syst.shape_u()
    nominal = syst.shape()
    did_something = 0
    for bin in xrange(1, old_hu.GetNbinsX() + 1 ) :
        if abs(old_hu.GetBinContent(bin) - old_hd.GetBinContent(bin)) < 0.01 or abs(nominal.GetBinContent(bin) - old_hd.GetBinContent(bin)) < 0.01 :
            old_hd.SetBinContent(bin, nominal.GetBinContent(bin))
            did_something = 1
    if 0 < 1 or did_something == 1 :
        syst.set_shapes(old_hu, old_hd, nominal)
        print ("modifyed ", syst.name(), nominal.GetName())
        return
    else :
        return

### reminiscent of doing cards with wrong XS normalization, leave it here in case we need again
def scaleBy(proc):
    # scale tHq by 3 and WZ by 2
    if "tHq" in proc.process() :
        proc.set_rate(proc.rate()*3)
        print ("scale " +   str(proc.process()) +  " by " + str(3))
    #if "WZ"  in proc.process() :
    #     proc.set_rate(proc.rate()*2)
    #     print ("scale " +   str(proc.process()) +  " by " + str(2))
    #    p.set_signal(True)
    ### use as:
    #print ("placeholder for 2lss 1tau processes ")
    #cb.ForEachProc(scaleBy)

def extract_thu(proc, coupling) :
    import pandas
    tagf = coupling.replace('p', '.').replace('m','-').replace('kt_', "")
    ct,cv = tuple(map(float, tagf.split('_kv_')))
    print("kt = "+ str(ct), "kv = " + str(cv))
    ###
    filethu = syst_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/data/%s_thuncertainties.txt" % proc
    data = pandas.read_csv(filethu, sep = ' ')
    data.dropna(inplace=True)
    data=data.astype(float)
    return {
    "pdf"   : 1. + round( data.loc[(data.cf == ct) & (data.cv == cv)]["pdfunc+[%]"].values[0]*0.01, 3),
    "qcdup" : 1. + round(data.loc[(data.cf == ct) & (data.cv == cv)]["scaleunc+[%]"].values[0]*0.01, 3),
    "qcddo" : 1. + round(data.loc[(data.cf == ct) & (data.cv == cv)]["scaleunc-[%]"].values[0]*0.01, 3)
    }


def lists_overlap(a, b):
  sb = set(b)
  return any(el in sb for el in a)

def list_proc(syst_list, MC_proc, all_proc_bkg, name_syst) :
    if syst_list["proc"] == "MCproc" :
        procs = MC_proc
    elif syst_list["proc"] in [ "ttHproc", "tHqproc", "tHWproc", "HHproc", "ggHproc", "qqHproc", "VHproc" ]:
        proc_signal_plus_data_bkg = list(set(MC_proc) - set(all_proc_bkg))
        proc_pfx = ('WH_', 'ZH_') if syst_list["proc"] == "VHproc" else '{}_'.format(syst_list["proc"].replace('proc', ''))
        procs = [ proc for proc in proc_signal_plus_data_bkg if proc.startswith(proc_pfx) and not proc.endswith(('FWDH', 'PTH_fwd')) ]
        if not procs:
            print("Skipping {} because unable to find processes that start with {} from: {}".format(
                name_syst, proc_pfx, ', '.join(proc_signal_plus_data_bkg),
            ))
    elif syst_list["proc"] == "TTWproc":
        procs = [ proc for proc in MC_proc if proc in [ "TTW", "TTWW" ] ]
    elif not set(syst_list["proc"]) <= set(all_proc_bkg) :
        print ("skiped " + name_syst  + " as the channel does not contain the process: ", syst_list["proc"])
        procs = []
    elif lists_overlap(syst_list["proc"], all_proc_bkg):
        intersection = list(set(list(syst_list["proc"])) - set(all_proc_bkg))
        procs = list(set(list(syst_list["proc"])) - set(intersection))
    else :
        procs = syst_list["proc"]
    return procs

def construct_templates(cb, ch, specific_ln_shape_systs, specific_shape_shape_systs, inputShapes, MC_proc, shape, noX_prefix, minimal_patch = False ):
    created_ln_to_shape_syst = []
    created_shape_to_shape_syst = []
    print ("Doing template to fake/gen tau systematics")
    try : tfile = ROOT.TFile(inputShapes, "READ")
    except : print ("Doesn't exist" + inputShapes)
    outpuShape = inputShapes.replace(".root", "_genfakesyst.root")
    tfileout = ROOT.TFile(outpuShape, "recreate")
    tfileout.cd()
    for ln_to_shape in specific_ln_shape_systs :
        print ("==============================")
        print ("Doing themplates to: " + ln_to_shape + " with value " + str(specific_ln_shape_systs[ln_to_shape]["value"]))
        name_syst = ln_to_shape
        print("From ln: " +  name_syst)
        if not specific_ln_shape_systs[ln_to_shape]["correlated"] :
            name_syst = ln_to_shape.replace("%sl" % analysis, "%sl%s" % (analysis, str(era - 2000)))
        for proc in MC_proc :
            histUp = ROOT.TH1F()
            histDo = ROOT.TH1F()
            ## fixme: old cards does not have uniform naming convention to tH/VH -- it should be only continue to conversions
            # do not write Convs -- otherwise it's doubled for 2lss+1tau and 3l+1tau
            if "Convs" in proc :
                if minimal_patch:
                    try : hist = tfile.Get(histFind)
                    except : print ("Doesn't find" + histFind)
                    hist.Write()
                continue
            #if  proc or "conversions" in proc or proc in ["tHq", "tHW", "VH"]: continue
            print ("================================================")
            central = 0
            central_calc = 0
            if noX_prefix : histFind = "%s" % (proc)
            else : histFind = "x_%s" % (proc)
            try : hist = tfile.Get(histFind)
            except : print ("Doesn't find" + histFind)
            histUp = hist.Clone()
            histUp.Scale(0.)
            histDo = hist.Clone()
            histDo.Scale(0.)
            central = hist.Integral()
            for typeHist in ["faketau", "gentau"] :
                if noX_prefix : histFind = "%s_%s" % (proc, typeHist)
                else : histFind = "x_%s_%s" % (proc, typeHist)
                try : hist = tfile.Get(histFind)
                except : print ("Doesn't find" + histFind)
                try : integral  = hist.Integral()
                except : print ("Can't calculate integral" + histFind)
                print (histFind, hist.Integral())
                # clone only the structure -- for the case of no shift
                if specific_ln_shape_systs[ln_to_shape]["type"] == typeHist :
                    histUp.Add(hist)
                    central_calc += hist.Integral()
                    histUp.Scale(specific_ln_shape_systs[ln_to_shape]["value"])
                    print (histFind + " Multiply up part by " + str(specific_ln_shape_systs[ln_to_shape]["value"]), "Integral = " + str(histUp.Integral()))
                    histDo.Add(hist)
                    histDo.Scale(1 - (specific_ln_shape_systs[ln_to_shape]["value"] - 1))
                    print (histFind + " Multiply down part by " + str(1 - (specific_ln_shape_systs[ln_to_shape]["value"] - 1)), "Integral = " + str(histDo.Integral()))
                else :
                    print ("Adding " + histFind + " part ")
                    histUp.Add(hist)
                    central_calc += hist.Integral()
                    histDo.Add(hist)
            if noX_prefix : nameprocx = "%s_%s" % (proc, name_syst)
            else : nameprocx = "x_%s_%s" % (proc, name_syst)
            histUp.SetName("%sUp"   % (nameprocx))
            histDo.SetName("%sDown" % (nameprocx))
            histUp.Write()
            histDo.Write()
            print("Central/gentau+faketau/Up/Down", central, central_calc, histUp.Integral(), histDo.Integral())
        created_ln_to_shape_syst += ["%s" % name_syst]
        if shape :
            for shape_to_shape in specific_shape_shape_systs :
                print ("Doing themplates to: " + shape_to_shape + " (originally shape) " )
                central_calc = 0
                histCentral = ROOT.TH1F()
                name_syst = shape_to_shape.replace("CMS_", "CMS_constructed_")
                #if not specific_shape_shape_systs[shape_to_shape]["correlated"] :
                #    name_syst = name_syst.replace("%sl" % analysis, "%sl%s" % (analysis, str(era - 2000)))
                for proc in MC_proc :
                    # do not write Convs -- otherwise it's doubled for 2lss+1tau and 3l+1tau
                    if "Convs" in proc :
                        if minimal_patch:
                            histFindCentral = "%s" % (proc)
                            try : histCentral = tfile.Get(histFindCentral)
                            except : print ("Doesn't find" + histFindCentral)
                            histCentral.Write()
                        continue
                    histFindCentral = "%s_%s" % (proc, typeHist)
                    try : histCentral = tfile.Get(histFindCentral)
                    except : print ("Doesn't find" + histFindCentral)
                    try : integral = histCentral.Integral()
                    except : print ("Doesn't find integral" + histFindCentral)
                    histUp = ROOT.TH1F("%s_clone" % histCentral.GetName(),
                             histCentral.GetTitle(),
                             histCentral.GetNbinsX(),
                             histCentral.GetXaxis().GetXbins().GetArray())
                    histDo = ROOT.TH1F("%s_clone2" % histCentral.GetName(),
                             histCentral.GetTitle(),
                             histCentral.GetNbinsX(),
                             histCentral.GetXaxis().GetXbins().GetArray())
                    for typeHist in ["faketau", "gentau"] :
                        histUpLoc = ROOT.TH1F()
                        histDoLoc = ROOT.TH1F()
                        histFindUp = "%s_%s_%sUp" % (proc, typeHist, shape_to_shape)
                        try : histUpLoc = tfile.Get(histFindUp)
                        except : print ("Doesn't find" + histFindUp)
                        histFindDown = "%s_%s_%sDown" % (proc, typeHist, shape_to_shape)
                        try : histDoLoc = tfile.Get(histFindDown)
                        except : print ("Doesn't find" + histFindDown)
                        print (histFindCentral, histFindDown, histFindUp)
                        histUp.Add(histUpLoc)
                        histDo.Add(histDoLoc)
                    histUp.SetName("%s_%sUp"    % (proc, name_syst))
                    histDo.SetName("%s_%sDown" % (proc, name_syst))
                    histUp.Write()
                    histDo.Write()
                    print("Central/Up/Down", tfile.Get(proc).Integral(), histUp.Integral(), histDo.Integral())
                created_shape_to_shape_syst += [name_syst]
                print ("constructed up/do templates from : " + shape_to_shape + " and saved as "+ name_syst )
    tfileout.Close()
    print ("File with ln to shape syst: " +  outpuShape)

    finalFile = outpuShape.replace(".root", "_all.root")
    print ("File merged with fake/gen syst: ", finalFile)
    hadd_str = "hadd -f %s %s %s" % (finalFile, outpuShape, inputShapes)
    print ('doing hadd : ' + hadd_str)
    p = Popen(shlex.split(hadd_str) , stdout=PIPE, stderr=PIPE)
    comboutput = p.communicate()[0]
    #if "conversions" in MC_proc : MC_proc.remove("conversions")
    ## fixme: old cards does not have uniform naming convention to tH/VH
    #MC_proc_less = list(set(list(MC_proc)) - set(["Convs"]))
    #for shape_syst in created_ln_to_shape_syst + created_shape_to_shape_syst :
    #    cb.cp().process(MC_proc_less).AddSyst(cb,  shape_syst, "shape", ch.SystMap()(1.0))
    #    print ("added " + shape_syst + " as shape uncertainty to the MC processes, except conversions")
    MC_proc_less = list(set(list(MC_proc)) - set(["Convs"]))
    for shape_syst in created_ln_to_shape_syst :
        cb.cp().process(MC_proc_less).AddSyst(cb,  shape_syst, "shape", ch.SystMap()(1.0))
        print ("added " + shape_syst + " as shape uncertainty to the MC processes, except conversions")
    for shape_syst in created_shape_to_shape_syst :
        cb.cp().process(MC_proc_less).AddSyst(cb,  shape_syst, "shape", ch.SystMap()(1.0))
        print ("added " + shape_syst + " as shape uncertainty to data_fakes")
    return finalFile

def manipulate_cards_Ov(output_file, coupling, bins, no_data, all_procs, preparedatacard) :
    print "Post Manipulate cards (if needed)"
    print (output_file)
    test_name_tHq = "tHq_%s" % coupling
    test_name_tHW = "tHW_%s" % coupling
    test_name_ttH = "ttH_%s" % coupling
    tfileout = ROOT.TFile(output_file + ".root", "UPDATE")
    integral_data = []
    no_data = no_data and coupling == "none"
    for bb in bins :
        data_obs = ROOT.TH1F()
        #data_obs.SetName("data_obs")
        for nkey, keyO in enumerate(tfileout.GetListOfKeys()) :
            obj =  keyO.ReadObj()
            obj_name = keyO.GetName()
            if test_name_tHq in obj_name or test_name_tHW in obj_name or test_name_ttH in obj_name :
                if test_name_tHq in obj_name and not coupling == "none":
                    #test_name = test_name_tHq
                    new_name = obj_name.replace("_" + coupling,"").replace("p0", "")
                    print ("renaming " +  obj_name + " to " + new_name)
                elif test_name_tHW in obj_name and not coupling == "none":
                    #test_name = test_name_tHW
                    new_name = obj_name.replace("_" + coupling,"").replace("p0", "")
                    print ("renaming " +  obj_name + " to " + new_name)
                elif test_name_ttH in obj_name and not coupling == "none":
                    #test_name = test_name_ttH
                    new_name = obj_name.replace("_" + coupling,"").replace("p0", "")
                    print ("renaming " +  obj_name + " to " + new_name)
                print ("renaming", new_name,  obj_name)
                obj.SetName(new_name)
                tfileout.cd()
                obj.Write()
                ROOT.gDirectory.Delete(obj_name+";1")
                tfileout.cd()
    tfileout.Close()
    outfile = output_file + ".txt"
    f1 = open(outfile, 'r').read()
    f2 = open(outfile, 'w')
    m = f1.replace(test_name_tHq, "tHq")
    m = m.replace(test_name_tHW, "tHW")
    m = m.replace(test_name_ttH, "ttH")
    #m = f1.replace(test_name_tHq.replace("p0", ""), "tHq")
    #m = m.replace(test_name_tHW.replace("p0", ""), "tHW")
    #m = m.replace(test_name_ttH.replace("p0", ""), "ttH")
    f2.write(m)
    f2.close()

def rescale_stxs_pT_bins (inputShapesI, stxs_pT_bins, era) :
    ## it assumes no subdirectories in the preparedatacards file,
    tfileout1 = ROOT.TFile(inputShapesI, "UPDATE")
    tfileout1.cd()
    for nkey, key in enumerate(tfileout1.GetListOfKeys()) :
        obj =  key.ReadObj()
        obj_name = key.GetName()
        #if type(obj) is not ROOT.TH1F and type(obj) is not ROOT.TH1D and type(obj) is not ROOT.TH1 and type(obj) is not ROOT.TH1S and type(obj) is not ROOT.TH1C and type(obj) is not ROOT.TH1 :
        if type(obj) is not ROOT.TH1F :
            if type(obj) is ROOT.TH1 :
                print ("data_obs can be be TH1")
                continue
            else :
                print ("WARNING: All the histograms that are not data_obs should be TH1F - otherwhise combine will crash!!!")
                sys.exit()
        factor = 1.0
        nominal  = ROOT.TH1F()
        if "PTH" in obj_name:
            if "_fake_" in obj_name or "Convs" in obj_name or "flip" in obj_name :
                continue
            if not "_htt" in obj_name and not "_hww" in obj_name and not "_hzz" in obj_name and not "_hzg" in obj_name and not "_hmm" in obj_name :
                continue
            for stxs_key in stxs_pT_bins.keys() :
                if stxs_key in obj_name :
                    factor = stxs_pT_bins[stxs_key][era]
                    break
            if factor == 1.0 :
                print ("Something wrong, it is not scaling ", obj_name)
            nominal = obj.Clone()
            nominal.Scale( factor )
            nominal.Write()
            print ("rescaled ", stxs_key, obj_name, factor, nominal.Integral(), obj.Integral())
    tfileout1.Close()

def check_systematics (inputShapesL, coupling, stxs_pT_bins) :
    if coupling == "none" :
        print ("Not doing cards with couplings, skping to modify all shapes with 'kt' mark on it from tHq/tHW/HH")
    ## it assumes no subdirectories in the preparedatacards file,
    tfileout = ROOT.TFile(inputShapesL, "UPDATE")
    tfileout.cd()
    ###########################
    for nkey, key in enumerate(tfileout.GetListOfKeys()) :
        obj =  key.ReadObj()
        obj_name = key.GetName()
        if (coupling == "none" or coupling == "kt_1_kv_1") and "_kt_" in obj_name :
            continue
        if not (coupling == "none" or coupling == "kt_1_kv_1") and ("tHq" in obj_name or "tHW" in obj_name) and not coupling in obj_name :
            continue
        ### FIXME: not doing BSM HH
        if "HH" in obj_name and "_kt_" in obj_name :
            continue
        #if  "data_fakes" in obj_name:
        #    print ("===========> type of ", obj_name, type(obj))
        if type(obj) is not ROOT.TH1F and type(obj) is not ROOT.TH1D and type(obj) is not ROOT.TH1 and type(obj) is not ROOT.TH1S and type(obj) is not ROOT.TH1C :
            continue
        #if "data_fakes" in obj_name: # FRjt_shape" in obj_name and
        #    print ("===========> TH1F type of ", obj_name)
        is_stxs = any(stxs_pT_val in obj_name for stxs_pT_bin in stxs_pT_bins for stxs_pT_val in stxs_pT_bins[stxs_pT_bin])
        is_stxs = False # actually modify the contents of STXS-binned distributions, in order for the datacard to pass the validation step

        if "Down" in obj_name :
            name_nominal = obj_name.split("_CMS")[0]
            name_up = obj_name.replace("Down", "Up")
            name_do = obj_name
            name_syst = obj.GetName().replace(name_nominal, "").replace("Down", "")
            nominal  = ROOT.TH1F()
            histo_up = ROOT.TH1F()
            histo_do = ROOT.TH1F()
            nominal  = tfileout.Get( name_nominal )
            histo_up = tfileout.Get( name_up )
            histo_do = tfileout.Get( obj_name )
            did_something_do = 0
            did_something_up = 0
            did_something_nom = 0
            try :
                histo_do.Integral()
            except :
                print ("There was no Do histo in", obj.GetName(), name_do)
                continue
            #####
            try :
                histo_up.Integral()
            except :
                if "CMS_ttHl_JESHEM" in name_do :
                    hadNom = True
                    try :
                        nominal.Integral()
                    except :
                        histo_up = histo_do
                        histo_up.SetName(name_do.replace("Down", "Up"))
                        hadNom = False
                        print ("adding HEM up as Down in ", name_nominal, name_do.replace("Down", "Up"))
                    if hadNom :
                        histo_up = nominal
                        histo_up.SetName(name_do.replace("Down", "Up"))
                        print ("adding HEM up as nominal in ", name_nominal, name_do.replace("Down", "Up"))
                else :
                    print ("There was no Up histo in", obj.GetName())
                    continue
                #if "FRjt_shape" in name_up and "data_fakes" in name_up:
                #    print ("===========> found ", name_up)
            if not is_stxs:
                for binn in xrange(1, histo_do.GetNbinsX() + 1 ) :
                    #if "FRjt_shape" in name_up and "data_fakes" in name_up:
                    #    print ("======> ", name_up, nominal.GetBinContent(binn), histo_do.GetBinContent(binn), histo_up.GetBinContent(binn), histo_do.GetBinError(binn), histo_up.GetBinError(binn), histo_do.GetBinContent(binn)/nominal.GetBinContent(binn), histo_up.GetBinContent(binn)/nominal.GetBinContent(binn))
                    if nominal.GetBinContent(binn) > 0 :
                        ## if up or do is zero fixe it
                        if histo_do.GetBinContent(binn) == 0 and histo_up.GetBinContent(binn) == 0:
                            # both up- and down-fluctuations are zero while the nominal is not
                            histo_do.SetBinContent(binn, nominal.GetBinContent(binn))
                            histo_up.SetBinContent(binn, nominal.GetBinContent(binn))
                            did_something_do = 1
                            did_something_up = 1
                        if histo_do.GetBinContent(binn) == 0 and abs(histo_up.GetBinContent(binn)) > 0 :
                            # down-fluctuation zero while nominal and up are not
                            histo_do.SetBinContent(binn, nominal.GetBinContent(binn)*nominal.GetBinContent(binn)/histo_up.GetBinContent(binn)  )
                            # down = nominal / (up/nominal)
                            did_something_do = 1
                        if histo_up.GetBinContent(binn) == 0 and abs(histo_do.GetBinContent(binn)) > 0 :
                            # up-fluctuation zero while nominal and down are not
                            histo_up.SetBinContent(binn, nominal.GetBinContent(binn)*nominal.GetBinContent(binn)/histo_do.GetBinContent(binn)  )
                            # up = nominal/(down/nominal)
                            did_something_up = 1
                        ##### then, deflate if too big
                        # if up/nom > 10: up = 10*nom
                        # if down/nom > 10: down = 10*nom
                        if histo_do.GetBinContent(binn)/nominal.GetBinContent(binn) > 100  :
                            print "WARNING: big shift in template for syst template %s down in process %s : variation = %g"%( name_syst, name_nominal, histo_do.GetBinContent(binn)/nominal.GetBinContent(binn))
                            histo_do.SetBinContent(binn, 100*nominal.GetBinContent(binn)  )
                            did_something_do = 1
                        if histo_up.GetBinContent(binn)/nominal.GetBinContent(binn) > 100 :
                            print "WARNING: big shift in template for syst template %s up in process %s : variation = %g"%( name_syst, name_nominal, histo_up.GetBinContent(binn)/nominal.GetBinContent(binn))
                            histo_up.SetBinContent(binn, 100*nominal.GetBinContent(binn) )
                            did_something_up = 1
                        #####
                        #if histo_do.GetBinError(binn)/nominal.GetBinContent(binn) > 100  :
                        #    print "WARNING: big shift in template for syst template %s down in process %s : variation = %g"%( name_syst, name_nominal, histo_do.GetBinContent(binn)/nominal.GetBinContent(binn))
                        #    histo_do.SetBinError(binn, 100*nominal.GetBinContent(binn)  )
                        #    did_something_do = 1
                        #if histo_up.GetBinError(binn)/nominal.GetBinContent(binn) > 100 :
                        #    print "WARNING: big shift in template for syst template %s up in process %s : variation = %g"%( name_syst, name_nominal, histo_up.GetBinContent(binn)/nominal.GetBinContent(binn))
                        #    histo_up.SetBinError(binn, 100*nominal.GetBinContent(binn) )
                        #    did_something_up = 1
                    else :
                        if nominal.GetBinContent(binn) == 0 and (abs(histo_do.GetBinContent(binn)) > 0 or  abs(histo_up.GetBinContent(binn)) > 0) :
                            print ("WARNING, nominal is zero while up/do not; up/do = %s/%s. Setting nom/up/do 0.00001 " % (str(histo_do.GetBinContent(binn))  , str(histo_up.GetBinContent(binn))))
                        histo_up.SetBinContent(binn, 0.00001 )
                        nominal.SetBinContent(binn, 0.00001 )
                        histo_do.SetBinContent(binn, 0.00001 )
                        did_something_nom = 1
                        did_something_do = 1
                        did_something_up = 1
                    if "data_fakes" in name_up:
                        print ("=========> ", name_up, nominal.GetBinContent(binn), histo_do.GetBinContent(binn), histo_up.GetBinContent(binn), histo_do.GetBinError(binn), histo_up.GetBinError(binn), histo_do.GetBinContent(binn)/nominal.GetBinContent(binn), histo_up.GetBinContent(binn)/nominal.GetBinContent(binn))
            if did_something_nom == 1 or did_something_up == 1 or did_something_do == 1 :
                assert(not is_stxs)
                print ("modified syst templates in ", name_syst, " in process: ", name_nominal, " nom/up/do = ", did_something_nom,  did_something_up, did_something_do)
                #tfileout.cd(obj0_name)
                histo_up.Write()
                nominal.Write()
                histo_do.Write()
            elif "HEM" in name_do:
                histo_up.Write()
        #else :
        #    print("rebining ", obj.GetName())
        #    nominal  = tfileout.Get( obj.GetName() )
        #    nominal.Rebin(10)
        #    nominal.Write()


    tfileout.Close()

def manipulate_cards(output_file, coupling, bins, no_data, all_procs, preparedatacard) :
    print "Post Manipulate cards (if needed)"
    test_name_tHq = "tHq_%s" % coupling
    test_name_tHW = "tHW_%s" % coupling
    test_name_VH = "VH"
    test_name_TTWH = "TTWH"
    test_name_TTZH = "TTZH"
    test_name_HH = "HH"
    tfileout = ROOT.TFile(output_file + ".root", "UPDATE")
    integral_data = []
    no_data = no_data and coupling == "none"
    for bb in bins :
        data_obs = ROOT.TH1F()
        #data_obs.SetName("data_obs")
        for nkey, keyO in enumerate(tfileout.GetListOfKeys()) :
            # this bellow would be interesting if we would know all the histogram names
            #rootmv file:part1_*_part2 file:new_name
            # https://root.cern.ch/how/how-quickly-inspect-content-file
            obj0 =  keyO.ReadObj()
            for nkey, key in enumerate(obj0.GetListOfKeys()) :
                #tfileout.get()
                obj =  key.ReadObj()
                obj_name = key.GetName()
                if type(obj) is not ROOT.TH1F : continue
                if test_name_tHq in obj_name\
                    or test_name_tHW in obj_name :
                    #or test_name_VH in obj_name\
                    #or test_name_TTWH in obj_name\
                    #or test_name_TTZH in obj_name\
                    print (obj_name)
                    if obj_name == "TTWH_hww" or obj_name == "TTZH_hww" : continue
                    if (test_name_TTWH in obj_name) and not "_" in obj_name and coupling == "none":
                        test_name = test_name_TTWH
                        new_name = obj_name + "_hww"
                        print ("renaming TTVH", new_name,  obj_name)
                    elif (test_name_TTZH in obj_name) and not "_" in obj_name and coupling == "none":
                        test_name = test_name_TTZH
                        new_name = obj_name + "_hww"
                        print ("renaming TTVH", new_name,  obj_name)
                    elif test_name_VH in obj_name and coupling == "none":
                        test_name = test_name_VH
                        new_name = obj_name.replace("VH", "WH")
                        print ("renaming VH", new_name,  obj_name)
                    elif test_name_tHq in obj_name and not coupling == "none":
                        test_name = test_name_tHq
                        new_name = obj_name.replace("_" + coupling,"")
                        print ("renaming " +  obj_name + " to " + new_name)
                    elif test_name_tHW in obj_name and not coupling == "none":
                        test_name = test_name_tHW
                        new_name = obj_name.replace("_" + coupling,"")
                        print ("renaming " +  obj_name + " to " + new_name)
                    print ("renaming", new_name,  obj_name)

                    obj.SetName(new_name)
                    tfileout.cd(bb)
                    obj.Write()
                    ROOT.gDirectory.Delete(obj_name+";1")
                    tfileout.cd()
                if obj_name in all_procs and no_data and not "H" in obj_name :
                    if not data_obs.Integral()>0 :
                        data_obs = obj.Clone()
                    else :
                        if data_obs.Integral() > 0.01 :
                            data_obs.Add(obj.Clone())
                            print ("data_obs += " + obj_name, obj.Integral())
        if no_data :
            # make sure that the Higgs proc we take as the SM
            tfileSM = ROOT.TFile(preparedatacard, "READ")
            for signal in ["ttH", "tHq", "tHW", "ZH", "WH", "ggH", "qqH", "TTWH", "TTZH"] :
                for decay in ["hww", "htt", "hzz"] :
                    try : obj = tfileSM.Get(signal+"_"+decay)
                    except : continue
                    try : intproc = obj.Integral()
                    except : continue
                    if intproc > 0.01 :
                        data_obs.Add(obj.Clone())
                        print ("data_obs += (SM) " + obj.GetName(), obj.Integral())
            for decay in ["tttt", "zzzz", "wwww", "ttzz", "ttww", "zzww"] :
                try : obj = tfileSM.Get("HH_"+decay)
                except : continue
                try : intproc = obj.Integral()
                except : continue
                if intproc > 0.01 :
                    data_obs.Add(obj.Clone())
                    print ("data_obs += (SM) " + obj.GetName(), intproc)
            preparedatacard
            tfileout.cd(bb)
            data_obs.SetName("data_obs")
            data_obs.Write()
            tfileout.cd()
        print ("sum fake data_obs", data_obs.Integral())
        integral_data = integral_data + [data_obs.Integral()]
    tfileout.Close()
    outfile = output_file + ".txt"
    f1 = open(outfile, 'r').read()
    f2 = open(outfile, 'w')
    m = f1.replace(test_name_tHq, "tHq")
    m = m.replace(test_name_tHW, "tHW")
    #m = m.replace("VH_", "WH_")
    #m = m.replace("TTWH", "TTWH_hww")
    #m = m.replace("TTZH", "TTZH_hww")
    f2.write(m)
    f2.close()
    if no_data :
        if len(integral_data) != len(bins) :
            print ("len(integral_data) != len(bins)", len(integral_data) , len(bins))
        countobs = 0
        print ("Writting data_obs as the sum of processes")
        with open(outfile) as in_file:
            buf = in_file.readlines()
        with open(output_file + ".txt", "w") as fp:
            for cnt, line in enumerate(buf):
              fp.write(buf[cnt])
              if "shapes *" in buf[cnt] :
                countobs += 1
                #print("Line {}: {}".format(cnt, buf[cnt]))
              if "--" in line and countobs > 0 :
                  countobs = 0
                  fp.write("bin           ")
                  for bb in bins :  fp.write(bb + "   ")
                  fp.write("\n")
                  fp.write("observation   ")
                  for obs in integral_data :  fp.write( "%f   " % obs ) # round(obs,1)
                  fp.write("\n")
                  fp.write("--------------------------------------------------------------------------------\n")



def get_tH_weight_str(kt, kv, cosa = -10):
    if cosa == -10 :
        return ("kt_%.3g_kv_%.3g" % (kt, kv)).replace('.', 'p').replace('-', 'm') #.replace('kv_1', 'kv_1p0').replace('1_', '1p0_').replace('2_', '2p0_').replace('3_', '3p0_').replace('0_', '0p0_')
    else :
        return ("kt_%.3g_kv_%s_cosa_%s" % (kt, str(kv), str(cosa))).replace('.', 'p').replace('-', 'm')

def get_tH_weight_str_out(kt, kv, cosa = -10):
    if cosa == -10 :
        return ("kt_%.3g_kv_%.3gA" % (kt, kv)).replace('.', 'p').replace('-', 'm').replace('kv_1A', 'kv_1p0A').replace('_m1_', '_m1p0_').replace('_m2_', '_m2p0_').replace('_m3_', '_m3p0_').replace('_1_', '_1p0_').replace('_2_', '_2p0_').replace('_3_', '_3p0_').replace('_0_', '_0p0_').replace('_m1_', '_m1p0_').replace('_m2_', '_m2p0_').replace('_m3_', '_m3p0_')
    else :
        return ("kt_%.3g_kv_%s_cosa_%s" % (kt, str(kv), str(cosa))).replace('.', 'p').replace('-', 'm')

def get_tH_weight_str_out_clara(kt, kv, cosa = -10):
    if cosa == -10 :
        return ("ct_%.3g_cv_%.3gA" % (kt, kv)).replace('.', 'p').replace('cv_1A', 'cv_1p0A').replace('_-1_', '_-1p0_').replace('_-2_', '_-2p0_').replace('_-3_', '_-3p0_').replace('_1_', '_1p0_').replace('_2_', '_2p0_').replace('_3_', '_3p0_').replace('_0_', '_0p0_').replace('_-1_', '_-1p0_').replace('_-2_', '_-2p0_').replace('_-3_', '_-3p0_')
    else :
        return ("kt_%.3g_kv_%s_cosa_%s" % (kt, str(kv), str(cosa))).replace('.', 'p')


def make_threshold(threshold, proc_list, file_input, tH_kin) :
    tfileout = ROOT.TFile(file_input, "READ")
    proc_list_new = []
    for proc in proc_list :
        histo = tfileout.Get(proc)
        add_proc = True
        integral = -1e3
        try:
            integral = histo.Integral()
        except :
            print ("there was no process %s in the prepareDatacard" % proc )
            add_proc = False
        else:
            if integral < 0.:
                print("make_threshold: {} has negative integral: {}".format(proc, integral))
            if tH_kin and ( "tHq" in proc or "tHW" in proc ):
                if integral < threshold/10. :
                    print ("there was no sufficient yield of process %s (integral = %s)" % (proc, str(integral)) )
                    add_proc = False
            elif integral < threshold :
                print ("there was no sufficient yield of process %s (integral = %s)" % (proc, str(integral)) )
                add_proc = False
        if add_proc:
            proc_list_new.append(proc)
    return proc_list_new

# usage: file, path = splitPath(s)
def splitPath(s) :
    f = os.path.basename(s)
    p = s[:-(len(f))-1]
    return f, p

def runCombineCommand(combinecmd, card, verbose=False, outfolder=".", queue=None, submitName=None):
    if queue:
        combinecmd = combinecmd.replace('combine', 'combineTool.py')
        combinecmd += ' --job-mode lxbatch --sub-opts="-q %s"' % queue
        combinecmd += ' --task-name tHq_%s' % submitName
        # combinecmd += ' --dry-run'
    if verbose:
        print 40*'-'
        print "%s %s" % (combinecmd, card)
        print 40*'-'
    try:
        p = Popen(shlex.split(combinecmd) + [card] , stdout=PIPE, stderr=PIPE, cwd=outfolder)
        comboutput = p.communicate()[0]
    except OSError:
        print ("combine command not known\n", combinecmd)
        comboutput = None
    return comboutput

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

def run_cmd(command):
  print ("executing command = '%s'" % command)
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout

def AddSystQuad(list):
    ell = []
    for element in list : ell = ell + [math.pow(element, 2.)]
    quad =  math.sqrt(sum(ell))
    return quad

def rebin_total(template, folder, fin, divideByBinWidth, name_total, dict) :
    total_hist = fin.Get(folder+"/"+name_total)
    hist = template.Clone()
    hist.SetMarkerSize(0)
    hist.SetFillColorAlpha(12, 0.40)
    #hist.SetFillColor(1)
    #hist.SetFillStyle(3244)
    hist.SetLineWidth(0)
    hist.SetMinimum(dict["minY"])
    hist.SetMaximum(dict["maxY"])
    for ii in xrange(1, template.GetXaxis().GetNbins()+1) :
        bin_width = 1.
        if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii)
        hist.SetBinContent(ii, total_hist.GetBinContent(ii)/bin_width)
        #if ii == 6 and "2lss_0tau_3j" in channel :
        #    ## just this bin went wrong on Havester combo of processes..
        #    ## I calculated the error by hand as quadratic sum of processes -- just for this bin
        #    hist.SetBinError(ii, 4.5)
        #else :
        hist.SetBinError(ii, total_hist.GetBinError(ii)/bin_width)
    hist.GetXaxis().SetTitleOffset(0.55)
    hist.GetXaxis().SetLabelColor(10)
    if (dict["maxY"] > 1000.) : hist.GetYaxis().SetTitleOffset(1.75)
    else : hist.GetYaxis().SetTitleOffset(1.35)
    hist.GetYaxis().SetTitleSize(0.050)
    hist.GetYaxis().SetLabelSize(0.056)
    hist.GetYaxis().SetTickLength(0.04)
    hist.GetXaxis().SetTickLength(0.04)
    return hist

def rebin_totalCat(template, bins, folder, fin, divideByBinWidth, name_total) :
    hist = template.Clone()
    hist.SetMarkerSize(0)
    hist.SetFillColorAlpha(12, 0.40)
    #hist.SetFillColor(1)
    #hist.SetFillStyle(3244)
    hist.SetLineWidth(0)
    for bb, bin in enumerate(bins) :
        content = 0
        error = 0
        for cat in bin :
            print folder+cat+"/"+name_total
            takeFrom = fin.Get(folder+cat+"/"+name_total)
            err = ROOT.Double()
            content += takeFrom.IntegralAndError(0,takeFrom.GetXaxis().GetNbins()+1, err, "")
            error = AddSystQuad([error, err])
        hist.SetBinContent(bb+1, content)
        hist.SetBinError(bb+1, error)
        print ("filled bin", bb+1)
    if not hist.GetSumw2N() : hist.Sumw2()
    hist.GetXaxis().SetTitleOffset(0.55)
    hist.GetXaxis().SetLabelColor(10)
    hist.GetYaxis().SetTitleOffset(1.35)
    hist.GetYaxis().SetTitleSize(0.050)
    hist.GetYaxis().SetLabelSize(0.056)
    hist.GetYaxis().SetTickLength(0.04)
    hist.GetXaxis().SetTickLength(0.04)
    return hist

def rebin_hist(template, folder, fin, name, itemDict, divideByBinWidth, legend) :
    print folder+"/"+name
    hist = fin.Get(folder+"/"+name)
    hist_rebin = template.Clone()
    hist_rebin.SetMarkerSize(0)
    hist_rebin.SetFillColor(itemDict["color"])
    hist_rebin.SetFillStyle(itemDict["fillStype"])
    if not itemDict["label"] == "none" : legend.AddEntry(hist_rebin, itemDict["label"], "f")
    if itemDict["make border"] == True :  hist_rebin.SetLineColor(1)
    else : hist_rebin.SetLineColor(itemDict["color"])
    for ii in xrange(1, template.GetXaxis().GetNbins()+1) :
        bin_width = 1.
        if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii)
        ### remove negatives
        binContent_original = hist.GetBinContent(ii)
        binError2_original = hist.GetBinError(ii)**2
        if binContent_original < 0. :
            print ("bin with negative entry: ", binContent_original)
            binError2_modified = binError2_original + math.pow(2, binContent_original - binContent_modified)
            if not binError2_modified >= 0. : print "Bin error negative!"
            hist_rebin.SetBinError(ii, math.sqrt(binError2_modified)/bin_width)
            hist_rebin.SetBinContent(ii, 0.)
        else :
            hist_rebin.SetBinError(ii,   hist.GetBinError(ii)/bin_width)
            hist_rebin.SetBinContent(ii, hist.GetBinContent(ii)/bin_width)
    if not hist.GetSumw2N() : hist.Sumw2()
    return hist_rebin

def doCategories(template, bins, fin, name, itemDict, divideByBinWidth) :
    hist_rebin = template.Clone()
    hist_rebin.SetMarkerSize(0)
    hist_rebin.SetFillColor(itemDict["color"])
    hist_rebin.SetFillStyle(itemDict["fillStype"])
    if "none" not in itemDict["label"] : legend1.AddEntry(hist_rebin, itemDict["label"], "f")
    if itemDict["make border"] == True :  hist_rebin.SetLineColor(1)
    else : hist_rebin.SetLineColor(itemDict["fillStype"])
    for bb, bin in enumerate(bins) :
        content = 0
        for cat in bin :
            if "3l_bt" in cat and "ZZ" in name : continue
            if "3l"  in cat and "ttH_hzg" in name : continue
            if "zpeak"  in cat and "ttH_hmm" in name : continue
            if "2lss_mm" in cat and "data_flips" in name : continue
            if "2lss_mm" in cat and "Convs" in name : continue
            if "2lss_mm" in cat and "ttH_hzg" in name : continue
            if "3j" in cat and "ttH_hzg" in name : continue
            if "2lss" in cat and "ttH_hmm" in name : continue
            print folder+cat+"/"+name
            content += fin.Get(folder+cat+"/"+name).Integral()
        hist_rebin.SetBinContent(bb+1, content)
        #print ("filled bin", bb+1)
    return hist_rebin

def rebin_data(template, folder, fin, fromHavester, dict, errorBar=True) :
    # in the case errorBar=True does not draw markers,
    #in the case it is false it draws only markers but shifts the empty bins to negative
    if not fromHavester :
        dataTGraph = fin.Get(folder+"/data")
        dataTGraph1 = ROOT.TGraphAsymmErrors()
        for ii in xrange(0, template.GetXaxis().GetNbins()) :
            bin_width = 1.
            if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii+1)
            xp = ROOT.Double()
            yp = ROOT.Double()
            dataTGraph.GetPoint(ii,xp,yp)
            if errorBar :
                dataTGraph1.SetPoint(ii,       template.GetBinCenter(ii+1) , yp/bin_width)
            elif yp < 0.2 : # do not show markers for empty bins
                dataTGraph1.SetPoint(ii,       template.GetBinCenter(ii+1) , (yp  - 10.0)/bin_width)
            else :
                dataTGraph1.SetPoint(ii,       template.GetBinCenter(ii+1) , yp/bin_width)
            if errorBar :
                dataTGraph1.SetPointEYlow(ii,  dataTGraph.GetErrorYlow(ii)/bin_width)
                dataTGraph1.SetPointEYhigh(ii, dataTGraph.GetErrorYhigh(ii)/bin_width)
            dataTGraph1.SetPointEYlow(ii,  dataTGraph.GetErrorYlow(ii)/bin_width)
            dataTGraph1.SetPointEYhigh(ii, dataTGraph.GetErrorYhigh(ii)/bin_width)
            # horizontal error bars
            dataTGraph1.SetPointEXlow(ii,  template.GetBinWidth(ii+1)/2.)
            dataTGraph1.SetPointEXhigh(ii, template.GetBinWidth(ii+1)/2.)
    else :
        dataTGraph = fin.Get(folder+"/data_obs")
        dataTGraph1 = template.Clone()
        for ii in xrange(1, template.GetXaxis().GetNbins()+1) :
            bin_width = 1.
            if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii+1)
            dataTGraph1.SetBinContent(ii, dataTGraph.GetBinContent(ii)/bin_width)
            dataTGraph1.SetBinError(ii, dataTGraph.GetBinError(ii)/bin_width)
    dataTGraph1.SetMarkerColor(1)
    dataTGraph1.SetMarkerStyle(20)
    if errorBar :
        dataTGraph1.SetMarkerSize(0)
    else : dataTGraph1.SetMarkerSize(1)
    dataTGraph1.SetLineColor(1)
    dataTGraph1.SetLineWidth(2)
    dataTGraph1.SetLineStyle(1)
    dataTGraph1.SetMinimum(dict["minY"])
    dataTGraph1.SetMaximum(dict["maxY"])
    return dataTGraph1

def err_data(fin, template, folder, fromHavester, errorBar=True) :
    # in the case errorBar=True does not draw markers,
    #in the case it is false it draws only markers but shifts the empty bins to negative
    if not fromHavester :
        dataTGraph = fin.Get(folder+"/data")
        dataTGraph1 = ROOT.TGraphAsymmErrors()
        for ii in xrange(0, template.GetXaxis().GetNbins()) :
            bin_width = 1.
            if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii+1)
            dividend = template.GetBinContent(ii+1)*bin_width
            xp = ROOT.Double()
            yp = ROOT.Double()
            dataTGraph.GetPoint(ii,xp,yp)
            if 1> 0 : # yp > 0 :
                if dividend > 0 :
                    if yp < 0.2 and not errorBar :
                        dataTGraph1.SetPoint(ii, template.GetBinCenter(ii+1), yp/dividend - 0.1)
                    else :
                        dataTGraph1.SetPoint(ii, template.GetBinCenter(ii+1) , yp/dividend)
                else : dataTGraph1.SetPoint(ii, template.GetBinCenter(ii+1) , 0.0)
            if dividend > 0 and errorBar:
                dataTGraph1.SetPointEYlow(ii,  (dataTGraph.GetErrorYlow(ii))/dividend)
                dataTGraph1.SetPointEYhigh(ii, (dataTGraph.GetErrorYhigh(ii))/dividend)
            else :
                dataTGraph1.SetPointEYlow(ii,  0.0)
                dataTGraph1.SetPointEYhigh(ii, 0.0)
            dataTGraph1.SetPointEXlow(ii,  template.GetBinWidth(ii+1)/2.)
            dataTGraph1.SetPointEXhigh(ii, template.GetBinWidth(ii+1)/2.)
    else :
        dataTGraph = fin.Get(folder+"/data_obs")
        dataTGraph1 = template.Clone()
        for ii in xrange(1, template.GetXaxis().GetNbins()+1) :
            bin_width = 1.
            if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii)
            dividend = template.GetBinContent(ii)*bin_width
            if dataTGraph.GetBinContent(ii) > 0 :
              if dividend > 0 :
                dataTGraph1.SetBinContent(ii, (dataTGraph.GetBinContent(ii)/dividend))
                dataTGraph1.SetBinError(ii,    dataTGraph.GetBinError(ii)/dividend) #
            else :
                dataTGraph1.SetBinContent(ii, -0.0)
        if not dataTGraph1.GetSumw2N() : dataTGraph1.Sumw2()
    dataTGraph1.SetMarkerColor(1)
    dataTGraph1.SetMarkerStyle(20)
    if errorBar :
        dataTGraph1.SetMarkerSize(0)
    else : dataTGraph1.SetMarkerSize(1)
    dataTGraph1.SetLineWidth(2)
    dataTGraph1.SetLineColor(1)
    dataTGraph1.SetLineStyle(1)
    return dataTGraph1

def err_dataCat(template, dataTGraph, folder, fromHavester) :
    if not fromHavester :
        dataTGraph1 = ROOT.TGraphAsymmErrors()
        for ii in xrange(0, template.GetXaxis().GetNbins()) :
            bin_width = 1.
            if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii+1)
            dividend = template.GetBinContent(ii+1)*bin_width
            xp = ROOT.Double()
            yp = ROOT.Double()
            dataTGraph.GetPoint(ii,xp,yp)
            if yp > 0 :
                if dividend > 0 : dataTGraph1.SetPoint(ii, template.GetBinCenter(ii+1) , yp/dividend)
                else : dataTGraph1.SetPoint(ii, template.GetBinCenter(ii+1) , -0.7)
            else : dataTGraph1.SetPoint(ii, template.GetBinCenter(ii+1) , -0.7)
            if dividend > 0 :
                dataTGraph1.SetPointEYlow(ii,  dataTGraph.GetErrorYlow(ii)/dividend)
                dataTGraph1.SetPointEYhigh(ii, dataTGraph.GetErrorYhigh(ii)/dividend)
            else :
                dataTGraph1.SetPointEYlow(ii,  0.0)
                dataTGraph1.SetPointEYhigh(ii, 0.0)
            dataTGraph1.SetPointEXlow(ii,  template.GetBinWidth(ii+1)/2.)
            dataTGraph1.SetPointEXhigh(ii, template.GetBinWidth(ii+1)/2.)
    else :
        dataTGraph1 = template.Clone()
        for ii in xrange(1, template.GetXaxis().GetNbins()+1) :
            bin_width = 1.
            if divideByBinWidth : bin_width = template.GetXaxis().GetBinWidth(ii)
            dividend = template.GetBinContent(ii)*bin_width
            if dataTGraph.GetBinContent(ii) > 0 :
              if dividend > 0 :
                dataTGraph1.SetBinContent(ii, (dataTGraph.GetBinContent(ii)/dividend))
                dataTGraph1.SetBinError(ii,    dataTGraph.GetBinError(ii)/dividend) #
            else :
                dataTGraph1.SetBinContent(ii, -0.0)
        if not dataTGraph1.GetSumw2N() : dataTGraph1.Sumw2()
    dataTGraph1.SetMarkerColor(1)
    dataTGraph1.SetMarkerStyle(20)
    dataTGraph1.SetMarkerSize(1)
    dataTGraph1.SetLineColor(1)
    dataTGraph1.SetLineWidth(2)
    dataTGraph1.SetLineStyle(1)
    return dataTGraph1


def do_hist_total_err(fin, template, folder, labelX, name_total, category, dict) :
    total_hist = fin.Get(folder+"/"+name_total)
    hist_total_err = template.Clone()
    hist_total_err.GetYaxis().SetTitle("Data/pred.") #"#frac{Data - Expectation}{Expectation}")
    hist_total_err.GetXaxis().SetTitleOffset(1.1)
    hist_total_err.GetYaxis().SetTitleOffset(0.8)
    hist_total_err.GetXaxis().SetTitleSize(0.105)
    hist_total_err.GetYaxis().SetTitleSize(0.10)
    hist_total_err.GetYaxis().SetLabelSize(0.105)
    hist_total_err.GetXaxis().SetLabelSize(0.10)
    hist_total_err.GetYaxis().SetTickLength(0.04)
    hist_total_err.GetXaxis().SetLabelColor(1)
    hist_total_err.GetXaxis().SetTitle(labelX)
    #hist_total_err.SetMarkerSize(0)
    hist_total_err.SetFillColorAlpha(12, 0.40)
    #hist_total_err.SetFillColorAlpha(12, 0.80)
    #hist_total_err.SetFillStyle(3244)
    hist_total_err.SetLineWidth(2)
    hist_total_err.SetMarkerSize(0)
    hist_total_err.SetMinimum(dict["minYerr"])
    hist_total_err.SetMaximum(dict["maxYerr"])
    for bin in xrange(0, hist_total_err.GetXaxis().GetNbins()) :
        hist_total_err.SetBinContent(bin+1, 1)
        if total_hist.GetBinContent(bin+1) > 0. :
            if bin == 5 and "2lss_0tau" in category :
                ## just this bin went wrong on Havester combo of processes..
                ## I calculated the error by hand as quadratic sum of processes -- just for this bin
                hist_total_err.SetBinError(bin+1, 4.5/total_hist.GetBinContent(bin+1))
            else : hist_total_err.SetBinError(bin+1, total_hist.GetBinError(bin+1)/total_hist.GetBinContent(bin+1))
        else : hist_total_err.SetBinError(bin+1, 0.01)
    return hist_total_err

def do_hist_total_errCats(templatebin, bins, binlabels, labelX, name_total, category) :
    hist_total_err = template.Clone()
    hist_total_err.GetYaxis().SetTitle("Data/pred.") #"#frac{Data - Expectation}{Expectation}")
    hist_total_err.GetXaxis().SetLabelOffset(0.015)
    hist_total_err.GetYaxis().SetTitleOffset(0.8)
    hist_total_err.GetXaxis().SetTitleSize(0.105)
    hist_total_err.GetYaxis().SetTitleSize(0.10)
    hist_total_err.GetYaxis().SetLabelSize(0.105)
    hist_total_err.GetXaxis().SetLabelSize(0.15)
    hist_total_err.GetYaxis().SetTickLength(0.04)
    hist_total_err.GetXaxis().SetLabelColor(1)
    hist_total_err.GetXaxis().SetTitle("")
    hist_total_err.GetXaxis().SetNdivisions(0)
    hist_total_err.SetMarkerSize(0)
    hist_total_err.SetFillColorAlpha(12, 0.40)
    hist_total_err.SetLineWidth(2)
    hist_total_err.SetMarkerSize(0)
    minYerr = -0.6
    maxYerr = 2.85
    if "3l" in category :
        minYerr = 0.701
        maxYerr = 1.39
    if "2lss" in category :
        minYerr = 0.701
        maxYerr = 1.39
    hist_total_err.SetMinimum(minYerr)
    hist_total_err.SetMaximum(maxYerr)
    for bin in xrange(0, hist_total_err.GetXaxis().GetNbins()) :
        hist_total_err.GetXaxis().SetBinLabel(bin+1, binlabels[bin])
        hist_total_err.SetBinContent(bin+1, 1.)
        if templatebin.GetBinContent(bin+1) > 0. :
            hist_total_err.SetBinError(bin+1, templatebin.GetBinError(bin+1)/templatebin.GetBinContent(bin+1))
        else : hist_total_err.SetBinError(bin+1, 0.01)
    return hist_total_err


def addLabel_CMS_preliminary() :

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
    label_preliminary = ROOT.TPaveText(x0 + 0.1050, ypreliminary - 0.0010, x0 + 0.2950, ypreliminary + 0.0500, "NDC")
    label_preliminary.AddText("Preliminary")
    label_preliminary.SetTextFont(52)
    label_preliminary.SetTextAlign(13)
    label_preliminary.SetTextSize(0.050)
    label_preliminary.SetTextColor(1)
    label_preliminary.SetFillStyle(0)
    label_preliminary.SetBorderSize(0)
    label_luminosity = ROOT.TPaveText(xlumi, y0 + 0.0047, xlumi + 0.1900, y0 + 0.0510, "NDC")
    label_luminosity.AddText("41.5 fb^{-1} (13 TeV)")
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
    histoP.GetCumulative()
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


def rebinRegular(
    histSource,
    nbin,
    BINtype,
    originalBinning,
    doplots,
    bdtType,
    outdir,
    nQuantMax=6,
    withFolder=False,
    partialCopy=False
    ) :
    print ("rebinRegular")

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
    print ("enumerate(nbin): ",enumerate(nbin), ", nbin: ",nbin)
    isMoreThan02 = 0
    bin_isMoreThan02 = 0
    for nn,nbins in enumerate(nbin) :
        print ("\n\nnn: ",nn,", nbins: ",nbins)
        file = TFile(histSource+".root","READ");
        file.cd()
        histograms=[]
        histograms2=[]
        h2 = TH1F()
        hSum = TH1F()
        hFakes = TH1F()
        hSumAll = TH1F()
        ratiohSum=1.
        ratiohSumP=1.
        ### rebin and  write the histograms
        if BINtype=="none" : name=histSource+"_"+str(nbins)+"bins_none.root"
        if BINtype=="regular" or options.BINtype == "mTauTauVis": name=histSource+"_"+str(nbins)+"bins.root"
        if BINtype=="ranged" : name=histSource+"_"+str(nbins)+"bins_ranged.root"
        if BINtype=="quantiles" : name=histSource+"_"+str(nbins)+"bins_quantiles.root"
        fileOut  = TFile(name, "recreate");
        if withFolder : folders_Loop = file.GetListOfKeys()
        else : folders_Loop = ["none"]
        for nkey, keyF in enumerate(folders_Loop) :
            print ("nkey: ",nkey,", keyF: ",keyF)
            if withFolder :
                if partialCopy :
                    if str(source) not in str(keyF.GetName()) : continue
                obj =  keyF.ReadObj()
                loop_on = obj.GetListOfKeys()
                histograms=[]
                histograms2=[]
                h2 = TH1F()
                hSum = TH1F()
                hFakes = TH1F()
                hSumAll = TH1F()
                ratiohSum=1.
                ratiohSumP=1.
            else :
                loop_on = file.GetListOfKeys()
            print ("withFolder", withFolder)
            for keyO in loop_on :
               # print ( keyF.GetName(), keyO.GetName() )
               #
               if not withFolder :
                   #print "got histogram"
                   obj = keyO.ReadObj()
                   if type(obj) is not TH1F : continue
                   h2  = obj.Clone()
                   #print h2.GetName()
               else : h2 = file.Get(keyF.GetName()+"/"+str(keyO.GetName())).Clone()
               factor=1.
               if  not h2.GetSumw2N() : h2.Sumw2()
               if  not hSum.GetSumw2N() : hSum.Sumw2()
               if withFolder : h2.SetName("x_"+str(h2.GetName()))
               histograms.append(h2.Clone())
               print ("h2.Integral:", h2.Integral())
               if "fakes_data" in h2.GetName() : hFakes=h2.Clone()
               if "fakes_data" in h2.GetName() : hFakes=h2.Clone()
               if h2.GetName().find("H") ==-1 and h2.GetName().find("hh") ==-1 and h2.GetName().find("signal") ==-1 and h2.GetName().find("data_obs") ==-1 :
                   print ("quantiles in ", h2.GetName())
                   if not hSumAll.Integral()>0 :
                       hSumAll=h2.Clone()
                       hSumAll.SetName("hSumAllBk1")
                   else : hSumAll.Add(h2)
            #################################################
            #print ("hSumAll.Integral: ", hSumAll.Integral(), ", hFakes.Integral: ",hFakes.Integral())
            nbinsQuant =  getQuantiles(hSumAll,nbins,xmax) ## nbins+1 if first quantile is zero ## getQuantiles(hFakes,nbins,xmax) #
            #print ("Bins by quantiles ",nbins,nbinsQuant)
            if withFolder: fileOut.mkdir(keyF.GetName()+"/")
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
                if BINtype=="none" :
                    histo=histogramCopy.Clone()
                    histo.SetName(nameHisto)
                elif BINtype=="ranged" or BINtype=="regular" :
                    histo= TH1F( nameHisto, nameHisto , nbins , xmin , xmax)
                elif BINtype=="quantiles" :
                    nbinsQuant= getQuantiles(hSumAll,nbins,xmax) # getQuantiles(hSumAll,nbins,xmax) ## nbins+1 if first quantile is zero
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
                if "fakes_data" in histo.GetName() and nkey == 0 :
                    ratio=1.
                    ratioP=1.
                    hTTi=histo.Clone()
                    hTTi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                    if histo.GetBinContent(histo.GetNbinsX()) >0 : ratio=histo.GetBinError(histo.GetNbinsX())/histo.GetBinContent(histo.GetNbinsX())
                    if histo.GetBinContent(histo.GetNbinsX()-1) >0 : ratioP=histo.GetBinError(histo.GetNbinsX()-1)/histo.GetBinContent(histo.GetNbinsX()-1)
                    errOcontTTLast=errOcontTTLast+[ratio] if ratio<1.01 else errOcontTTLast+[1.0]
                    errOcontTTPLast=errOcontTTPLast+[ratioP] if ratioP<1.01 else errOcontTTPLast+[1.0]
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
            print (name+" created")
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
                errOcontSUMLast=errOcontSUMLast+[ratiohSum] if ratiohSum<1.001 else errOcontSUMLast+[1.0]
                errOcontSUMPLast=errOcontSUMPLast+[ratiohSumP] if ratiohSumP<1.001 else errOcontSUMPLast+[1.0]
                errSUMLast=errSUMLast+[hSumi.GetBinError(hSumi.GetNbinsX())]
                contSUMLast=contSUMLast+[hSumi.GetBinContent(hSumi.GetNbinsX())]
                if ratiohSum > 0.199 or nbins > nQuantMax :
                    isMoreThan02 = isMoreThan02 + 1
                    if isMoreThan02 == 1 :
                        bin_isMoreThan02 = nbins
                fileOut.cd()
                hSumCopy.Write()
                hSumi.Write()
                if BINtype=="quantiles" :
                    print ("nbins: ",nbins)
                    print ("nbinsQuant: ",nbinsQuant)
                    lastQuant=lastQuant+[nbinsQuant[nbins]]   # original
                    xmaxQuant=xmaxQuant+[xmaxdef]
                    xminQuant=xminQuant+[xmindef]
                print ("it should be only one ",  nkey, errOcontTTLast)
    print ("min",xmindef,xmin)
    print ("max",xmaxdef,xmax)
    print ("isMoreThan02", isMoreThan02, bin_isMoreThan02)
    return [errOcontTTLast,errOcontTTPLast,errOcontSUMLast,errOcontSUMPLast,lastQuant,xmaxQuant,xminQuant, bin_isMoreThan02]

def ReadLimits(bdtType,nbin, BINtype,channel,local,nstart,ntarget, sendToCondor):
    print ("ReadLimits:: bdtType: ",bdtType,", nbin:",nbin,", BINtype: ",BINtype,", channel: ",channel,", local: ",local,", ",nstart,", ntarget: ",ntarget)
    central=[]
    do1=[]
    do2=[]
    up1=[]
    up2=[]
    for nn,nbins in enumerate(nbin) :
        # ttH_2lss_1taumvaOutput_2lss_MEM_1D_nbin_9.log
        if nstart==-1 : shapeVariable=bdtType
        elif nstart==0 :
            if channel in ["4l_0tau", "2lss_1tau", "2l_2tau", "1l_2tau", "1l_1tau", "3l_1tau", "3l_0tau", "0l_2tau", "2los_1tau"] and not sendToCondor:
                shapeVariable=bdtType+'_'+str(nbins)+"bins" # 'datacard_'+
            elif channel in [ "0l_2tau"]:
                #print ("read", bdtType+'_'+str(nbins)+"bins_"+BINtype)
                shapeVariable=bdtType+'_'+str(nbins)+"bins_"+BINtype
            elif channel in [ "2l_0tau", "1l_0tau"]:
                #print ("read", bdtType+'_'+str(nbins)+"bins_"+BINtype)
                shapeVariable=bdtType+'_'+str(nbins)+"bins_mod"
            else :
                shapeVariable=options.variables+'_'+bdtType+'_nbin_'+str(nbins)
        elif nstart==1 : shapeVariable=options.variables+'_'+str(nbins)+'bins'
        else : shapeVariable=options.variables+'_from'+str(nstart)+'_to_'+str(nbins)
        #if BINtype=="ranged" : shapeVariable=shapeVariable+"_ranged"
        #if BINtype=="quantiles" : shapeVariable=shapeVariable+"_quantiles"
        #print ("shapeVariable = ", shapeVariable)
        if channel in [ "0l_2tau"] and sendToCondor :
            #mvaOutput_0l_2tau_deeptauVTight_9bins_regular.3502010.0.out
            datacardFile_output = glob.glob(os.path.join(local, "%s*.out" % (shapeVariable)))[0]
            #print("read", glob.glob(os.path.join(local, "%s*.out" % (shapeVariable))))
        else :
            #datacardFile_output = os.path.join(local, "%s.log" % (shapeVariable))
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
        #print (shapeVariable, nbins,central)
    #print (shapeVariable,nbin)
    #print (shapeVariable,central)
    #print do1
    return [central,do1,do2,up1,up2]


###########################################################
# doYields



def PrintTables(cmb, uargs, filey, unblinded, labels, typeChannel, ColapseCat = []):

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
        if not unblinded :
            bottom = bottom + r' \multicolumn{2}{c|}{$-$} '
        else : bottom = bottom + r' \multicolumn{2}{c|}{$%g$} ' % (c_cat[ll].cp().GetObservedRate())
        if ll == len(labels) - 1 : bottom = bottom + r' \\'
        else : bottom = bottom + ' &'
    header = header +"} \n"
    bottom = bottom +"\n"
    filey.write(header)

    if typeChannel == 'tau' :
        conversions = "conversions"
        flips = 'flips'
        fakes_data = 'fakes_data'

        filey.write(r"""
        \hline
        Process & \multicolumn{2}{c|}{$1\Plepton + 2\tauh$} & \multicolumn{2}{c|}{$2\Plepton + 2\tauh$} & \multicolumn{2}{c|}{$3\Plepton + 1\tauh$} & \multicolumn{2}{c|}{$2\Plepton ss + 1\tauh$} \\
        \hline
        \hline"""+"\n")

    if typeChannel == 'multilep2lss' :
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

    if typeChannel == 'multilepCR2lss' :
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

    if typeChannel == 'multilepCR3l4l' :
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

    if typeChannel == 'multilep3l4l' :
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

    if 'multilep' in typeChannel :
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

    if typeChannel == 'tau' :
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
    if typeChannel == 'tau' : singleCompMC = singleCompMC + ['EWK']
    singleCompMC = singleCompMC + [
        'TTZ',
        fakes_data,
        conversions,
        flips,
        'Rares'
    ]

    singleCompMClabels = []
    if typeChannel == 'tau' : singleCompMClabels = singleCompMClabels + ['$\PW\cPZ + \cPZ\cPZ$']
    singleCompMClabels = singleCompMClabels + [
        '$\cPqt\cPaqt\cPZ$',
        'Misidentified',
        'Conversions',
        'signal flip',
        'Other'
    ]

    if typeChannel == 'tau' : listTosum = [signals, TTWX, tH]
    if 'multilep' in typeChannel : listTosum = [signals, TTWX, tH, EWK]
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


def setTDRStyle():
  tdrStyle =  ROOT.TStyle("tdrStyle","Style for P-TDR")

   #for the canvas:
  tdrStyle.SetCanvasBorderMode(0)
  tdrStyle.SetCanvasColor(ROOT.kWhite)
  tdrStyle.SetCanvasDefH(600) #Height of canvas
  tdrStyle.SetCanvasDefW(600) #Width of canvas
  tdrStyle.SetCanvasDefX(0)   #POsition on screen
  tdrStyle.SetCanvasDefY(0)


  tdrStyle.SetPadBorderMode(0)
  #tdrStyle.SetPadBorderSize(Width_t size = 1)
  tdrStyle.SetPadColor(ROOT.kWhite)
  tdrStyle.SetPadGridX(False)
  tdrStyle.SetPadGridY(False)
  tdrStyle.SetGridColor(0)
  tdrStyle.SetGridStyle(3)
  tdrStyle.SetGridWidth(1)

#For the frame:
  tdrStyle.SetFrameBorderMode(0)
  tdrStyle.SetFrameBorderSize(1)
  tdrStyle.SetFrameFillColor(0)
  tdrStyle.SetFrameFillStyle(0)
  tdrStyle.SetFrameLineColor(1)
  tdrStyle.SetFrameLineStyle(1)
  tdrStyle.SetFrameLineWidth(1)

#For the histo:
  #tdrStyle.SetHistFillColor(1)
  #tdrStyle.SetHistFillStyle(0)
  tdrStyle.SetHistLineColor(1)
  tdrStyle.SetHistLineStyle(0)
  tdrStyle.SetHistLineWidth(1)
  #tdrStyle.SetLegoInnerR(Float_t rad = 0.5)
  #tdrStyle.SetNumberContours(Int_t number = 20)

  tdrStyle.SetEndErrorSize(2)
  #tdrStyle.SetErrorMarker(20)
  #tdrStyle.SetErrorX(0.)

  tdrStyle.SetMarkerStyle(20)

#For the fit/function:
  tdrStyle.SetOptFit(1)
  tdrStyle.SetFitFormat("5.4g")
  tdrStyle.SetFuncColor(2)
  tdrStyle.SetFuncStyle(1)
  tdrStyle.SetFuncWidth(1)

#For the date:
  tdrStyle.SetOptDate(0)
  # tdrStyle.SetDateX(Float_t x = 0.01)
  # tdrStyle.SetDateY(Float_t y = 0.01)

# For the statistics box:
  tdrStyle.SetOptFile(0)
  tdrStyle.SetOptStat(0) # To display the mean and RMS:   SetOptStat("mr")
  tdrStyle.SetStatColor(ROOT.kWhite)
  tdrStyle.SetStatFont(42)
  tdrStyle.SetStatFontSize(0.025)
  tdrStyle.SetStatTextColor(1)
  tdrStyle.SetStatFormat("6.4g")
  tdrStyle.SetStatBorderSize(1)
  tdrStyle.SetStatH(0.1)
  tdrStyle.SetStatW(0.15)
  # tdrStyle.SetStatStyle(Style_t style = 1001)
  # tdrStyle.SetStatX(Float_t x = 0)
  # tdrStyle.SetStatY(Float_t y = 0)

# Margins:
  tdrStyle.SetPadTopMargin(0.05)
  tdrStyle.SetPadBottomMargin(0.13)
  tdrStyle.SetPadLeftMargin(0.16)
  tdrStyle.SetPadRightMargin(0.02)

# For the Global title:

  tdrStyle.SetOptTitle(0)
  tdrStyle.SetTitleFont(42)
  tdrStyle.SetTitleColor(1)
  tdrStyle.SetTitleTextColor(1)
  tdrStyle.SetTitleFillColor(10)
  tdrStyle.SetTitleFontSize(0.05)
  # tdrStyle.SetTitleH(0) # Set the height of the title box
  # tdrStyle.SetTitleW(0) # Set the width of the title box
  # tdrStyle.SetTitleX(0) # Set the position of the title box
  # tdrStyle.SetTitleY(0.985) # Set the position of the title box
  # tdrStyle.SetTitleStyle(Style_t style = 1001)
  # tdrStyle.SetTitleBorderSize(2)

# For the axis titles:

  tdrStyle.SetTitleColor(1, "XYZ")
  tdrStyle.SetTitleFont(42, "XYZ")
  tdrStyle.SetTitleSize(0.06, "XYZ")
  # tdrStyle.SetTitleXSize(Float_t size = 0.02) # Another way to set the size?
  # tdrStyle.SetTitleYSize(Float_t size = 0.02)
  tdrStyle.SetTitleXOffset(0.9)
  tdrStyle.SetTitleYOffset(1.25)
  # tdrStyle.SetTitleOffset(1.1, "Y") # Another way to set the Offset

# For the axis labels:

  tdrStyle.SetLabelColor(1, "XYZ")
  tdrStyle.SetLabelFont(42, "XYZ")
  tdrStyle.SetLabelOffset(0.007, "XYZ")
  tdrStyle.SetLabelSize(0.05, "XYZ")

# For the axis:

  tdrStyle.SetAxisColor(1, "XYZ")
  tdrStyle.SetStripDecimals(True)
  tdrStyle.SetTickLength(0.03, "XYZ")
  tdrStyle.SetNdivisions(510, "XYZ")
  tdrStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
  tdrStyle.SetPadTickY(1)

# Change for log plots:
  tdrStyle.SetOptLogx(0)
  tdrStyle.SetOptLogy(0)
  tdrStyle.SetOptLogz(0)

# Postscript options:
  tdrStyle.SetPaperSize(20.,20.)
  # tdrStyle.SetLineScalePS(Float_t scale = 3)
  # tdrStyle.SetLineStyleString(Int_t i, const char* text)
  # tdrStyle.SetHeaderPS(const char* header)
  # tdrStyle.SetTitlePS(const char* pstitle)

  # tdrStyle.SetBarOffset(Float_t baroff = 0.5)
  # tdrStyle.SetBarWidth(Float_t barwidth = 0.5)
  # tdrStyle.SetPaintTextFormat(const char* format = "g")
  # tdrStyle.SetPalette(Int_t ncolors = 0, Int_t* colors = 0)
  # tdrStyle.SetTimeOffset(Double_t toffset)
  # tdrStyle.SetHistMinimumZero(kTRUE)

  tdrStyle.SetHatchesLineWidth(5)
  tdrStyle.SetHatchesSpacing(0.05)

  tdrStyle.cd()
