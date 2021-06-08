
def options_plot (analysis, channel, all_procs, Hdecays) :
    dprocs = OrderedDict()
    ## the order of the entries will be the order of the drawing, that is why this is almost manual
    # TODO: write it on a smarther way
    if analysis == "ttH" :
        conversions = "conversions"
        fakes       = "fakes_data"
        flips       = "flips_data"
        # if label == "none" it means that this process is to be merged with the anterior key
        if fakes in all_procs       : dprocs[fakes]       = {"color" :  12, "fillStype" : 3345, "label" : "Non-prompt"  , "make border" : True}
        if flips in all_procs       : dprocs[flips]       = {"color" :   1, "fillStype" : 3006, "label" : "Flips", "make border" : True}
        if conversions in all_procs : dprocs[conversions] = {"color" :   5, "fillStype" : 1001, "label" : "Conv."       , "make border" :  True}
        if "Rares" in all_procs     : dprocs["Rares"]     = {"color" : 851, "fillStype" : 1001, "label" : "Rares"       , "make border" : True}
        if "EWK" in all_procs       : dprocs["EWK"]       = {"color" : 610, "fillStype" : 1001, "label" : "EWK"         , "make border" : True}
        if "ZZ" in all_procs        : dprocs["ZZ"]        = {"color" : 610, "fillStype" : 1001, "label" : "none"        , "make border" : True}
        if "WZ" in all_procs        : dprocs["WZ"]        = {"color" : 610, "fillStype" : 1001, "label" : "EWK"         , "make border" : True}
        if "TTWW" in all_procs :
            dprocs["TTW"]                                 = {"color" : 823, "fillStype" : 1001, "label" : "none"        , "make border" : False}
            dprocs["TTWW"]                                = {"color" : 823, "fillStype" : 1001, "label" : "ttW(W)"  , "make border" : True}
        elif "TTW" in all_procs :
            dprocs["TTW"]                                 = {"color" : 823, "fillStype" : 1001, "label" : "ttW"        , "make border" : True}
        if "TTZ" in all_procs       : dprocs["TTZ"]       = {"color" : 822, "fillStype" : 1001, "label" : "ttZ"         , "make border" : True}
        ### signals
        for decay in list(set(list(Hdecays)) - set(["htt"])) :
            if "ttH_%s" % decay in all_procs :
                 dprocs["ttH_%s" % decay]                 = {"color" :   2, "fillStype" : 1001, "label" : "none"        , "make border" : False}
        dprocs["ttH_htt"]                                 = {"color" :   2, "fillStype" : 1001, "label" : "ttH"         , "make border" : True}
        if "tHq_htt" in all_procs and "tHW_htt" in all_procs :
            for decay in list(set(list(Hdecays)) - set(["htt"])) :
                if "tHq_%s" % decay in all_procs :
                    dprocs["tHq_%s" % decay]              = {"color" :  52, "fillStype" : 1001, "label" : "none"        , "make border" : False}
            for decay in Hdecays :
                if "tHW_%s" % decay in all_procs :
                    dprocs["tHW_%s" % decay]              = {"color" : 52, "fillStype" : 1001, "label" : "none"         , "make border" : False}
            dprocs["tHq_htt"]                             = {"color" : 52, "fillStype" : 1001, "label" : "tH"           , "make border" : True}
        if "VH_htt" in all_procs :
            for decay in list(set(list(Hdecays)) - set(["htt"])) :
                if "VH_%s" % decay in all_procs :
                    dprocs["VH_%s" % decay]               = {"color" : 67, "fillStype" : 1001, "label" : "none"         , "make border" : False}
            dprocs["VH_htt"]                              = {"color" : 67, "fillStype" : 1001, "label" : "tH"           , "make border" : True}

        # change the order of the stack if channel is dominated by fakes
        if channel in ["2los_1tau", "1l_2tau", "2eos_1tau", "2muos_1tau", "1mu1eos_1tau", "1l_1tau", "2l_2tau"] :
            ## remove "fakes_data" from first entry and add as last
            del dprocs[fakes]
            dprocs[fakes]                                 = {"color" :   1, "fillStype" : 3005, "label" : "Fakes"        , "make border" : True}
        if "0l" in channel :
            del dprocs["EWK"]
            dprocs["EWK"]                                 = {"color" : 610, "fillStype" : 1001, "label" : "EWK"         , "make border" : True}
            del dprocs[fakes]
            dprocs[fakes]                                 = {"color" :   1, "fillStype" : 3005, "label" : "Fakes"        , "make border" : True}
            dprocs["TT"]                                  = {"color" :   1, "fillStype" : 1001, "label" : "TT"          , "make border" : True}
    else : sys.exit("analysis " + analysis + " not implemented")
    return dprocs

def options_plot_ranges (analysis) :
    if analysis == "ttH" :
        info_channel = {
            "2lss_0tau" : { "minY" : -5., "maxY" :  115., "minYerr": 0.501, "maxYerr" : 1.59, "useLogPlot" : False},
            "ttWctrl"   : { "minY" : -5., "maxY" :  115., "minYerr": -0.6, "maxYerr" : 2.85, "useLogPlot" : False},
            "2lss_1tau" : { "minY" : -0.9, "maxY" :  14., "minYerr":  0.0, "maxYerr" : 2.75, "useLogPlot" : False},
            "3l_0tau"   : { "minY" : -6, "maxY" :  229., "minYerr": 0.501, "maxYerr" : 1.59, "useLogPlot" : False},
            "ttZctrl"   : { "minY" : -6, "maxY" :  229., "minYerr": -0.6, "maxYerr" : 2.85, "useLogPlot" : False},
            "2l_2tau"   : {
                "minY" : 0.007, "maxY" :  50.,
                "minYerr":  0.0, "maxYerr" : 2.75,
                "useLogPlot" : True
                },
            "3l_1tau"   : { "minY" : -0.2, "maxY" :  6.9, "minYerr":  0.0, "maxYerr" : 5.35, "useLogPlot" : False},
            "1l_2tau"   : { "minY" : 0.07, "maxY" :  5000., "minYerr": 0.59, "maxYerr" : 1.87, "useLogPlot" : True},
            "2los_1tau" : { "minY" : 0.07, "maxY" :  5000., "minYerr": -0.6, "maxYerr" : 2.85, "useLogPlot" : False},
            "0l_2tau"   : { "minY" : 0.07, "maxY" :  5000., "minYerr": -0.6, "maxYerr" : 2.85, "useLogPlot" : False},
            "1l_1tau"   : { "minY" : 0.07, "maxY" :  5000., "minYerr": -0.6, "maxYerr" : 2.85, "useLogPlot" : False},
            "WZctrl"    : { "minY" : 0.07, "maxY" :  5000., "minYerr": -0.6, "maxYerr" : 2.85, "useLogPlot" : False},
            "4l_0tau"   : { "minY" : -0.35, "maxY" :  13.9, "minYerr": 0.601, "maxYerr" : 2.19, "useLogPlot" : False},
            "ZZctrl"    : { "minY" : -0.35, "maxY" :  13.9, "minYerr": -0.6, "maxYerr" : 2.85, "useLogPlot" : False},
        }
    else : sys.exit("analysis " + analysis + " not implemented")
    return info_channel
