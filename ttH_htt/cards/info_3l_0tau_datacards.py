def read_from():

    withFolder = False
    label = "3l_0tau_central_DNN_legacy_100bins_2018_20Dec2019"
    mom="/home//acaan/ttHAnalysis/2018/" + label + "/datacards/3l/prepareDatacards/"
    bdtTypes = [
    #"mvaDiscr_3l"
    "output_NN"
    #"output_NN_3l_ttH_tH_3cat_v8"
    ]
    # If there are subcategories construct the list of files to read based on their naming convention
    cateDraw_type = [ "tH", ] #   "rest"   "ttH",
    cateDraw_btag = [ "bl", ] # "bt"
    cateDraw_flavour = [ "eee" , "eem", "emm", "mmm",  ] #
    bdtTypes_exp = []
    for bdtType in bdtTypes :
        if "output_" in bdtType :
            for catType in cateDraw_type :
                for cat_btag in cateDraw_btag :
                    for cat_flav in cateDraw_flavour :
                        if catType == "rest" :
                                if cat_flav in cateDraw_flavour :
                                    bdtTypes_exp += [ bdtType + "_" + catType + "_" + cat_flav ]
                                else :
                                    bdtTypes_exp += [ bdtType + "_" + catType + "_" + cat_flav + "_" + cat_btag]
                        else :
                            bdtTypes_exp += [ bdtType + "_" + catType+ "_" + cat_btag]
        else :
            bdtTypes_exp += [bdtType]

    if len(cateDraw_type) == 0 : bdtTypes_exp = bdtTypes

    channelsTypes = [ "3l_0tau" ]
    ch_nickname = "3l_OS"

    originalBinning=100
    nbinRegular = np.arange(10, 12)
    nbinQuant = np.arange(5, 6)

    maxlim = 2.0

    output = {
    "withFolder"      : withFolder,
    "label"           : label,
    "mom"             : mom,
    "bdtTypes"        : list(set(bdtTypes_exp)),
    "channelsTypes"   : channelsTypes,
    "originalBinning" : originalBinning,
    "nbinRegular"     : nbinRegular,
    "nbinQuant"       : nbinQuant,
    "maxlim"          : maxlim,
    "ch_nickname"     : ch_nickname,
    }

    return output
