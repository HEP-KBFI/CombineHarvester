def read_from():

    withFolder = False
    label = "1l_2tau_fixed_resHTT_03Dec_100bins_2016"
    mom="/home/acaan/ttHAnalysis/2016/"+label+"/datacards/1l_2tau/prepareDatacards/"
    bdtTypes = [
        "mvaOutput_legacy",
        "mvaOutput_final"
    ]
    # If there are subcategories construct the list of files to read based on their naming convention

    channelsTypes = [ "1l_2tau" ]
    ch_nickname = "1l_2tau"

    originalBinning=100
    nbinRegular = np.arange(10, 11)
    nbinQuant = np.arange(1, 12)

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
