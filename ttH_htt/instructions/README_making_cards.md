# Some pointers to the configs of the WriteDatacards (prepareDatcard.root -> datacard.txt/root)

General idea of making a datacard.txt/root

The same WriteDatacards command, with those added options.

Examples of commands (with the substructure of subfolders I usually use to always find results):

mkdir output_to_cards/res/

```
WriteDatacards.py \
--inputShapes folder_cards_original_DL/newProcName/prepareDatacards_blabla.root \
--channel "2l_0tau" \
--noX_prefix  \
--signal_type "res" \
--mass "spin0_400" \
--HHtype  "bbWW" --analysis HH \
--output_file output_to_cards/res/HH_blabla_2016 \
--era 2016
```

Add also `--no_data` if you want a blinded card (the data_obs will be the sum of BKGs).
Usually datacards checking during reviews are asked on this way.

It will create the card: output_file + ".txt"

comments:

- this will make datacards where the spin 0 resonance with 400 GeV is the signal. See the options that you can use in the command-line help for picking the HH signal (they have an effect [here](https://github.com/HEP-KBFI/CombineHarvester/blob/961f2b1a0a8ae002e3d7fd82fb523fa11fa97568/ttH_htt/configs/list_channels_HH.py#L57-L81)).
- There are also other possible options.
  - eg to understand the option `--renamedHHInput` look [here](https://github.com/HEP-KBFI/CombineHarvester/blob/master/ttH_htt/instructions/README_cards_kl_kt_lik.md)
    - If that is not uses this only says if you used the raw TLL input (did not do step1 of that instructions)

## adding multilepton channels

- to add mutilepton channels mind [here](https://github.com/HEP-KBFI/CombineHarvester/blob/612740181c88378389d0b736675645c1c7e9b348/ttH_htt/configs/list_channels_HH.py#L76-L89), [here](https://github.com/HEP-KBFI/CombineHarvester/blob/612740181c88378389d0b736675645c1c7e9b348/ttH_htt/configs/plot_options_HH.py#L104-L150) and [here](https://github.com/HEP-KBFI/CombineHarvester/blob/03db55b95b0e5955d97820c3688c5d5d3f3422d6/ttH_htt/configs/list_channels_HH.py#L13-L38) (for this last do first the working example described [here](https://github.com/HEP-KBFI/CombineHarvester/blob/master/ttH_htt/instructions/README_cards_kl_kt_lik.md)).

## TODO's (suggestions)

1 -  Separate the [list of systematics](https://github.com/HEP-KBFI/CombineHarvester/blob/612740181c88378389d0b736675645c1c7e9b348/ttH_htt/configs/list_syst.py) in 3 files to be loaded accordingly with the requested analysis
- common ones: lumi, pdf's, theory shape systematics,...., JEC/JER....
- specific to HH (or even to bbWW / multilepton ?)
- specific to ttH (everything in the file right now that is none of the above)

2 - Fix the application of HH BRs by channel accordingly with naming convention ([here-BRs](https://github.com/HEP-KBFI/CombineHarvester/blob/612740181c88378389d0b736675645c1c7e9b348/ttH_htt/configs/list_syst.py#L61-L66) uncertainty and [here-theory-shape-uncertainty](https://github.com/HEP-KBFI/CombineHarvester/blob/612740181c88378389d0b736675645c1c7e9b348/ttH_htt/configs/list_syst.py#L90)). See [this issue](https://github.com/HEP-KBFI/hh-bbww/issues/6) also for the single H processes in TLL prepareDatacards.
