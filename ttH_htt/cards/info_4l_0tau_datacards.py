def read_from():

    withFolder = False
    label = "4l_0tau_central_deepVSjVLoose_veto_NN_legacy_cards_2019Oct09_2018"
    #mom="/home/acaan/ttHAnalysis/2017/"+label+"/datacards/2lss"
    mom="/afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/deeptauWPS/"+label+"/prepareDatacards/"
    bdtTypes = [
    #"massL4",
    #"mvaOutput_4l",
    "mvaOutput_4l_2"
    ]

    channelsTypes = [ "4l_0tau" ]
    ch_nickname = "4l_OS"

    originalBinning=100
    nbinRegular = np.arange(2, 3)
    nbinQuant = [2] #np.arange(5, 6)s

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
    # 2018:
