# One example of command chain

I give one example of the set of commands in the usual structure of subfolders I use to not get lost

```
mkdir output_to_card/res/results/

text2workspace.py /path/complete/datacard.txt   \
-o /path/complete/results/datacard_WS.root
```

```
cd /path/complete/results/

combineTool.py -M \
FitDiagnostics /path/complete/results/datacard_WS.root \
 --saveShapes --saveWithUncertainties  --saveNormalization  --skipBOnlyFit  \
-n _blabla
```
add `-t -1` if blinded.

```
mkdir output_to_card/res/plots/

python test/makePlots.py  \
--input output_to_card/res/results/fitDiagnostics_shapes_blabla.root \
--odir output_to_card/res/plots/  \
--original /path/complete/datacard.root \
 --era 2017 \
--nameOut blabla2 \
--do_bottom  --channel 2l_0tau \
--binToRead HH_2l_0tau \
--binToReadOriginal  HH_2l_0tau \
--HH  --signal_type res  --mass spin0_400  --HHtype bbWW
```

add `--unblind` to add data to the plot

We will use this ensemble of commands a lot, so usually, I script them (see eg here).

comments:

- The `--binToRead` is the name of the folder to read inside the `fitDiagnostics_blabla.root` folder `shapes_fit_s`, that is the name of the bin in the datacard.txt (see [1])
- If `--original /path/complete/datacard.root` is not added it will make a plot with plain bins
- era is just to write the correct lumi on the plot
- this will make plots where the spin 0 resonance with 400 GeV is the signal. See the options that you can use in the command-line help for picking the HH signal (they have an effect [here](https://github.com/HEP-KBFI/CombineHarvester/blob/961f2b1a0a8ae002e3d7fd82fb523fa11fa97568/ttH_htt/configs/list_channels_HH.py#L57-L81)).

[1] protip: When you are going to do combined fits you may like to combine cards keeping the same bin naming convention for internal bins,
like eg:

```
combineCards.py \
HH_2l_0tau=datacard_hh_bb2l.txt \
HH_1l_0tau=datacard_hh_bb1l.txt \
> datacard_hh_combo.txt
```

# Description of the used configs

- Plot ranges in top/bottom plots, make not to be log-scale and labels are coded by channel [here](https://github.com/HEP-KBFI/CombineHarvester/blob/fd6a86d02f87b0746601c6850805f27c2bafed0d/ttH_htt/configs/plot_options_HH.py#L104-L129)
- Stack processes naming, drawing style, drawing order, labels in legend, processes to merge (look eg how VH and TH are merged) are set globally [here](https://github.com/HEP-KBFI/CombineHarvester/blob/fd6a86d02f87b0746601c6850805f27c2bafed0d/ttH_htt/configs/plot_options_HH.py#L104-L129)
- The list of processes that the plotter look is hardcoded by channel [here](https://github.com/HEP-KBFI/CombineHarvester/blob/ee10ff510cc31486704a4bf3b7ea1dd5821c15eb/ttH_htt/configs/list_channels_HH.py#L80-L92). Like this, you have the power of asking for a process not be drawn (if eg, have almost negligible yield).
 - if you see blanks between the total error band an the stack it is problably because a process if missing from this list (and problably as well from the ordered dictionary that makes the stack)
- The choice of the HH signal to draw makes effect [here](https://github.com/HEP-KBFI/CombineHarvester/blob/ee10ff510cc31486704a4bf3b7ea1dd5821c15eb/ttH_htt/configs/list_channels_HH.py#L80-L92).
 - Note that it supports having make a renaming, see the making of the cards for GF nonresonant NLO [here]() to understand why that.

Note: If you add processes to the datacards that are not in this list (eg ggH and qqH) you need to explicitly add on the above-mentioned places. \n

*IMPORTANT*: you need to ssh with "ssh -XY" to that working, and let the canvases pop-up. With "ssh -XYC" the plotter maybe run faster.
That is why we cannot now make that faster / as jobs / in screen right now.
