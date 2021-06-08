import argparse
import ROOT as r
import collections
import sys
import math

parser = argparse.ArgumentParser()
parser.add_argument("--signal_type ", dest="signal_type", help="type of res/nonres", default='res', choices=['res', 'nonresLO', 'nonresNLO'])
parser.add_argument("--mass ", dest="mass", nargs='+', help="mass", default=['300', '800'], choices=['300', '800', 'SM'])
parser.add_argument("--spin", type=str, dest="spin", nargs='+', help="spin", default=['spin0'], choices=['spin0', 'spin2', 'none'])
parser.add_argument("--input_path", type=str, dest="input_path", help="path of datacard text file")
parser.add_argument("--cat", type=str, dest="cat", nargs='+', help="event category", default=['all'], choices=['all', 'bkg'])
parser.add_argument("--channel", type=str, dest="channel", help="channel", default='1l_0tau', choices=['1l_0tau', '2l_0tau'])
parser.add_argument("--unblind", dest="unblind", help="unblind", default=False)

options = parser.parse_args()
signal_type = options.signal_type
mass = options.mass
input_path = options.input_path
spin = options.spin
unblind = options.unblind

SH = ['TTH', 'tHq', 'tHW', 'ggH', 'qqH', 'ZH', 'WH', 'TTWH', 'TTZH']
SHerror = r.Double()
SHyield = 0
dnn_node = ['TT_resolved', 'TT_boosted', 'W_resolved', 'W_boosted', 'Other', 'H_boosted', 'H_resolved_2b', 'H_resolved_1b', 'HH_boosted', 'HH_resolved_2b', 'HH_resolved_1b']
results = collections.OrderedDict()
total_results = collections.OrderedDict()
for dn in dnn_node:
  results[dn] = collections.OrderedDict()
  SHerror = r.Double()
  SHyield = 0
  f = r.TFile('%s/hadd_stage2_LBN_%s_Tight.root' %(input_path, dn))
  mdir = f.Get('hh_bb1l_Tight/sel/datacard/LBN/%s' %dn)
  samples = [s.GetName() for s in mdir.GetListOfKeys() if not (s.GetName().endswith(('_fake', '_Convs', '_hww', '_hzz', '_htt', '_hbb', '_bbzz', '_bbww', '_bbtt','fakes_mc')))]
  for sample in samples:   
    if 'signal' in sample:continue
    if '3000' in sample or 'spin2' in sample: continue                                                               
    s = mdir.Get(sample)
    hist = s.Get('MVAOutput_300_spin0')
    if sample in SH:
      error_ = r.Double()
      SHyield += hist.IntegralAndError(0, -1, error_)
      SHerror += error_**2
    else:                                   
      if sample in results[dn]:
        print 'found same sample twice'
        sys.exit()
      else:
        error = r.Double()
        yield_ = hist.IntegralAndError(0, -1, error)
        results[dn][sample] = (yield_, error)
      if sample not in total_results:
        total_results[sample] = (yield_, error**2)
      else:
        total_results[sample] = (total_results[sample][0]+yield_, total_results[sample][1]+error**2)
  results[dn]['SingleHiggs'] = (SHyield, math.sqrt(SHerror))
  if 'SingleHiggs' not in total_results:
    total_results['SingleHiggs'] = (SHyield, SHerror)
  else:
    total_results['SingleHiggs'] = (total_results['SingleHiggs'][0]+SHyield, total_results['SingleHiggs'][1]+SHerror)

maxlen = max(list(map(lambda x: len(x), results[dn].keys())))
for dn in dnn_node:
  print dn
  sorted_result = list(sorted([(kk, vv) for kk, vv in results[dn].items()], key=lambda kv: kv[1], reverse=True))
  for k, v in sorted_result:
    if not unblind and k=='data_obs': continue
    print ('{:>{len}} {:.3f} +- {:.3f}'.format(k, v[0], v[1], len=maxlen))
  print('\n')

sorted_total_result = list(sorted([(kk, vv) for kk, vv in total_results.items()], key=lambda kv: kv[1], reverse=True))
print ('total yield')
for k,v in sorted_total_result:
  if not unblind and k=='data_obs': continue
  print('{:>{len}} {} +- {}'.format(k, v[0], math.sqrt(v[1]), len=maxlen))
