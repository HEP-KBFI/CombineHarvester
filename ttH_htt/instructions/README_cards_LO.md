# How make cards on scans scan should be


```
python test/do_HH_LO_cards.py \
--channel "2l_0tau"  \
--prepareDatacards_path prepareDatacards_path \
--output_path output_path \
--era 2016 \
--scan_in shape_BM
```

Check the options of `--scan_in`.
In the SL case you can add `--flavourCats` to make the cards with flavour categories (see issue 1).

- Comment:
  - The MVA (histogram) to be used is understood by the name of the input file
    - In this example, for `--scan_in kl_scan` and `--scan_in shape_BM` the MVA is the one trained for SM and for `--scan_in resonance` it is the one trained for 900GeV signal. That is what this option is eg [here](https://github.com/HEP-KBFI/CombineHarvester/blob/8955e0dbe24b0241f79c4e09b9f2274d1916a34b/ttH_htt/test/do_HH_LO_cards.py#L89)

# Issues

- *issue 1*: to make the merged cards (eg without `--flavourCats` in the SL case) you will need to hadd the inputs yourself, [following that naming convention](https://github.com/HEP-KBFI/CombineHarvester/blob/d9454235b9f5a1ef6061bcd3f2e6e4dad4612ef0/ttH_htt/test/do_HH_LO_cards.py#L231-L237).
  - in the script for the data/MC plots exercise [I did that to be part of the script](https://github.com/HEP-KBFI/CombineHarvester/blob/d9454235b9f5a1ef6061bcd3f2e6e4dad4612ef0/ttH_htt/test/do_bbWW_dataMC.py#L117-L123), I am not sure it worth to make that automatic.

## TODO's (suggestions)

- You may like to make cards be submitted to be faster (as eg it is done [here](https://github.com/HEP-KBFI/CombineHarvester/blob/d9454235b9f5a1ef6061bcd3f2e6e4dad4612ef0/ttH_htt/test/do_HH_LO_cards.py#L231-L237))
  - the problem on doing that now is that the datacard.txt/root naming comes from the log file of WriteDatacard run
    - that logic should be easy to solve
- For the nonres you may like to do with other naming convention, to eg, match with other groups agreement (see step 1 [of these instructions](https://github.com/HEP-KBFI/CombineHarvester/blob/master/ttH_htt/instructions/README_cards_kl_kt_lik.md))
- You may like to have the same signal name in all cards for any reason, in this case this needs to be sone at datacard.txt/root level
  - As an is an example you may see what is coded when you add `--coupling` to the WriteDatacard script (that works for the tH signal having a coupling and appearing in the prepareDatcard as eg `tHq_coupling_hww` and in last step rename it to `tHq_hww` you will need to adapt it to HH/your case)
- You may like to do input cards (as eg [here](https://github.com/HEP-KBFI/CombineHarvester/blob/master/ttH_htt/instructions/README_rebining.md) ) to hardcode all these subcategories options / binning choices / MVA choices, instead of having on the main code.

# Working examples

```
/home/acaan/bbww_Jul2020_baseline_dataMC/DL/MVA/2017/inputs/

/home/acaan/bbww_Jul2020_baseline_dataMC/SL/MVA/2016/inputs/

/home/acaan/bbww_Jul2020_baseline_dataMC/SL/MVA/2017/inputs/

- (lxplus) /afs/cern.ch/work/a/acarvalh/public/to_HH_bbWW/cards_baselineAug
  - Tarballs with SL and DL
```

There are also examples of outputs in one subfolder previous to inputs.
The structure of output_path is done manually.

The examples of outputs can also be found in lxplus

```
/afs/cern.ch/work/a/acarvalh/public/to_HH_bbWW/cards_baselineAug
```
