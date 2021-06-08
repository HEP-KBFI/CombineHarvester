def read_from():

    withFolder = False
    label = "2lss_0tau_NN_tHcat_2019Jun17"
    #"2lss_0tau_NN_tHcat-correctBal_subcategories_2019Apr22"
    #mom="/home/acaan/ttHAnalysis/2017/"+label+"/datacards/2lss"
    mom="/afs/cern.ch/work/a/acarvalh/CMSSW_10_2_10/src/data_tth/"+label+"/" 
    bdtTypes = [
        #"mva_Updated",
        "mvaDiscr_2lss",
        #"output_NN_2lss_0tau_ttH_tH_3cat_THQenrich2_v2",
        #"output_NN_2lss_0tau_ttH_tH_3cat_noTHQenrich2_v1",
        #"output_NN_2lss_0tau_ttH_tH_3cat_noTHQenrich2_v2",
        #"output_NN_2lss_0tau_ttH_tH_3cat_noTHQenrich2_v3",
        #"output_NN_2lss_0tau_ttH_tH_4cat_THQenrich2_v1",
    ]
    # If there are subcategories construct the list of files to read based on their naming convention 
    cateDraw_type = ["ttH", "tH", "ttW", "rest"]
    cateDraw_flavour = ["ee", "em", "mm"]
    cateDraw_btag = ["bl", "bt"]
    bdtTypes_exp = []
    for bb, bdtType in enumerate(bdtTypes) :
        if "output_NN" not in bdtType : 
            for cat_flavour in cateDraw_flavour :
              for charge in ["pos", "neg"] :
                if cat_flavour == "ee" : 
                    bdtTypes_exp += [  bdtType + "_ttH_2lss_0tau_" + cat_flavour + "_" + charge]
                    #bdtTypes_exp += [  bdtType + "_2lss_0tau_ttW_" + cat_flavour + "_" + charge]
                else :
                  for cat_btag in cateDraw_btag :
                    bdtTypes_exp += [  bdtType + "_ttH_2lss_0tau_" + cat_flavour + "_" + cat_btag + "_" + charge]
                    #bdtTypes_exp += [  bdtType + "_2lss_0tau_ttW_" + cat_flavour + "_" + cat_btag + "_" + charge]
        else :
            for catType in cateDraw_type :
                for cat_btag in cateDraw_btag :
                  if catType == "rest"  and cat_btag == "bt":
                      bdtTypes_exp += [ bdtType + "_" + catType + "_" + cat_btag]
                  else :
                    for cat_flavour in cateDraw_flavour :
                      bdtTypes_exp += [ bdtType + "_" + catType + "_" + cat_flavour + "_" + cat_btag]
    if len(cateDraw_type) == 0 : bdtTypes_exp = bdtTypes

    channelsTypes = [ "2lss_0tau" ]
    ch_nickname = "2lss"

    originalBinning=100
    nbinRegular = np.arange(6, 7)
    nbinQuant = np.arange(1, 20) 

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
