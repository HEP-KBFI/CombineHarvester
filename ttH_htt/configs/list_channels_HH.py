def list_channels( fake_mc, signal_type="none", mass="none", HHtype="none", renamedHHInput=False ) :
    #####################
    # signal_type = "noresLO" | "nonresNLO" | "res"
    # mass nonres = "cHHH1" | cHHH... || "SM", "BM12", "kl_1p00"... || "spin0_900",....
    # HHtype = "bbWW" | "multilepton"
    #####################
    sigs = ["ttH", "tHq", "tHW", "WH", "ZH", "ggH", "qqH" ]
    decays = ["_hww", "_hzz", "_htt", "_hzg", "_hmm" ]
    # FIXME ---> to be used when the cards are done with Higs processes in Physics model
    # naming convention and separating by branching ratio
    # by now it will look for them (eg ttH_hww) in the prepareDatacards and not find
    decays_hh = []
    decays_hh_vbf = []
    if renamedHHInput :
        if "bbWW" in HHtype:
            decays_hh = ["hbbhww", "hbbhtt", "hbbhzz"]
            decays_hh_vbf = ["hbbhtt", "hbbhww", 'hbbhzz']
        elif HHtype == "multilepton" :
            decays_hh = ["hwwhww","htthww","hzzhww","hzzhzz","htthtt","htthzz"]
            decays_hh_vbf = ["hwwhww","htthww","hzzhww","hzzhzz","htthzz","htthtt"] # "htautauhtautau"
            
        elif HHtype == "bbWW_bbtt" :
            decays_hh = ["hbb_htt"]
            decays_hh_vbf = ["hbb_htt"]
        elif HHtype == "bbWW_SL" :
            decays_hh = ["SL_hbb_hww"]
            decays_hh_vbf = []
        elif HHtype == "bbWW_DL" :
            decays_hh = ["DL_hbb_hww"]
            decays_hh_vbf = []
        else :
            print("HHtype (%s) not implemented" % ( HHtype))
            sys.exit()
    else :
        if "bbWW" in HHtype:
            decays_hh = ["bbww", "bbtt", "bbzz"]
        elif HHtype == "multilepton" :
            decays_hh = ["wwww","ttww", "tttt", "ttzz", "zzww", "zzzz"]
        elif HHtype == "bbWW_SL" :
            decays_hh = ["bbvv_sl"]
        elif HHtype == "bbWW_DL" :
            decays_hh = ["bbvv"]
        else :
            print("HHtype (%s) not implemented" % ( HHtype))
            sys.exit()

    #---> by now not used, we may use to implement systematics/BR -- see how decays_hh is used in WriteDatacards
    #higgs_procs = [ [y + x  for x in decays if not (x in ["hzg", "hmm"] and y != "ttH")] for y in sigs]
    higgs_procs = [ [y + x  for x in decays if not (x in ["hzg", "hmm"])] for y in sigs]

    prefix_VBF = "signal_vbf_nonresonant"
    SM_VBF     = "1_1_1"
    prefix_GF  = "signal_ggf_nonresonant"
    couplings_GF_NLO = [ "cHHH0", "cHHH1", "cHHH5", "cHHH2p45" ]
    couplings_VBF    = [ "1_1_1", "1_1_2", "1_2_1", "1_1_0", "1p5_1_1", "0p5_1_1", "1_0_1" ]
    if renamedHHInput :
        prefix_VBF = "qqHH"
        SM_VBF     = "CV_1_C2V_1_kl_1"
        prefix_GF  = "ggHH"
        #couplings_GF_NLO = [ "kl_0_kt_1", "kl_1_kt_1", "kl_5_kt_1" ]
        couplings_GF_NLO = [ "kl_1_kt_1", "kl_2p45_kt_1", "kl_5_kt_1", "kl_0_kt_1" ]
        # --> using "cHHH2p45" as control -- check closure to see if this is the best case
        couplings_VBF    = [ "CV_1_C2V_1_kl_1", "CV_1_C2V_1_kl_2", "CV_1_C2V_2_kl_1",  "CV_1_C2V_1_kl_0", "CV_1p5_C2V_1_kl_1", "CV_0p5_C2V_1_kl_1", "CV_1_C2V_0_kl_1" ]

    if signal_type == "nonresLO" :
        listSig = []
        for decay_hh in decays_hh :
            listSig = listSig + [
            "%s_%s"  % (prefix_GF, decay_hh),
            #"%s_%s_hh_%s" % (prefix_VBF, SM_VBF, decay_hh)
            ]
        sigs = [ listSig ]
    elif signal_type == "nonresNLO" :
        listSig = []
        for decay_hh in decays_hh :
            for massType in couplings_GF_NLO :
                listSig = listSig + [ "%s_%s_%s" % (prefix_GF, massType , decay_hh) ]
        for decay_hh in decays_hh_vbf :
            for massType in couplings_VBF :
                listSig = listSig + [ "%s_%s_%s" % (prefix_VBF, massType, decay_hh) ]
        sigs = [ listSig ]
    elif signal_type == "res" :
        listSig = []
        for decay_hh in decays_hh :
            listSig = listSig + [ "signal_ggf_%s_%s" % (mass, decay_hh) ]
        sigs = [ listSig ]
    else :
        print("signal_type %s not implemented" % (signal_type))
        sys.exit()
    # FIXME ---> add VBF to nonres case (SM by default)
    # FIXME ---> add multilep options
    ######################
    ## the bellow would be if all the single h processes with all booked decay modes in the definition of higgs_procs are in the inputs
    #higgs_procs = higgs_procs + sigs
    #higgs_proc_no_BR = []
    ## the bellow would be if some list of single h processes with decay modes and correct naming convention are in the inputs
    #higgs_procs = sigs + [["ttH_hww", "tHW_hww", "WH_hww"]]
    #higgs_proc_no_BR = []
    ## the bellow would be if some list of single h processes with decay modes and correct naming convention are in the inputs, but higgs_proc_no_BR is
    higgs_procs_w_BR = []
    higgs_proc_no_BR = ["ttH", "tHq","tHW", "WH","ZH","qqH", "ggH"]
    for proc in higgs_proc_no_BR:
        higgs_procs_w_BR.append(proc+"_hww")
        higgs_procs_w_BR.append(proc+"_hzz")
        higgs_procs_w_BR.append(proc+"_htt")
        higgs_procs_w_BR.append(proc+"_hbb")
        higgs_procs_w_BR.append(proc+"_hgg")
    thprocs_bbww = ["TH_hww","TH_hzz","TH_htt","TH_hbb","TH_hgg"]
    
    higgs_procs = sigs

    conversions = "Convs"
    if fake_mc :
        fakes       = "fakes_mc"
        flips       = "flips_mc"
    else :
        fakes       = "Fakes"
        flips       = "data_flips"

    info_channel = {
        "2l_0tau" : {
            "bkg_proc_from_data" : [ fakes    ],
            "bkg_procs_from_MC"  : ["TT", "ST", "Other_bbWW", "DY", "WJets", "VV"] + higgs_procs_w_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "1l_0tau" : {
            "bkg_proc_from_data" : [ fakes    ],
            "bkg_procs_from_MC"  : ["TT", "ST", "Other_bbWW", "DY", "WJets", "VV"] + higgs_procs_w_BR + thprocs_bbww,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "0l_4tau" : {
            "bkg_proc_from_data" : [ 'multilepton_' + fakes    ],
            "bkg_procs_from_MC"  : ["multilepton_Convs", "TTZ", "TTW", "TTWW", "TT", "multilepton_Other", "DY", "W", "WW", "WZ", "ggZZ","qqZZ"] + higgs_procs_w_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "1l_3tau" : {
            "bkg_proc_from_data" : [ 'multilepton_' + fakes    ],
            "bkg_procs_from_MC"  : ["multilepton_Convs", "TTZ", "TTW", "TTWW", "TT", "multilepton_Other", "DY", "W", "WW", "WZ", "ggZZ","qqZZ"] + higgs_procs_w_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "2lss" : {
            "bkg_proc_from_data" : [ 'multilepton_' + fakes , 'multilepton_' + flips],
            "bkg_procs_from_MC"  : ["multilepton_Convs", "TTZ", "TTW", "TTWW", "TT", "multilepton_Other", "DY", "W", "WW", "WZ", "ggZZ","qqZZ"] + higgs_procs_w_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "2l_2tau" : {
            "bkg_proc_from_data" : [ 'multilepton_' + fakes    ],
            "bkg_procs_from_MC"  : ["multilepton_Convs", "TTZ", "TTW", "TTWW", "TT", "multilepton_Other", "DY", "W", "WW", "WZ", "ggZZ","qqZZ"] + higgs_procs_w_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "3l" : {
            "bkg_proc_from_data" : [ 'multilepton_' + fakes    ],
            "bkg_procs_from_MC"  : ["multilepton_Convs", "TTZ", "TTW", "TTWW", "TT", "multilepton_Other", "DY", "W", "WW", "WZ", "ggZZ","qqZZ"] + higgs_procs_w_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "3l_1tau" : {
            "bkg_proc_from_data" : [ 'multilepton_' + fakes    ],
            "bkg_procs_from_MC"  : ["multilepton_Convs", "TTZ", "TTW", "TTWW", "TT", "multilepton_Other", "DY", "W", "WW", "WZ", "ZZ", "ggZZ", "qqZZ"] + higgs_procs_w_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "4l" : {
            "bkg_proc_from_data" : [ 'multilepton_' + fakes    ],
            "bkg_procs_from_MC"  : ["multilepton_Convs", "TTZ", "TTW", "TTWW", "TT", "multilepton_Other", "DY", "W", "WW", "WZ", "ggZZ","qqZZ"] + higgs_procs_w_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "WZCR" : {
            "bkg_proc_from_data" : [ 'multilepton_' + fakes    ],
            "bkg_procs_from_MC"  : ["multilepton_Convs", "TTZ", "TTW", "TTWW", "TT", "multilepton_Other", "DY", "W", "WW", "WZ", "ggZZ","qqZZ"] + higgs_proc_no_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "ZZCR" : {
            "bkg_proc_from_data" : [ 'multilepton_' + fakes    ],
            "bkg_procs_from_MC"  : ["multilepton_Convs", "TTZ", "TTW", "TTWW", "TT", "multilepton_Other", "DY", "W", "WW", "WZ", "ggZZ","qqZZ"] + higgs_proc_no_BR,
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        }


    }
    #---> by now "TTH", "TH" and "VH" are automatically marked as BKG
    return {
        "higgs_procs"      : sigs,
        "decays"           : [],
        "decays_hh"        : decays_hh,
        "info_bkg_channel" : info_channel,
        "higgs_procs_to_draw"      : sigs[0],
    }
