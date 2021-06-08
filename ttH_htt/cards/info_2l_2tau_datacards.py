def read_from():

    withFolder = False
    label = "2l_2tau_central_deepVSjVLoose_veto_master_cards_2019Oct10_2017"
    mom="/afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/deeptauWPS/"+label+"/prepareDatacards/"
    bdtTypes = [
    "mva_2l_2tau",
    #"mTauTauVis"
    ]

    channelsTypes = [ "2l_2tau" ]
    ch_nickname = "2l_2tau_lepdisabled_taudisabled_sumOS"

    originalBinning=100
    nbinRegular = np.arange(1, 11)
    nbinQuant = np.arange(1, 3)

    maxlim = 2.0

    output = {
    "withFolder"      : withFolder,
    "label"           : label,
    "mom"             : mom,
    "bdtTypes"        : bdtTypes,
    "channelsTypes"   : channelsTypes,
    "originalBinning" : originalBinning,
    "nbinRegular"     : nbinRegular,
    "nbinQuant"       : nbinQuant,
    "maxlim"          : maxlim,
    "ch_nickname"     : ch_nickname,
    }

    return output
