#!/usr/bin/env python
import os, shlex
from subprocess import Popen, PIPE

# python test/do_kt_scans.py --inputShapes /afs/cern.ch/work/a/acarvalh/CMSSW_10_2_10/src/data_tth/prepareDatacards_1l_2tau_mvaOutput_plainKin_SUM_VT_noRebin_noNeg.root --channel 1l_2tau --cardFolder testPlots_master10X
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputShapes",    type="string",       dest="inputShapes", help="Full path of prepareDatacards.root")
parser.add_option("--channel",        type="string",       dest="channel",     help="Channel to assume (to get the correct set of syst)")
parser.add_option("--channel_to_card",        type="string",       dest="channel_to_card",     help="Channel to assume naming the output datacard in case of subcategories",  default="none")
parser.add_option("--cardFolder",     type="string",       dest="cardFolder",  help="Folder where to save the datacards (relative or full).\n Default: teste_datacards",  default="teste_datacards")
parser.add_option("--shapeSyst",      action="store_true", dest="shapeSyst",   help="Do apply the shape systematics. Default: False", default=False)
parser.add_option("--no_data",      action="store_true", dest="no_data",   help="Self explanatory", default=False)

parser.add_option("--era",            type="int",          dest="era",         help="Era to consider (important for list of systematics). Default: 2017",  default=2017)
(options, args) = parser.parse_args()

if options.channel_to_card == "none" :
    channel_to_card = options.channel
else :
    channel_to_card = options.channel_to_card

func_file = os.environ["CMSSW_BASE"] + "/src/CombineHarvester/ttH_htt/python/data_manager.py"
execfile(func_file)


tHweights = [
  {"kt" : -1.0, "kv" : 1.0, "cosa" : -10}, # the default (i.e. no weight)
  {"kt" : -3.0, "kv" : 1.0, "cosa" : -10},
  {"kt" : -2.0, "kv" : 1.0, "cosa" : -10},
  {"kt" : -1.5, "kv" : 1.0, "cosa" : -10},
  {"kt" : -1.25, "kv" : 1.0, "cosa" : -10},
  {"kt" : -0.75, "kv" : 1.0, "cosa" : -10},
  {"kt" : -0.5, "kv" : 1.0, "cosa" : -10},
  {"kt" : -0.25, "kv" : 1.0, "cosa" : -10},
  {"kt" : 0.0, "kv" : 1.0, "cosa" : -10},
  {"kt" : 0.25, "kv" : 1.0, "cosa" : -10},
  {"kt" : 0.5, "kv" : 1.0, "cosa" : -10},
  {"kt" : 0.75, "kv" : 1.0, "cosa" : -10},
  {"kt" : 1.0, "kv" : 1.0, "cosa" : -10},
  {"kt" : 1.25, "kv" : 1.0, "cosa" : -10},
  {"kt" : 1.5, "kv" : 1.0, "cosa" : -10},
  {"kt" : 2.0, "kv" : 1.0, "cosa" : -10},
  {"kt" : 3.0, "kv" : 1.0, "cosa" : -10},
  {"kt" : -2.0, "kv" : 1.5, "cosa" : -10},
  {"kt" : -1.25, "kv" : 1.5, "cosa" : -10},
  {"kt" : -1.0, "kv" : 1.5, "cosa" : -10},
  {"kt" : -0.5, "kv" : 1.5, "cosa" : -10},
  {"kt" : -0.25, "kv" : 1.5, "cosa" : -10},
  {"kt" : 0.25, "kv" : 1.5, "cosa" : -10},
  {"kt" : 0.5, "kv" : 1.5, "cosa" : -10},
  {"kt" : 1.0, "kv" : 1.5, "cosa" : -10},
  {"kt" : 1.25, "kv" : 1.5, "cosa" : -10},
  {"kt" : 2.0, "kv" : 1.5, "cosa" : -10},
  {"kt" : -3.0, "kv" : 0.5, "cosa" : -10},
  {"kt" : -2.0, "kv" : 0.5, "cosa" : -10},
  {"kt" : -1.25, "kv" : 0.5, "cosa" : -10},
  {"kt" : 1.25, "kv" : 0.5, "cosa" : -10},
  {"kt" : 2.0, "kv" : 0.5, "cosa" : -10},
  {"kt" : 3.0, "kv" : 0.5, "cosa" : -10},
  #{"kt" : 1.0, "kv" : -1.1111, "cosa" : -0.9},
  #{"kt" : 1.0, "kv" : -1.25, "cosa" : -0.8},
  #{"kt" : 1.0, "kv" : -1.42857, "cosa" : -0.7},
  #{"kt" : 1.0, "kv" : -1.6667, "cosa" : -0.6},
  #{"kt" : 1.0, "kv" : -2, "cosa" : -0.5},
  #{"kt" : 1.0, "kv" : -2.5, "cosa" : -0.4},
  #{"kt" : 1.0, "kv" : -3.333, "cosa" : -0.3},
  #{"kt" : 1.0, "kv" : -5, "cosa" : -0.2},
  #{"kt" : 1.0, "kv" : -10, "cosa" : -0.1},
  #{"kt" : 1.0, "kv" : -10000, "cosa" : 0.0001},
  #{"kt" : 1.0, "kv" : 10, "cosa" : 0.1},
  #{"kt" : 1.0, "kv" : 5, "cosa" : 0.2},
  #{"kt" : 1.0, "kv" : 3.333, "cosa" : 0.3},
  #{"kt" : 1.0, "kv" : 2.5, "cosa" : 0.4},
  #{"kt" : 1.0, "kv" : 2, "cosa" : 0.5},
  #{"kt" : 1.0, "kv" : 1.6667, "cosa" : 0.6},
  #{"kt" : 1.0, "kv" : 1.42857, "cosa" : 0.7},
  #{"kt" : 1.0, "kv" : 1.25, "cosa" : 0.8},
  #{"kt" : 1.0, "kv" : 1.1111, "cosa" : 0.9}
]

list_couplings = [
  {
    "name" : get_tH_weight_str(entry["kt"], entry["kv"], entry["cosa"]),
    "ratio" : entry["kt"]/entry["kv"],
    "name_out" : get_tH_weight_str_out(entry["kt"], entry["kv"], entry["cosa"])
  } for entry in tHweights
]

for ee, entry in enumerate(list_couplings) :
    cmd = "WriteDatacards.py "
    cmd += " --inputShapes %s"  % options.inputShapes
    cmd += " --channel %s"      % options.channel
    #cmd += " --cardFolder %s"   % options.cardFolder
    if options.shapeSyst : cmd += " --shapeSyst"
    cmd += " --noX_prefix"
    cmd += " --coupling %s"     % entry["name"]
    cmd += " --era %s"          % options.era
    if options.no_data : cmd += " --no_data"
    cmd += " --tH_kin"
    cmd += " --output_file %s/ttH_%s_%s_%s" % (options.cardFolder, channel_to_card, options.era, entry["name_out"].replace("A", ""))
    runCombineCmd(cmd)
