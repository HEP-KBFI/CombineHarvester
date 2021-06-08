# Other functionalities that are in another repo and you may like to export to this repo


1) do a plain table of yields with uncertainies from prefit/postfit

In [this repo](https://github.com/acarvalh/signal_extraction_tH_ttH) you have a
card with options of what to do [here](https://github.com/acarvalh/signal_extraction_tH_ttH/blob/82463b2f37735a14af806b00b1e078bcecf94925/cards/options.dat).

If in this options card you have as options set:

```
doWS                    = True
preparePlotCombine      = True
drawPlot                = False
doTableYields           = True
```
And ALL THE REST AS FALSE.

You can run:

```
python test/run_limits_floating_components.py \
 --cardToRead cardToRead \
 --cardFolder cardFolder/
```

You will have as output a log file

```
cardFolder/cardFolder.log
```

that are the prefit yields (with uncertaities) taken from the datacard.txt/root.

- If you do that once with one  datacard.txt/root and follow what are the
combine commands and functions called to do so

If you would like to do postfit ask in the to the option card as well

```
doPostFit           = True
```
