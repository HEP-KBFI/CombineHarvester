def read_from():

    withFolder = False
    label = "0l_2tau_fixed_resHTT_03Dec_100bins_2018"
    mom="/home/acaan/ttHAnalysis/2018/"+label+"/datacards/0l_2tau/prepareDatacards/"
    bdtTypes = [
        #"mvaOutput_Legacy",
        "mva_Updated"
        #"mvaOutput_0l_2tau_deeptauVTight",
        #"mva_0l_2tau_deeptauLoose_2",
        #"mvaOutput_0l_2tau_deeptauLoose",
        #"mva_0l_2tau_deeptauVTight_2",
    ]
    # If there are subcategories construct the list of files to read based on their naming convention
    ## prepareDatacards_2lss_1tau_sumOS_output_NN_2lss_1tau_ttH_tH_3cat_v5_ttH_1tau.root

    channelsTypes = [ "0l_2tau" ]
    ch_nickname = "0l_2tau_0l_2tau"

    originalBinning=100
    nbinRegular = np.arange(15, 16)
    nbinQuant = np.arange(20, 25)

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
