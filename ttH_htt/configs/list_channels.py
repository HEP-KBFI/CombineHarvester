def list_channels(analysis, fake_mc) :
    if analysis == "ttH" :
        sigs = ["ttH", "tHq", "tHW", "WH", "ZH", "ggH", "qqH" ] # , "TTWH", "TTZH",
        decays = ["_hww", "_hzz", "_htt", "_hzg", "_hmm" ]
        decays_hh = ["_tttt", "_zzzz", "_wwww", "_ttzz", "_ttww", "_zzww"  ]
        higgs_procs = [ [y + x  for x in decays if not (x in ["hzg", "hmm"] and y != "ttH")] for y in sigs]
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
            "isSMCSplit" : False
        },
        "4lctrl" : {
            "bkg_proc_from_data" : [ fakes  , flips  ],
            "bkg_procs_from_MC"  : ["TTW", "TTWW", "TTZ", "Rares", conversions, "WZ", "ZZ"],
            "isSMCSplit" : False
        },
        "3lctrl" : {
            "bkg_proc_from_data" : [ fakes  , flips  ],
            "bkg_procs_from_MC"  : ["TTW", "TTWW", "TTZ", "Rares", conversions, "WZ", "ZZ"],
            "isSMCSplit" : False
        },
        "2lss_1tau" : {
            "bkg_proc_from_data" : [ fakes , flips ], #
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", conversions],
            "isSMCSplit" : True
            },
        "3l_0tau"   : {
            "bkg_proc_from_data" : [ fakes  ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", "EWK", conversions],
            "isSMCSplit" : False
        },
        "1l_2tau"   : {
            "bkg_proc_from_data" : [ fakes       ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ"],
            "isSMCSplit" : False
            },
        "2l_2tau"   : {
            "bkg_proc_from_data" : [ fakes       ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ"],
            "isSMCSplit" : False
            },
        "3l_1tau"   : {
            "bkg_proc_from_data" : [ fakes, flips   ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", conversions],
            "isSMCSplit" : True
            },
        "2los_1tau" : {
            "bkg_proc_from_data" : [ fakes, flips   ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", conversions],
            "isSMCSplit" : False
        },
        "0l_2tau"   : {
            "bkg_proc_from_data" : [ fakes      ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", "DY", "TT"],
            "isSMCSplit" : False
            },
        "1l_1tau"   : {
            "bkg_proc_from_data" : [ fakes      ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", "DY", "TT"],
            "isSMCSplit" : False
            },
        "4l_0tau"   : {
            "bkg_proc_from_data" : [ fakes, flips   ],
            "bkg_procs_from_MC"  : [ "TTW", "TTWW", "TTZ", "Rares", "WZ", "ZZ", conversions, "TT"],
            "isSMCSplit" : False
        }        }
    else : sys.exit("analysis " + analysis + " not implemented")
    return {
        "higgs_procs"      : higgs_procs,
        "decays"           : decays,
        "decays_hh"        : decays_hh,
        "info_bkg_channel" : info_channel
    }
