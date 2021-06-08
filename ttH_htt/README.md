# Making datacards.txt 

The script on  in this repository manipulate the output of the KBFI analysis into the format necessary for the statistical analysis.

To run the scripts as executable (as the exemple bellow) you may compile the repository with

```
scram b -j 8
```

The output of the KBFI analysis jobs ("prepareDatacards") is comverted into .txt/.root combine datacards as the bellow example:

```
WriteDatacards.py  --inputShapes /absolute/or/relative/path/to/prepareDatacards_favourite.root --channel 1l_2tau --cardFolder /absolute/or/relative/path/of/folder/to/results 
```

Please check it out the extensive list of command line descriptions and further options by running it with the --help option. 
For example, by default the script does not add shapes systematics to the datacard.txt, you need to explicetly ask for it adding to the commend line `--shapeSyst`

- The options for common and specific systematics are found on. 

```
configs/list_syst.py
```

the specificities of sytematics for each channel/analysis are [here for specipc systematics/channel/process](https://github.com/HEP-KBFI/CombineHarvester/blob/master/ttH_htt/configs/list_syst.py#L70) -- the structure/usage of those are expected to be self explanatory in the case you need to implement a new entry.

- The list of processes by channel and by analysis type ("ttH" ot "HH") on

```
configs/list_channels.py
```

In the way that all the config files are loaded on the main script there is no need to recompile the folder if you change/add a systematics entry.

#P.s.: 
Those are certified to work for all the ttH channels, 
but the same core scripts should work as well for the HH analysis if one adds to the configs. This will be done in a posterior stage. 

#TODO (Xanda): 
Check closelly for the shape systematics minding problable naming modifications

# Making limits/plots/impacts/GOF/Yields from one "prepareDatacards"

With the intention of testing locally if the datacard production was succesfull we also have an script that wraps all the necessary combine commands to have limits/plots/impacts/GOF... 

This one is used as the command bellow exemplifies:

```
python test/make_combine.py  --inputShapes /absolute/or/relative/path/to/prepareDatacards_favourite.root --doXXX --channel 1l_2tau --odir /absolute/or/relative/path/of/folder/to/results
```

where `--doXXX` is a placeholder for the comand line you want to give, according with which 
action you want to be computed. It is recomended to do one option/run.

Please check it out the extensive list of command line descriptions of the action options and further options by running it with the --help option

#IMPORTANT: 
To run the option that make plots (`makePostFitPlots.py`) work it is imperative that you started your ssh session with at least `-Y` option (prefereable with `-XY`): e.g. `ssh -Y user@server.ser`

## Making plots only

We do have an execulable `makePostFitPlots.py` to draw prefit/postfit plots that can be used as standalone (not on the commands wrapper `make_combine.py`). Please run the wrapper once with the option `--doPreFit` to see printed out an example of how to use it. Also do not hesitate on check `makePostFitPlots.py --help`


The options for color code of the plots (global to each analysis ttH/HH) and ranges of the plots (specific for each channel) are found on:

```
configs/plot_options.py
```

# Making datacards.txt for kt/kv scans from one "prepareDatacards"

The command bellow manipulate the output of the KBFI analysis (master10X, that contain the weights for the tH/ttH kinematics variation) into the format necessary for the statistical analysis that is done in [this repository](https://github.com/acarvalh/signal_extraction_tH_ttH)


```
python test/do_kt_scans.py --inputShapes /absolute/or/relative/path/to/prepareDatacards_favourite.root --channel 1l_2tau --cardFolder testPlots_master10X/
```

Please check it out the extensive list of command line descriptions and further options by running it with the --help option. 
For example, by default the script does not add shapes systematics to the datacard.txt, you need to explicetly ask for it adding to the commend line `--shapeSyst`

# WARNING: 
For the final combined results/plots/tables on the ttH analysis please refer to [this repository](https://github.com/acarvalh/signal_extraction_tH_ttH), that takes as inputs only combine datacards (.txt) and is in line with the latest fit and plot options agreed for legacy paper with the other groups.

