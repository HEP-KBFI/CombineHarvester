def read_from():

    withFolder = False
    label = "2lss_1tau_central_DNN_legacy_100bins_2018_20Dec2019"
    mom="/home/acaan/ttHAnalysis/2018/" + label + "/datacards/2lss_1tau/prepareDatacards/"
    bdtTypes = [
        "output_NN"
    ]
    # If there are subcategories construct the list of files to read based on their naming convention
    ## prepareDatacards_2lss_1tau_sumOS_output_NN_2lss_1tau_ttH_tH_3cat_v5_ttH_1tau.root
    cateDraw_type = [ "rest", ] # , "tH", "ttH"
    bdtTypes_exp = []
    for bb, bdtType in enumerate(bdtTypes) :
      #if bb == 0 : bdtTypes_exp += [ bdtType ]
      #else :
      for catType in cateDraw_type :
        bdtTypes_exp += [ bdtType + "_" + catType ]
    #if len(cateDraw_type) == 0 : bdtTypes_exp = bdtTypes

    channelsTypes = [ "2lss_1tau" ]
    ch_nickname = "2lss_1tau_sumOS"

    originalBinning=100
    nbinRegular = np.arange(1, 10)
    nbinQuant = np.arange(5, 6)

    maxlim = 2.0

    output = {
    "withFolder"      : withFolder,
    "label"           : label,
    "mom"             : mom,
    "bdtTypes"        : bdtTypes_exp,
    "channelsTypes"   : channelsTypes,
    "originalBinning" : originalBinning,
    "nbinRegular"     : nbinRegular,
    "nbinQuant"       : nbinQuant,
    "maxlim"          : maxlim,
    "ch_nickname"     : ch_nickname,
    }

    return output
