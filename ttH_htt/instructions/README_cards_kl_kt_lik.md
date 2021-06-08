# How a card to kt-kl likelihood scan should be

See [link1](https://github.com/fabio-mon/HiggsAnalysis-CombinedLimit/blob/102x_includingHH/python/HHModel.py) the physics model and [here](https://indico.cern.ch/event/922778/contributions/3926882/attachments/2066188/3467540/HH_meeting_29_Jun_2020.pdf) a presentation of how the input cards should be.

ps.: The inference repository is being made inside the bbWW private area [link2](https://gitlab.cern.ch/cms-hh-bbww/statistical-inference).
As this is not only usable on bbWW, that will be passed to a more public place soon.
A presentation of it is features is [here](https://indico.cern.ch/event/922781/contributions/3952917/attachments/2076679/3487269/20072020_CMS.pdf)

ps.2: It is ok to make datacards.txt/root in one CMSSW release and the inference in other.

# Making a bbWW card

Repository where the original prepareDatacards: prepareDatacards_path.

## step 1 -- fixing naming conventions to go along link1

python test/rename_procs.py --inputPath prepareDatacards_path

All the prepareDatacards in "inputPath" with renamed processes will be under the subdirectory /newProcName
If you wanna test it out you will need to copy the prepareDatacards_path to a place that you have rights to write on (or code it to write the results to be written in another place).

--> if you add it to the above command with a  `--card  prepareDatacards_bla.root` it will make only this file

The naming conventions to change are written in this [dictionary](https://github.com/HEP-KBFI/CombineHarvester/blob/c00175249c5f344044a8f13b1e0d14003841979a/ttH_htt/test/rename_procs.py#L22-L43), you may need to adapt again due the inference part [issue 1].

## step 2 -- To make a datacard.txt/root with the format needed in link1

To make the correct formatting you need the bellow option
(see here for details on the Writedatacards macro)

```
--analysis HH  --renamedHHInput  --signal_type nonresNLO  --HHtype bbWW
```

The options in last option (`--HHtype`) needs an explanation [issue 1]

I am assuming that they need to be rebinned to have final cards.

We do have a wrapper that does the rebining (out of a [hardcoded dictionary of bin/subcategories](https://github.com/HEP-KBFI/CombineHarvester/blob/bfe51dc8b83244dd5980da2b398d059dd1646dd2/ttH_htt/test/do_HH_GF_NLO_cards.py#L55-L78))
and create the final card, so you so not need to make that by hand.

```
python test/do_HH_GF_NLO_cards.py \
--channel "2l_0tau"  \
--prepareDatacards_path prepareDatacards_path \
--output_path output_path \
--era 2017
```

There is an additional option `--signal` related with [issue 1], that will chose both an choice of channels to consider in WriteDatacards (`--HHtype`) and an output file naming convention.

## Simple developments not done at the moment

- You may like to have the option to bypass the rebining, in the semi-final case that you will have directly the input with correct binning
- You may like to do input cards (as eg [here](https://github.com/HEP-KBFI/CombineHarvester/blob/master/ttH_htt/instructions/README_rebining.md) ) to hardcode all these subcategories options / binning choices instead of having on the main code.

# Issues

- issue 1: by now in the development of link1 is pending to verify if/how we can use multiprocesses and how, so there are options to consider only one channel for tests.
  -  This is just to keep in mind that you may need to change naming convention again for final consumption.

The components needed to make the templates are [those](https://github.com/HEP-KBFI/CombineHarvester/blob/7c2ea180fd960d455860dc65977e778c74a55b08/ttH_htt/configs/list_channels_HH.py#L46)  for GF and [those](https://github.com/HEP-KBFI/CombineHarvester/blob/7c2ea180fd960d455860dc65977e778c74a55b08/ttH_htt/scripts/WriteDatacards.py#L206-L213) for VBF. To make the signal for each HH final state feed the physics model and construct the signal you need this complete set of 3 (5) shapes in for each HH final state.

- issue 2: some processes in some subcategories have negligible yield in all the components -- that will lead to crashes/inconsistencies in the fit.
  - to solve that at the moment I comment stuff by hand
    - eg all the yields of bbww SL are negligible in DL cards. To do multiprocess DL cards (DL cards considering bbww DL and bbtt) I remove bbww SL of [this list](https://github.com/HEP-KBFI/CombineHarvester/blob/94b09ebd55eb83ec4ab7b5c16ec3eb96ba2d0db8/ttH_htt/configs/list_channels_HH.py#L15) -- that is not an ideal procedure!!!!
  - [Suggestion to solve:] You need to put a safeguard that tells to not add any of the templates for that process if (and only if) ALL the 3 (5) templates are negligible == eg have yield less than 0.01. One idea is a variation of [this function](https://github.com/HEP-KBFI/CombineHarvester/blob/7c2ea180fd960d455860dc65977e778c74a55b08/ttH_htt/scripts/WriteDatacards.py#L206-L213) but entering the list of couplings for GF and VBF (mind the renaming!).
    - the trick for not doing that using the above-mentioned function is that if you have a channel that have non-negligible yield for 2 parts of the shape template and a negligible yield to a third you will need to keep that third one.

- issue 3: Not all the processes have complete set of templates to GF and/or VBF (= samples are missing in the system). In this case you cannot add the GF or VBF process with that HH final state to  the card.
  - by now that is also done by hand commenting in/out the lists [here](https://github.com/HEP-KBFI/CombineHarvester/blob/94b09ebd55eb83ec4ab7b5c16ec3eb96ba2d0db8/ttH_htt/configs/list_channels_HH.py#L13-L28)
    - [Suggestion to solve:] You need to put a safeguard that tells to not add any of the templates for that process if ALL the templates are existent in the input file.

- issue 4: Now in the working inputs we do not have the single H processes separated by branching ratio. Just for testing the workflow adding the single H scaling I ONLY renamed [those for a suitable naming convention](https://github.com/HEP-KBFI/CombineHarvester/blob/70ea4d84548242b4bf093b817553024fa020875a/ttH_htt/test/rename_procs.py#L28-L30). To link1 work well with single H processes scaled they need to be marked as signal.
  - As this is not a permanent solution, and in the working inputs we have only a couple of single H to comment/uncomment [this part](https://github.com/HEP-KBFI/CombineHarvester/blob/master/ttH_htt/configs/list_channels_HH.py#L84-L93) will chose what to have as signal in the resulting datacard.txt/root (whateaver is in `"bkg_procs_from_MC"` list is marked as BKG in the datacard.txt/root)
    - [Solution:] solve [this issue](https://github.com/HEP-KBFI/hh-bbww/issues/6) in the analysis code

# Working input examples (inputs and results inside)

  - (manivald)
    - SL: /home/acaan/bbww_Jul2020_baseline_dataMC/SL/MVA/2017/
    - DL: /home/acaan/bbww_Jul2020_baseline_dataMC/DL/MVA/2017/
  - (lxplus) /afs/cern.ch/work/a/acarvalh/public/to_HH_bbWW/cards_baselineAug
    - Tarballs with SL and DL
```
datacard_hh_bb2l_hh_bb2l_OS_SM_plainVars_inclusive_bbWW_DL_nonresNLO_none_45_onlyDL_2017.txt

br as DL_hbb_hww == does not contain VBF

datacard_hh_bb2l_hh_bb2l_OS_SM_plainVars_inclusive_bbWW_bbtt_nonresNLO_none_45_onlyBBTT_2017.txt

br as only hbb_htt === contain GF and VBF

datacard_hh_bb2l_hh_bb2l_OS_SM_plainVars_inclusive_bbWW_nonresNLO_none_45_multisig_2017.txt

br as hbb_htt (GF and VBF) + DL_hbb_hww
```
