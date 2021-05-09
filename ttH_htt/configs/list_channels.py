def list_channels(analysis, fake_mc) :
    if analysis == "ttH" :
        sigs = ["ttH", "tHq", "tHW", "WH", "ZH", "ggH", "qqH" ] # , "TTWH", "TTZH",
        decays = ["_hww", "_hzz", "_htt", "_hzg", "_hmm" ]
        decays_hh = ["_tttt", "_zzzz", "_wwww", "_ttzz", "_ttww", "_zzww"  ]
        higgs_procs = [ [y + x  for x in decays if not (x in ["_hzg", "_hmm"] and y != "ttH")] for y in sigs]
        higgs_procs = higgs_procs + [["HH" + x  for x in decays_hh]]
        conversions = "Convs"
        #print (higgs_procs)
        if fake_mc :
            fakes       = "fakes_mc"
            flips       = "flips_mc"
        else :
            fakes       = "data_fakes"
            flips       = "data_flips"

        info_channel = {
        "2lss_0tau" : {
            "bkg_proc_from_data" : [ fakes  , flips  ],
            "bkg_procs_from_MC"  : ["TTW", "TTWW", "TTZ", "Rares", conversions, "WZ", "ZZ"],
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "4lctrl" : {
            "bkg_proc_from_data" : [ fakes  , flips  ],
            "bkg_procs_from_MC"  : ["TTW", "TTWW", "TTZ", "Rares", conversions, "WZ", "ZZ"],
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "3lctrl" : {
            "bkg_proc_from_data" : [ fakes  , flips  ],
            "bkg_procs_from_MC"  : ["TTW", "TTWW", "TTZ", "Rares", conversions, "WZ", "ZZ"],
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "2lss_1tau_rest" : {
            "bkg_proc_from_data" : [ fakes , flips ], #
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", "Convs"],
            "isSMCSplit" : True,
            "proc_to_remove" : {
                "2018" : ["WH_hww"],
            }
            },
        "2lss_1tau_tH" : {
            "bkg_proc_from_data" : [ fakes , flips ], #
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", "Convs"],
            "isSMCSplit" : True,
            "proc_to_remove" : {
                "2018" : ["WH_hww", "WH_htt"]
            }
            },
        "2lss_1tau_ttH" : {
            "bkg_proc_from_data" : [ fakes , flips ], #
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", "Convs"],
            "isSMCSplit" : True,
            "proc_to_remove" : {}
            },
        "3l_0tau"   : {
            "bkg_proc_from_data" : [ fakes  ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", "EWK", conversions],
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "1l_2tau"   : {
            "bkg_proc_from_data" : [ fakes       ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ"],
            "isSMCSplit" : False,
            "proc_to_remove" :
                {
                "2016" : ["tHq_htt", "ttH_hww", "ttH_hzz", "TTWW", "WH_htt", "ZH_htt", "ZH_hww"],
                "2017" : ["ZH_htt", "HH_ttww", "tHq_htt", "tHW_htt", "ttH_hww", "ttH_hzz", "TTWW", "WH_htt", ],
                "2018" : ["ggH_hzz", "tHq_htt", "tHW_hww", "ttH_hww", "ttH_hzz", "ZH_htt", "ZH_hww"]

                }
            },
        "2l_2tau"   : {
            "bkg_proc_from_data" : [ fakes       ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ"],
            "isSMCSplit" : False,
            "proc_to_remove" : {
            "2016" : ["ttH_hww", "tHW_htt", "TTWW", "Rares", "ZZ"],
            "2017" : ["ttH_hzz", "TTWW"],
            "2018" : []

            }
            },
        "3l_1tau"   : {
            "bkg_proc_from_data" : [ fakes, flips   ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", conversions],
            "isSMCSplit" : True,
            "proc_to_remove" : {}
            },
        "2los_1tau" : {
            "bkg_proc_from_data" : [ fakes, flips   ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", conversions],
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "0l_2tau"   : {
            "bkg_proc_from_data" : [ fakes      ],
            "bkg_procs_from_MC"  : [ "TTW", "TTZ", "Rares", "WZ", "ZZ", "DY", "TT"], # "TTWW",
            "isSMCSplit" : False,
            "proc_to_remove" :
            {
                "2018" : ["ggH_hww", "ggH_hzz", "ZH_hww", "WH_htt", "ttH_hzz", "ttH_hww", "TTW", "TTWW"], #
                "2017" : ["ggH_hzz", "ttH_hzz", "ttH_hww", "ttH_hzg", "HH_tttt", "TTW", "TTWW"],
                "2016" : ["ggH_hww", "WH_htt", "ZH_htt", "ZH_hww", "ZH_hzz", "HH_tttt", "HH_ttww", "HH_ttzz", "ttH_hzg", "ttH_hzz", "TTW", "TTWW"]
            }
            },
        "1l_1tau"   : {
            "bkg_proc_from_data" : [ fakes      ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", "DY", "TT"],
            "isSMCSplit" : False,
            "proc_to_remove" : {
            "2018" : ["ggH_hzz", "ggH_hww", "qqH_hww", "qqH_hzz", "tHq_hzz",  "ttH_hmm", "ttH_hzg", "WH_hww", "WH_hzz", "ZH_htt", "ZH_hww", "ZH_hzz", ], #
            "2017" : ["ggH_hzz", "ggH_hww", "qqH_hww", "HH_tttt", "HH_ttww", "HH_ttzz", "tHq_hzz", "tHW_hzz", "ttH_hzg", "WH_htt", "WH_hww", "WH_hzz", "ZH_hww", "ZH_hzz"],
            "2016" : ["ggH_hww", "qqH_hww", "tHq_hww", "tHq_hzz",  "tHq_hzz", "ttH_hmm", "ttH_hzg", "WH_htt", "WH_hzz" , "ZH_htt", "ZH_hww", "ZH_hzz",  "HH_tttt", "HH_ttww", "HH_ttzz"]
            }
            },
        "4l_0tau"   : {
            "bkg_proc_from_data" : [ fakes, flips   ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", conversions, "TT"],
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        }
        }
    elif analysis == "HH" :
        #sigs = [["signal_ggf_nonresonant_cHHH1_hh_bbtt", "signal_ggf_nonresonant_cHHH1_hh_bbvv_sl", "signal_ggf_nonresonant_cHHH1_hh_bbvv"]]
        #sigs = [["signal_ggf_nonresonant_hh_bbttSM", "signal_ggf_nonresonant_hh_bbvv_slSM", "signal_ggf_nonresonant_hh_bbvvSM" ]]
        #sigs = [["signal_ggf_nonresonant_hh_bbttBM12", "signal_ggf_nonresonant_hh_bbvv_slBM12", "signal_ggf_nonresonant_hh_bbvvBM12" ]]
        sigs = [["signal_ggf_spin0_900_hh_bbtt", "signal_ggf_spin0_900_hh_bbvv", "signal_ggf_spin0_900_hh_bbvv_sl"]]
        #sigs = [["signal_ggf_nonresonant_hh_bbttkl_1p00", "signal_ggf_nonresonant_hh_bbvv_slkl_1p00", "signal_ggf_nonresonant_hh_bbvvkl_1p00"]]
        higgs_procs = sigs
        conversions = "Convs"
        #print (higgs_procs)
        if fake_mc :
            fakes       = "fakes_mc"
            flips       = "flips_mc"
        else :
            fakes       = "data_fakes"
            flips       = "data_flips"

        info_channel = {
        "2l_0tau" : {
            "bkg_proc_from_data" : [ fakes    ],
            "bkg_procs_from_MC"  : ["Convs", "TTH", "TH", "TTZ", "TTW", "TTWW", "TT", "Other", "VH", "DY", "W", "WW", "WZ", "ZZ"],
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        },
        "1l_0tau" : {
            "bkg_proc_from_data" : [ fakes    ],
            "bkg_procs_from_MC"  : ["Convs", "TTH", "TH", "TTZ", "TTW", "TTWW", "TT", "Other", "VH", "DY", "W", "WW", "WZ", "ZZ"],
            "isSMCSplit" : False,
            "proc_to_remove" : {}
        }
        }
        decays = []
        decays_hh = []

    else : sys.exit("analysis " + analysis + " not implemented")
    return {
        "higgs_procs"      : higgs_procs,
        "decays"           : decays,
        "decays_hh"        : decays_hh,
        "info_bkg_channel" : info_channel
    }
