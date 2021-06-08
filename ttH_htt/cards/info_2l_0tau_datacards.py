def read_from(in_more_subcats, BDTfor):
    withFolderL = True
    label  = "hh_bb1l_26Jul_baseline_TTSL_noWjj_dataMC"

    if in_more_subcats == "resolved_2b_vbf" :
        bdtTypes = [
            "BDT_resolved_2b_vbf_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "resolved_2b_nonvbf" :
        bdtTypes = [
            "BDT_resolved_2b_nonvbf_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "resolved_1b" :
        bdtTypes = [
            "BDT_resolved_1b_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "boosted" :
        bdtTypes = [
            "BDT_boosted_OS_disabled_MVAOutput_%s" %BDTfor,
        ]

    elif in_more_subcats == "HH_boosted" :
        bdtTypes = [
            "LBN_HH_boosted_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "HH_boosted_vbf" :
        bdtTypes = [
            "LBN_HH_boosted_vbf_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "HH_boosted_nonvbf" :
        bdtTypes = [
            "LBN_HH_boosted_nonvbf_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "HH_resolved_2b_nonvbf" :
        bdtTypes = [
            "LBN_HH_resolved_2b_nonvbf_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "HH_resolved_1b" :
        bdtTypes = [
            "LBN_HH_resolved_1b_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "HH_resolved_2b_vbf" :
        bdtTypes = [
            "LBN_HH_resolved_2b_vbf_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "HH_resolved_1b" :
        bdtTypes = [
            "LBN_HH_resolved_1b_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "HH_resolved_1b_vbf" :
        bdtTypes = [
            "LBN_HH_resolved_1b_vbf_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "HH_resolved_1b_nonvbf" :
        bdtTypes = [
            "LBN_HH_resolved_1b_nonvbf_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "TT_boosted" :
        bdtTypes = [
            "LBN_TT_boosted_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "TT_resolved" :
        bdtTypes = [
            "LBN_TT_resolved_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "W_resolved" :
        bdtTypes = [
            "LBN_W_resolved_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "SingleTop_resolved" :
        bdtTypes = [
            "LBN_SingleTop_resolved_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "DY_resolved" :
        bdtTypes = [
            "LBN_DY_resolved_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "Other" :
        bdtTypes = [
            "LBN_Other_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "W_boosted" :
        bdtTypes = [
            "LBN_W_boosted_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "SingleTop_boosted" :
        bdtTypes = [
            "LBN_SingleTop_boosted_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "DY_boosted" :
        bdtTypes = [
            "LBN_DY_boosted_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
    elif in_more_subcats == "boosted" :
        bdtTypes = [
            "BDT_boosted_OS_disabled_MVAOutput_%s" %BDTfor,
        ]
        
    channelsTypes = [ "2l_0tau" ]
    ch_nickname = "hh_bb2l"

    originalBinning=100
    nbinRegular = np.arange(15, 22)
    nbinQuant = np.arange(20, 21, 1)

    maxlim = 2.0
    minlim = 0.0

    output = {
    "withFolder"      : withFolderL,
    "label"           : label,
    "bdtTypes"        : bdtTypes,
    "channelsTypes"   : channelsTypes,
    "originalBinning" : originalBinning,
    "nbinRegular"     : nbinRegular,
    "nbinQuant"       : nbinQuant,
    "maxlim"          : maxlim,
    "minlim"          : minlim,
    "ch_nickname"     : ch_nickname,
        "makePlotsBin"    : []
    }

    return output
