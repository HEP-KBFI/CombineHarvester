# For making the prepareDatacards out of analysis jobs

When doing the analysis jobs remember to ask for the additional plots for data/MC be done
- see [this issue](https://github.com/HEP-KBFI/hh-bbww/issues/14)  for pointers were to make it, I left something to you in this issue.
- binning is set eg [here](https://github.com/HEP-KBFI/hh-bbww/blob/66a4fe8f5461f2ac1a2ba1c9c86c4458fe86111e/src/EvtHistManager_hh_bb2l.cc#L179-L187)
- in [this issue](https://github.com/HEP-KBFI/hh-bbww/issues/16) tells how to add plots booking (as eg the lepton cone pt)

# For doing cards and plots

Repository where the prepareDatacards to be rebined are: prepareDatacards_path

The bellow command will:

1 - do a datacard.txt/root of the prepareDatacards of the list constructed as `typeMVA`
2 - if asked so, merge some categories, [here](https://github.com/HEP-KBFI/CombineHarvester/blob/fd6a86d02f87b0746601c6850805f27c2bafed0d/ttH_htt/test/do_bbWW_dataMC.py#L117-L123)
3 - do prefit plots for those

```
python test/do_bbWW_dataMC.py \
--inputPath inputPath \
--outputpath outputpath \
--channel "2l_0tau" \
--era 2017
```

The plots are then in outputpath + "/plots".

- The "do_bbWW_dataMC.py" is just a wrapper of commands --> inside this script you have the commands to make datacard.txt/root and the plots and in each script you can check the options on help

Do take a look at them individually as some options are harcoded, e.g. by now the assumed signal os spin 0 resonance with mass = 400 GeV.

# For polishing plots style

If you want to change plot ranges in top/bottom plots, make not to be log-scale... see [here](https://github.com/HEP-KBFI/CombineHarvester/blob/f49bcb33223b2019ffcbbc584bac7508c4868985/ttH_htt/instructions/README_plotter.md) for the details of the plotter.

If already ran that once  you then put `makePlotsOnly = True` in "do_bbWW_dataMC.py" and run the same command, it takes seconds to remake each plot (faster than take each saved.root and change it there...)

For tunning those plot options, I suggest doing it in one plot first, instead of run the full to see the result later (or, in ran it once, you will have the plotting command printed in the screen, just use it standalone)

# For doing post-fit plots

Just add ` --doPostFit` on this command and run just the plots again with `makePlotsOnly = True` , the combine fitDiagnosis is already done in a first run.

# Some concrete input examples

manivald
- DL:  /home/acaan/bbww_Jul2020_baseline_dataMC/DL/dataMC/
- SL: /home/acaan/bbww_Jul2020_baseline_dataMC/SL/dataMC/

lxplus
- SL: /afs/cern.ch/work/a/acarvalh/public/to_HH_bbWW/SL/hh_bb1l_26Jul_baseline_TTSL_noWjj_dataMC
- DL: /afs/cern.ch/work/a/acarvalh/public/to_HH_bbWW/DL/hh_bb2l_21July_SM_default_dataMC
