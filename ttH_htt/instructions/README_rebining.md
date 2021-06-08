# Running a bin optimization exercise

Repository where the prepareDatacards to be rebined are: prepareDatacards_path

The bellow command will:

1 - do a datacard.txt/root of the prepareDatacards with many bins (see list on the input card described bellow)
2 - do copies of this card rebined in a subdirectory `output_path/datacards_rebined`
3 - do blinded limits to each one, save on log files in `output_path/datacards_rebined/results`
4 - collect the numeric central limits + 1 sigma in a plot
4 - do prefit plots for some bin choices, if (see list on the input card described bellow)

```
 python test/rebin_datacards_HH.py \
 --channel "1l_0tau"  \
 --signal_type res  \
 --mass spin0_900  \
 --HHtype bbWW \
 --prepareDatacards_path /home/acaan/bbww_Jul2020_baseline_dataMC/SL/MVA/ \
 --output_path /home/acaan/bbww_Jul2020_baseline_dataMC/SL/MVA/results/
```

The `--channel` [defines the input cards](https://github.com/HEP-KBFI/CombineHarvester/blob/0cd321e3d62aa37c9eaa392f51219a76102fc972/ttH_htt/test/rebin_datacards_HH.py#L72-L73) that have the information of what you want to rebin and how.
(eg for 1l_0tau [this is the card](https://github.com/HEP-KBFI/CombineHarvester/blob/0cd321e3d62aa37c9eaa392f51219a76102fc972/ttH_htt/cards/info_1l_0tau_datacards.py)).
This card contains choices of:

- which MVA type (by the name convention of the prepareDatacards)
 - in the baseline for bbWW SL we did only BDTs targeting the SM nonresonant and the spoin 0 900 GeV
- which subcategories list, the full one, or one of your chosing after doing some files merging, [example](https://github.com/HEP-KBFI/CombineHarvester/blob/0cd321e3d62aa37c9eaa392f51219a76102fc972/ttH_htt/cards/info_1l_0tau_datacards.py#L11-L15)
- which subcategory to consider == you may like to comment in/out parts to have then done in different bin ranges/overlay same bin range
- a range of bins to scan, [here](https://github.com/HEP-KBFI/CombineHarvester/blob/0cd321e3d62aa37c9eaa392f51219a76102fc972/ttH_htt/cards/info_1l_0tau_datacards.py#L37-L38)
- a list of bins to make a prefit plot from the a rebined datacard.txt/root, [here](https://github.com/HEP-KBFI/CombineHarvester/blob/0cd321e3d62aa37c9eaa392f51219a76102fc972/ttH_htt/cards/info_1l_0tau_datacards.py#L54)
- the ranges of the plot limits X nbins, [here](https://github.com/HEP-KBFI/CombineHarvester/blob/0cd321e3d62aa37c9eaa392f51219a76102fc972/ttH_htt/cards/info_1l_0tau_datacards.py#L40-L41)

As you saw above, you can  chose the signal assumption in the command line `--signal_type res  --mass  --HHtype`
By default the signal assumed is SM LO.

- *IMPORTANT*: if you are optimizing for a BDT trained for signal, you must chose that signal too be considered on the binning optimization to the results make sense!!!


- The manipulation of the card with rebining information is manual and it is suposed to be manual -- that is a binning optimization, mostly visual.

You can skip some of the steps done by the script

- If you already have the rebined datacards and only want to make a prefit oplot for a differente choice of bins use `--doLimitsOnly`
- If you just want to  `--drawLimitsOnly` you just collect the limits in a plot of limits X nbins, in case you need to adapt the plot ranges

ps.: the step 1 must always be done as it sets the naming convention of the final card given the signal,
that is fast enought to not have to hardcode the construction of the datacard.txt/root name.

## Collecting limits of combinations

After you decided the best binning choices to each subcategory you use that information to cambine the cards that you want and compute limits you combine the chosen cards by hand.
Just for the sake of the example, the bellow is usimh the result of the baseline optimization of bbWW SL (see [here]())

```
cd output_path/datacards_rebined

combineCards.py \
Res_allReco=datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_Res_allReco_bbWW_res_spin0_900_3bins.txt \
HbbFat_WjjRes_allReco=datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_HbbFat_WjjRes_allReco_bbWW_res_spin0_900_5bins.txt \
> datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_bbWW_res_spin0_900_SubCats_moreBins.txt

combineCards.py \
HbbFat_WjjRes_allReco_m=datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_HbbFat_WjjRes_allReco_m_bbWW_res_spin0_900_8bins.txt \
HbbFat_WjjRes_allReco_e=datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_HbbFat_WjjRes_allReco_e_bbWW_res_spin0_900_8bins.txt \
Res_allReco_1b_m=datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_Res_allReco_1b_m_bbWW_res_spin0_900_5bins.txt \
Res_allReco_1b_e=datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_Res_allReco_1b_e_bbWW_res_spin0_900_5bins.txt \
Res_allReco_2b_m=datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_Res_allReco_2b_m_bbWW_res_spin0_900_5bins.txt \
Res_allReco_2b_e=datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_Res_allReco_2b_e_bbWW_res_spin0_900_5bins.txt \
> datacard_hh_bb1l_hh_bb1l_cat_jet_2BDT_Wjj_simple_X900GeV_bbWW_res_spin0_900_flavourSubCats_moreBins.txt
```

# rebining type choices

By now there are two (done in [this function](https://github.com/HEP-KBFI/CombineHarvester/blob/0cd321e3d62aa37c9eaa392f51219a76102fc972/ttH_htt/python/data_manager.py#L1030)):

1 - regular binning, by default
2 - quantiles binning adding the option
 - now set ine the sum of BKGs, defined as any process that does not have a H, hh, signal or data_obs in the name, see [here](https://github.com/HEP-KBFI/CombineHarvester/blob/db024d3d09e680165b45a4520bdbabcc18275d46/ttH_htt/python/data_manager.py#L1134-L1139)

Those pointers should help you in case you want to implement another binning type.

# To note

- If you change the naming convention of the subcategories on the jobs (e.g. including multiclass bins), you will need to adapt the logic/namings in the input cards by channel.

- We do a text replacing in the datacard.txt [here](), that is introducing weird characters in the result datacard_Xbins.txt. That is not a problem for any computation, but maybe anoying if you want to oprn thr card to read with `less`. You may like to fix that, but that is not urgent.

# Some concrete input/output examples

- (manivald) prepareDatacards_path = output_path = /home/acaan/bbww_Jul2020_baseline_dataMC/SL/MVA/
- (lxplus)   prepareDatacards_path = output_path = /afs/cern.ch/work/a/acarvalh/public/to_HH_bbWW/SL/rebining_output_example.tar.gz

They do not need to be the same, just for the sake of this example they are.
