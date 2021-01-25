### everthing that is marked as "uncorrelated" is renamed as:
### "CMS_ttHl" ->  "CMS_ttHl%s" % str(era).replace("20","")
### where era = 2016/2017/2018

# syst: theory and from MC generators - taken correlated between all years (check if that is what we want to do)
lumiSyst             = {2016: 1.022,          2017: 1.020,          2018: 1.015}
lumi_2016_2017_2018  = {2016: 1.009,          2017: 1.008,          2018: 1.020}
lumi_2017_2018       = {2017: 1.003,          2018: 1.004}
lumi_13TeV_BCC       = {2017: 1.003,          2018: 1.002}
lumi_2016_2017       = {2016: 1.008,          2017: 1.006}
lumi_13TeV_DB        = {2016: 1.005,          2017: 1.005}
lumi_13TeV_GS        = {2016: 1.004,          2017: 1.001}

vbf_dipole_ln_Syst = {
    "0l_4tau" : {"wwww": 1.,   "ttww":1.94, "tttt":0.93, "zzww":1.,    "ttzz":1.,    "zzzz":1.},
    "1l_3tau" : {"wwww": 1.,   "ttww":0.87, "tttt":0.9,  "zzww":1.,    "ttzz":0.83,  "zzzz":1.},
    "2lss" :    {"wwww": 1.23, "ttww":1.47, "tttt":1.58, "zzww":1.33,  "ttzz":1.67,  "zzzz":1.},
    "2l_2tau" : {"wwww": 1.08, "ttww":1.,   "tttt":0.94, "zzww":2.8,   "ttzz":1.32,  "zzzz":1.},
    "3l" :      {"wwww": 0.99, "ttww":1.04, "tttt":1.07, "zzww":0.94,  "ttzz":1.07,  "zzzz":2.22},
    "3l_1tau" : {"wwww": 0.8,  "ttww":0.96, "tttt":0.86, "zzww":2.65,  "ttzz":1.59,  "zzzz":1.},
    "4l" :      {"wwww": 1.41, "ttww":0.82, "tttt":0.7,  "zzww":0.71,  "ttzz":2.08,  "zzzz":1.}
}


theory_ln_Syst = {
    #https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO
    "QCDscale_ttjets"             : {"value": (0.965 , 1.024),    "proc" : ["TT"]},
    "pdf_ttjets"                  : {"value": 1.042,               "proc" : ["TT"]}, # includes alpha s
    "TopmassUnc_ttjets"           : {"value": 0.973/1.028,               "proc" : ["TT"]},

#https://arxiv.org/pdf/1610.07922.pdf
    "QCDscale_ttZ"                : {"value": (0.887 , 1.096),    "proc" : ["TTZ"]},
    "QCDscale_ttW"                : {"value": (0.885 , 1.129),    "proc" : ["TTW"]},

    "pdf_ttZ"                     : {"value": 1.04,              "proc" : ["TTZ"]},  # includes alpha s 
    "pdf_ttW"                     : {"value": 1.034,               "proc" : ["TTW"]},  
  
    "EW_ttZ"                      : {"value": (0.998,1.0),               "proc" : ["TTZ"]},  
    "EW_ttW"                      : {"value": (0.968,1.0),               "proc" : ["TTW"]},  

    #HH https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHXSWGHH#Current_recommendations_for_HH_c modify scale for coupling?
    "pdf_ggHH"                      : {"value": 1.021,               "proc" : ["ggHH"]},
    "QCDscale_ggHH"                 : {"value": (0.95 , 1.022),     "proc" : ["ggHH"]},
    "alfa_s_ggHH"                    : {"value": 1.021,              "proc" : ["ggHH"]},
    "TopmassUnc_ggHH"               : {"value": 1.026,              "proc" : ["ggHH"]},
    "pdf_qqHH"                      : {"value": 1.021,               "proc" : ["qqHH"]}, # includes alpha s
    "QCDscale_qqHH"                 : {"value": (0.996 , 1.003),     "proc" : ["qqHH"]},
    # higgs https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageAt13TeV (mh = 125.09)
    "alfa_s_ggH"                    : {"value": 1.025,              "proc" : ["ggH"]},
    "pdf_ggH"                     : {"value": 1.018,              "proc" : ["ggH"]},
    "QCDscale_ggH"                : {"value": (0.924 , 1.081),    "proc" : ["ggH"]},

    "pdf_qqH"                     : {"value": 1.021,              "proc" : ["qqH"]},
    "QCDscale_qqH"                : {"value": (0.96 , 1.03),      "proc" : ["qqH"]},
    "alfa_s_qqH"                    : {"value": 1.005,              "proc" : ["qqH"]},

    "QCDscale_WH"                 : {"value": (0.95 , 1.07),      "proc" : ["WH"]},
    "pdf_WH"                      : {"value": 1.017,              "proc" : ["WH"]},
    "alfa_s_WH"                    : {"value": 1.009,              "proc" : ["WH"]},
    "QCDscale_ZH"                 : {"value": (0.962 , 1.03),    "proc" : ["ZH"]},
    "pdf_ZH"                      : {"value": 1.013,              "proc" : ["ZH"]},
    "alfa_s_ZH"                    : {"value": 1.009,              "proc" : ["ZH"]},

    "QCDscale_ttH"                : {"value": (0.908 , 1.058),    "proc" : ["TTH","ttH"]},
    "pdf_ttH"               : {"value": 1.03,              "proc" : ["TTH","ttH"]},
    "alfa_s_ttH"                    : {"value": 1.02,              "proc" : ["TTH","ttH"]},

    "QCDscale_tHq"                : {"value": (0.853, 1.065),     "proc" : ["tHq"]},
    "pdf_tHq"                      : {"value": 1.035,               "proc" : ["tHq"]},
    "alfa_s_tHq"                    : {"value": 1.012,              "proc" : ["tHq"]},

    "QCDscale_tHW"                : {"value": (0.933, 1.049),     "proc" : ["tHW"]},
    "pdf_tHW"                    : {"value": 1.063,              "proc" : ["tHW"]},
    "alfa_s_tHW"                    : {"value": 1.015,              "proc" : ["tHW"]}, 
#Andrew
    "pdf_ggZZ"                      : {"value": (0.823/1.236),              "proc" : ["ggZZ"]},
    "QCDscale_ggZZ"                 : {"value": 1.173,              "proc" : ["ggZZ"]},
    "pdf_qqZZ"                      : {"value": (0.9868/1.0208),              "proc" : ["qqZZ"]},
    #"EW_corr_ggZZ"                 : {"value": 1.,              "proc" : ["ggZZ"]}, # ?
    "QCDscale_qqZZ"                 : {"value": 1.0314,              "proc" : ["qqZZ"]},
   # "EW_corr_qqZZ"                 : {"value": 1.,              "proc" : ["qqZZ"]},# ?
    "pdf_WZ"                      : {"value": (0.967/1.038),              "proc" : ["WZ"]},
    "QCDscale_WZ"                 : {"value": 1.014,              "proc" : ["WZ"]},
# other WZ/ZZ

    "CMS_WZ_theo"            : {"value": 1.07,               "proc" : ["WZ"]},
    }

## --- BR(H->XX)/BR_sm(H->XX) = (kappa_X)^2 -------------------------------------------------------------- ##
## --- Rel. Unc. on BR(H->XX) = dBR(H->XX)/BR(H->XX) = 2 * d(kappa_X)/kappa_X ---------------------------- ##
## --- Measured kappa_X values used below taken from Run-1 coupling combination (HIG-15-002) ------------- ##
## --- Table-17 (B_bsm = 0 case, "ATLAS+CMS measured" column) in HIG-15-002-paper-v14.pdf ---------------- ##
## --- In cases where 1-sigma intervals are given, we take mid-point of the interval compatible with SM -- ##
## --- as the central value --- ##
higgsBR_exptl = {
    "hww" : 1.26, # kappa_W is 0.87 (+0.13) (-0.09) -> Expt. Unc. on H->WW BR: 2*sqrt(((0.149)^2 + (0.103)^2)/2) = 2*0.128 = 26%
    "hzz" : 1.18, # kappa_Z = 1.035 +0.095 -0.095 -> Expt. Unc. on H->ZZ BR: 2*sqrt(((0.091)^2 + (0.091)^2)/2) =  2*0.091 = 18%
    "htt" : 1.31, # kappa_tau = 0.84 (+0.15)(-0.11) -> Expt. Unc. on H->tautau BR: 2*sqrt(((0.178)^2 + (0.131)^2)/2) = 2*0.156 = 31%
    "hzg" : 1.0,  # Not observed yet but upper bounds available
    "hmm" : 1.0,  # Not observed yet but upper bounds available
    "hbb" : 1.89, # kappa_b = 0.49 (+0.27)(-0.15) -> Expt. Unc. on H->bb BR: 2*sqrt(((0.550)^2 + (0.306)^2)/2) = 2*0.445 = 89%
    "tttt" : 1.0330,
    "zzzz" : 1.0308,
    "wwww" : 1.0308,
    "wwzz" : 1.0308,
    "ttzz" : 1.0319,
    "ttww" : 1.0319,
    "hwwhww": 1.0308,
    "htthww": 1.0319,
    "hzzhww": 1.0308,
    "hzzhzz": 1.0308,
    "htthtt": 1.0330,
    "htthzz": 1.0319
}

## --- Values taken from LHCHXWG TWiki: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBR
higgsBR_theo = {
    "hww" : 1.0154,
    "hzz" : 1.0154,
    "htt" : 1.0165,
    "hzg" : 1.0582,
    "hmm" : 1.0168,
    "hbb" : 1.0126,
    "tttt" : 1.0330,
    "zzzz" : 1.0308,
    "wwww" : 1.0308,
    "wwzz" : 1.0308,
    "ttzz" : 1.0319,
    "ttww" : 1.0319,
    "hwwhww": 1.0308,
    "htthww": 1.0319,
    "hzzhww": 1.0308,
    "hzzhzz": 1.0308,
    "htthtt":1.0330, 
    "htthzz": 1.0319
}

################################################
# syst specific to processes

def specific_syst(analysis, list_channel_opt, channel="multilepton") :
    channel = channel.replace('bbWW', 'bbww')
    if analysis == "HH" :
        ttH_procs = ["ttH_htt", "ttH_hww", "ttH_hzz", "ttH_hzg", "ttH_hzz"]
        tH_procs = ["tH_htt", "tH_hww", "tH_hzz"]
        tHq_procs = ["tHq_htt", "tHq_hww", "tHq_hzz"]
        tHW_procs = ["tHW_htt", "tHW_hww", "tHW_hzz"]
        specific_ln_systs = {
            "CMS_fakes"            : {"value" : 1.3,  "correlated"   : True,  "renameTo" : "CMS_%s_fakes" %channel, "proc" : ["%s_data_fakes"%channel],          "channels" : [k for k,v in list_channel_opt.items() if "data_fakes"  in v["bkg_proc_from_data"]]},  # for channels with "fakes_data"
            "CMS_multilepton_FakeableID_lnU"   : {"value" : 1.5,  "correlated"   : True,  "proc" : ["%s_data_fakes"%channel],           "channels" : ["1l_3tau", "3l_1tau"]},  #For channels with small changes to the tau selection not properly treated in the fake rate extraction 
            "CMS_multilepton_QF"               : {"value" : 1.3,  "correlated"   : True,  "renameTo" : None, "proc" : ["%s_data_flips"%channel],          "channels" : [k for k,v in list_channel_opt.items() if "data_flips"  in v["bkg_proc_from_data"]]},  # for channels with "flips_data"
            "CMS_Convs"            : {"value" : 1.5,  "correlated"   : True,  "proc" : ["%s_Convs"%channel], "renameTo" : "CMS_%s_Convs"%channel, "channels" : [k for k,v in list_channel_opt.items() if "Convs" in v["bkg_procs_from_MC"]]},   # for channels with "conversions"
            "CMS_Other"           : {"value" : 1.5,  "correlated"   : True, "renameTo" : "CMS_%s_Other"%channel, "proc" : ["%s_Other"%channel],                  "channels" : [k for k,v in list_channel_opt.items() if "Other" in v["bkg_procs_from_MC"]]},            # for channels with WZ
        }
        ## if it is uncorrelated and the name or renameTo contains "CMS_ttHl_" leave it (a 16/17/18 will be added just after ttHl), if not add an "Era" where the year should be (2016/2017/2018 will replace "Era")
        specific_shape = {
            # ##################################### JER splitted -> not needed
            # "CMS_ttHl_JERBarrel"        : {"correlated" : False, "renameTo" : "CMS_JER_Barrel_Era"        ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # "CMS_ttHl_JEREndcap1"       : {"correlated" : False, "renameTo" : "CMS_JER_Endcap1_Era"       ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # "CMS_ttHl_JEREndcap2LowPt"  : {"correlated" : False, "renameTo" : "CMS_JER_Endcap2lowpt_Era"  ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # "CMS_ttHl_JEREndcap2HighPt" : {"correlated" : False, "renameTo" : "CMS_JER_Endcap2highpt_Era" ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # "CMS_ttHl_JERForwardLowPt"  : {"correlated" : False, "renameTo" : "CMS_JER_Forwardlowpt_Era"  ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # "CMS_ttHl_JERForwardHighPt" : {"correlated" : False, "renameTo" : "CMS_JER_Forwardhighpt_Era" ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # #####################################
            # ################################### trigger
            "CMS_ttHl_trigger"          : {"correlated" : False, "renameTo" : "CMS_%s_trigger_Era" %channel, "proc" : "MCproc"                 , "channels" : [n for n in list(list_channel_opt.keys()) if not ("2lss" in n)]}, # uncorrelate by channel as well, that renaming is done on the main code
            ## CMS_ttHl16_trigger_ee/em/mm
            "CMS_ttHl_trigger_2lssEE"   : {"correlated" : False, "renameTo" : "CMS_%s_trigger_ee_Era" %channel,  "proc" : "MCproc"                 , "channels" : [n for n in list(list_channel_opt.keys()) if ("2lss" in n)]},
            "CMS_ttHl_trigger_2lssEMu"  : {"correlated" : False, "renameTo" : "CMS_multilepton_trigger_em_Era"   ,  "proc" : "MCproc"                 , "channels" : [n for n in list(list_channel_opt.keys()) if ("2lss" in n)]},
            "CMS_ttHl_trigger_2lssMuMu" : {"correlated" : False, "renameTo" : "CMS_multilepton_trigger_mm_Era"    ,  "proc" : "MCproc"                 , "channels" : [n for n in list(list_channel_opt.keys()) if ("2lss" in n)]},
            "CMS_ttHl_l1PreFire"        : {"correlated" : False, "renameTo" : "CMS_%s_prefireProbability_Era" %channel ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())}, # should be 2016/2017 not 2018, that is done on the main code
            # ################################### btag
            "CMS_ttHl_btag_HFStats1" : {"correlated" : False, "renameTo" : "CMS_btag_hfstats1_Era"     ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_btag_HFStats2" : {"correlated" : False, "renameTo" : "CMS_btag_hfstats2_Era"     ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_btag_LFStats1" : {"correlated" : False, "renameTo" : "CMS_btag_lfstats1_Era",  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_btag_LFStats2" : {"correlated" : False, "renameTo" : "CMS_btag_lfstats2_Era",  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_btag_HF"       : {"correlated" : False, "renameTo" : "CMS_btag_HF_Era_Era"            ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_btag_LF"       : {"correlated" : False, "renameTo" : "CMS_btag_LF_Era"            ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_btag_cErr1"    : {"correlated" : False, "renameTo" : "CMS_btag_cErr1_Era"         ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_btag_cErr2"    : {"correlated" : False, "renameTo" : "CMS_btag_cErr2_Era"         ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # ################################# JER + JES
            "CMS_ttHl_JER"                  : {"correlated" : False, "renameTo" : "CMS_JER_Era"         ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # #### JEC_regrouped
            ## corr part
            #"CMS_ttHl_JES"          : {"correlated" : True, "renameTo" : "CMS_JES"   ,  "proc" : "MCproc"                 , "channels" : ["3l"]},
            "CMS_ttHl_JESAbsolute"          : {"correlated" : True, "renameTo" : "CMS_JES_Abs"   ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_JESBBEC1"             : {"correlated" : True, "renameTo" : "CMS_JES_BBEC1"      ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_JESEC2"               : {"correlated" : True, "renameTo" : "CMS_JES_EC2"        ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_JESFlavorQCD"         : {"correlated" : True, "renameTo" : "CMS_JES_FlavQCD"  ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_JESHF"                : {"correlated" : True, "renameTo" : "CMS_JES_HF"         ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_JESRelativeBal"       : {"correlated" : True, "renameTo" : "CMS_JES_RelBal",  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # ## uncorr part
            "CMS_ttHl_JESAbsolute_Era"       : {"correlated" : False, "renameTo" : "CMS_JES_Abs_Era"      ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_JESBBEC1_Era"          : {"correlated" : False, "renameTo" : "CMS_JES_BBEC1_Era"         ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_JESEC2_Era"            : {"correlated" : False, "renameTo" : "CMS_JES_EC2_Era"           ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_JESRelativeSample_Era" : {"correlated" : False, "renameTo" : "CMS_JES_RelSample_Era",  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_JESHF_Era"             : {"correlated" : False, "renameTo" : "CMS_JES_HF_Era"            ,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            # ############################## Lepton efficency:
            "CMS_ttHl_lepEff_elloose"       : {"correlated" : True, "renameTo" : "CMS_%s_eff_eloose" %channel,  "proc" : "MCproc"                 , "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            "CMS_ttHl_lepEff_eltight"       : {"correlated" : True, "renameTo" : "CMS_%s_eff_etight" %channel,  "proc" : "MCproc"                 , "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            "CMS_ttHl_lepEff_mutight"       : {"correlated" : True, "renameTo" : "CMS_%s_eff_mtight" %channel,  "proc" : "MCproc"                 , "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            "CMS_ttHl_lepEff_muloose"       : {"correlated" : True, "renameTo" : "CMS_%s_eff_mloose" %channel,  "proc" : "MCproc"                 , "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            # ############################## Tau related:
            "CMS_ttHl_tauIDSF"              : {"correlated" : False, "renameTo" : "CMS_%s_eff_t_Era" %channel, "proc" : "MCproc"                 , "channels" :  list(set(list(list_channel_opt.keys())) - set(["4l", "3l", "2lss", "ZZCR", "WZCR", "1l_0tau", "2l_0tau"]))},
            "CMS_ttHl_tauES"                : {"correlated" : False, "renameTo" : "CMS_%s_scale_t_Era" %channel, "proc" : "MCproc"                 , "channels" : list(set(list(list_channel_opt.keys())) - set(["4l", "3l", "2lss", "ZZCR", "WZCR"]))},
            # ########################### FakeRate:
            "CMS_ttHl_FRe_shape_pt"         : {"correlated" : True, "renameTo" : "CMS_%s_FakeRate_e_pt" %channel , "proc" : ["data_fakes"%schannel], "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            "CMS_ttHl_FRe_shape_norm"       : {"correlated" : True, "renameTo" : "CMS_%s_FakeRate_e_norm" %channel, "proc" : ["data_fakes"%schannel], "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            "CMS_ttHl_FRe_shape_eta_barrel" : {"correlated" : True, "renameTo" : "CMS_%s_FakeRate_e_be" %channel  , "proc" : ["data_fakes"%schannel], "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            "CMS_ttHl_FRm_shape_pt"         : {"correlated" : True, "renameTo" : "CMS_%s_FakeRate_m_pt" %channel , "proc" : ["data_fakes"%schannel], "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            "CMS_ttHl_FRm_shape_norm"       : {"correlated" : True, "renameTo" : "CMS_%s_FakeRate_m_norm" %channel, "proc" : ["data_fakes"%schannel], "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            "CMS_ttHl_FRm_shape_eta_barrel" : {"correlated" : True, "renameTo" : "CMS_%s_FakeRate_m_be" %channel, "proc" : ["data_fakes"%schannel], "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))},
            "CMS_ttHl_FRjt_norm"            : {"correlated" : False, "renameTo" :"CMS_%s_FakeRate_jt_norm" %channel, "proc" : ["data_fakes"%schannel], "channels" : list(set(list(list_channel_opt.keys())) - set(["4l", "3l", "2lss", "ZZCR", "WZCR", "1l_0tau", "2l_0tau"]))},
            "CMS_ttHl_FRjt_shape"           : {"correlated" : False, "renameTo" : "CMS_multilepton_FakeRate_jt_shape" , "proc" : ["data_fakes"%schannel], "channels" : list(set(list(list_channel_opt.keys())) - set(["4l", "3l", "2lss", "ZZCR", "WZCR", "1l_0tau", "2l_0tau"]))},
            "CMS_ttHl_FRet_shift"           : {"correlated" : False, "renameTo" : "CMS_multilepton_FakeRate_et_shift", "proc" : ["data_fakes"%schannel], "channels" : list(set(list(list_channel_opt.keys())) - set(["4l", "3l", "2lss", "ZZCR", "WZCR", "1l_0tau", "2l_0tau"]))},
            # ################# other
            "CMS_ttHl_topPtReweighting"     : {"correlated" : True, "renameTo" : "CMS_%s_topPtReweighting" %channel, "proc" : ["TT"], "channels" : ["3l", "WZCR", "1l_0tau", "2l_0tau"]},
            "CMS_ttHl_UnclusteredEn"        : {"correlated" : True, "renameTo" : "CMS_%s_UnclusteredEn" %channel,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            "CMS_ttHl_pileup"               : {"correlated" : True, "renameTo" : "CMS_%s_pileup" %channel,  "proc" : "MCproc"                 , "channels" : list(list_channel_opt.keys())},
            
            "CMS_ttHl_PS_TT_ISR"   : {"correlated" : True, "renameTo" : "CMS_%s_PS_TT_ISR" %channel, "proc" : ["TT"], "channels" : ["3l", "WZCR", "1l_0tau", "2l_0tau"]},
            "CMS_ttHl_PS_TT_FSR"   : {"correlated" : True, "renameTo" : "CMS_%s_PS_TT_FSR" %channel, "proc" : ["TT"], "channels" : ["3l", "WZCR", "1l_0tau", "2l_0tau"]},
            "CMS_ttHl_JESHEM"       : {"correlated" : True,  "renameTo" : None  , "proc" : "MCproc"      , "channels" : list(set(list(list_channel_opt.keys())) - set(["3l", "1l_0tau", "2l_0tau"]))}, # only for 2018 -- that is set on the Writedatacards # Saswati: it is removed for bb1l as up histogram is absent
           # "CMS_ttHl_EWK_btag"     : {"correlated" : True, "renameTo" : "CMS_multilepton_EWK_btag"   , "proc" : ["WZ"], "channels" : list(set(list(list_channel_opt.keys())) - set(["0l_4tau"]))}, 
           # "CMS_ttHl_EWK_jet"      : {"correlated" : True, "renameTo" : "CMS_multilepton_EWK_jet"   , "proc" : ["WZ"], "channels" : [k for k,v in list_channel_opt.items() if "WZ" in v["bkg_procs_from_MC"] or "ZZ" in v["bkg_procs_from_MC"]]}, ## added only on SRs atm 

            # ######## theory
            "CMS_ttHl_thu_shape_ttH"     : {"correlated" : True, "renameTo" : "CMS_%s_thu_shape_ttH" %channel, "proc" : ttH_procs, "channels" : [k for k,v in list_channel_opt.items() if any(i in v["bkg_procs_from_MC"] for i in ttH_procs)]},
            "CMS_ttHl_thu_shape_tHq"     : {"correlated" : True, "renameTo" : "CMS_%s_thu_shape_tHq" %channel, "proc" : tHq_procs, "channels" : [k for k,v in list_channel_opt.items() if any(i in v["bkg_procs_from_MC"] for i in tHq_procs)]},
            "CMS_ttHl_thu_shape_tHW"     : {"correlated" : True, "renameTo" : "CMS_%s_thu_shape_tHW" %channel, "proc" : tHW_procs, "channels" : [k for k,v in list_channel_opt.items() if any(i in v["bkg_procs_from_MC"] for i in tHW_procs)]},
            "CMS_ttHl_thu_shape_ttW"     : {"correlated" : True, "renameTo" : "CMS_%s_thu_shape_ttW" %channel, "proc" : ["TTW", "TTWW"], "channels" : [k for k,v in list_channel_opt.items() if "TTW" in v["bkg_procs_from_MC"]]},
            "CMS_ttHl_thu_shape_ttZ"     : {"correlated" : True, "renameTo" : "CMS_%s_thu_shape_ttZ" %channel, "proc" : ["TTZ"], "channels" : [k for k,v in list_channel_opt.items() if "TTZ" in v["bkg_procs_from_MC"]]},
            #"CMS_ttHl_thu_shape_HH"      : {"correlated" : True, "renameTo" : "CMS_%s_thu_shape_ggHH" %channel, "proc" : ["ggHH"], "channels" : list(list_channel_opt.keys())}, #niot working for LO or Res, done for NLO in the inference FW
            "CMS_ttHl_thu_shape_DY"      : {"correlated" : True, "renameTo" : "CMS_%s_thu_shape_DY" %channel, "proc" : ["DY"], "channels" : [k for k,v in list_channel_opt.items() if "DY" in v["bkg_procs_from_MC"]]},
            "CMS_ttHl_thu_shape_TT"      : {"correlated" : True, "renameTo" : "CMS_%s_thu_shape_TT" %channel, "proc" : ["TT"], "channels" : [k for k,v in list_channel_opt.items() if "TT" in v["bkg_procs_from_MC"]]},
            "CMS_ttHl_thu_shape_WZ"      : {"correlated" : True, "renameTo" : "CMS_%s_thu_shape_WZ" %channel, "proc" : ["WZ"], "channels" : [k for k,v in list_channel_opt.items() if "WZ" in v["bkg_procs_from_MC"]]},
            #"CMS_ttHl_thu_shape_ggZZ"      : {"correlated" : True, "renameTo" : "CMS_multilepton_thu_shape_ggZZ", "proc" : ["ggZZ"], "channels" : [k for k,v in list_channel_opt.items() if "ggZZ" in v["bkg_procs_from_MC"]]}, not working?
            "CMS_ttHl_thu_shape_qqZZ"      : {"correlated" : True, "renameTo" : "CMS_multilepton_thu_shape_ggZZ", "proc" : ["qqZZ"], "channels" : [k for k,v in list_channel_opt.items() if "qqZZ" in v["bkg_procs_from_MC"]]},
            # ##################################### MC closure
            "CMS_ttHl_Clos_e_shape" : {"correlated" : False, "renameTo" : "CMS_%s_Clos_e_shape" %channel, "proc" : ["data_fakes"%schannel], "channels" : ["3l","2lss", "WZCR", "1l_0tau", "2l_0tau", "ZZCR"]}, 
            
            "CMS_ttHl_Clos_m_shape" : {"correlated" : False, "renameTo" : "CMS_%s_Clos_m_shape" %channel , "proc" : ["data_fakes"%schannel], "channels" : ["3l","2lss", "WZCR", "1l_0tau", "2l_0tau", "ZZCR"]},
            #"CMS_ttHl_Clos_t_shape" : {"correlated" : False, "renameTo" : "CMS_multilepton_Clos_t_shape"  , "proc" : ["data_fakes"%schannel], "channels" : list(list_channel_opt.keys())]}, #MCClosure not used for any channel containing taus
            "CMS_ttHl_Clos_e_norm"  : {"correlated" : True, "renameTo" : "CMS_%s_Clos_e_norm" %channel, "proc" : ["data_fakes"%schannel], "channels" : ["3l","2lss", "WZCR", "WZCR", "1l_0tau", "2l_0tau", "ZZCR"]},
            "CMS_ttHl_Clos_m_norm"  : {"correlated" : True, "renameTo" : "CMS_%s_Clos_m_norm"%channel  , "proc" : ["data_fakes"%schannel], "channels" : ["3l","2lss", "WZCR", "1l_0tau", "2l_0tau", "ZZCR"]},
        #     "CMS_ttHl_Clos_t_norm"  : {"correlated" : False, "renameTo" : None  , "proc" : ["data_fakes"%schannel], "channels" : [n for n in list(list_channel_opt.keys()) if ("1tau" in n or "2tau" in n) and not ("2lss_1tau" in n or "3l_1tau" in n) ]}, #MCClosure not used for any channel containing taus
        }
        specific_ln_shape_systs = {
            ##"CMS_eff_t"             : {"value" : 1.05, "correlated" : True,  "type" : "gentau" , "channels" : [k for k,v in list_channel_opt.items() if v["isSMCSplit"]]},  # only for gentau
            #"CMS_ttHl_FRjtMC_shape" : {"value" : 1.3,  "correlated" : True,  "type" : "faketau", "channels" : [k for k,v in list_channel_opt.items() if v["isSMCSplit"]]},  # only for fake tau. was:
        }
        specific_shape_shape_systs = {
 #           "CMS_ttHl_FRjt_norm"  : {"correlated" : False, "type" : "faketau"},  ## only for faketau
 #           "CMS_ttHl_FRjt_shape" : {"correlated" : False, "type" : "faketau"},  ## only for faketau
 #           "CMS_ttHl_tauIDSF"    : {"correlated" : False, "type" : "gentau"},  ## only for faketau
 #           "CMS_ttHl_tauES"      : {"correlated" : False, "type" : "gentau"},  ## only for faketau
        }

        created_shape_to_shape_syst = {
  #      "CMS_constructed_ttHl_FRjt_norm",
  #      "CMS_constructed_ttHl_FRjt_shape",
  #      "CMS_constructed_ttHl_tauIDSF",
  #      "CMS_constructed_ttHl_tauES"
        }

    else : sys.exit("analysis " + analysis + " not implemented")
    return {
        "specific_ln_systs"             : specific_ln_systs,
        "specific_shape"                : specific_shape,
        "specific_ln_to_shape_systs"    : specific_ln_shape_systs,
        "specific_shape_to_shape_systs" : specific_shape_shape_systs,
        "created_shape_to_shape_syst"   : created_shape_to_shape_syst
    }
