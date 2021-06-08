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

options = parser.parse_args()
signal_type = options.signal_type
mass = options.mass
input_path = options.input_path
spin = options.spin

f = r.TFile(input_path)
SH = ['TTH', 'tHq', 'tHW', 'ggH', 'qqH', 'ZH', 'WH', 'TTWH', 'TTZH']
SHerror = r.Double()
SHyield = 0
mdir = f.Get('hh_bb1l_Tight/sel/evt')
results = collections.OrderedDict()
samples = [s.GetName() for s in mdir.GetListOfKeys() if not (s.GetName().endswith(('_fake', '_Convs')))]
for sample in samples:
  if 'signal' in sample and not ('300' in sample or '800' in sample): continue
  if '3000' in sample: continue
  s = mdir.Get(sample)
  hist = s.Get('HT')
  if sample in SH:
      error_ = r.Double()
      SHyield += hist.IntegralAndError(0, -1, error_)
      SHerror += error_**2
  else:
    if sample in results:
      print 'found same sample twice'
      sys.exit()
    else:
      error = r.Double()
      yield_ = hist.IntegralAndError(0, -1, error)
      results[sample] = (yield_, error)

results['SingleHiggs'] = (SHyield, math.sqrt(SHerror))
total = sum(v[0] for k, v in results.items() if not k.startswith(('data_obs', 'signal')))
total_error = math.sqrt(sum(v[1]**2 for k, v in results.items() if not k.startswith(('data_obs', 'signal'))))
results['total_BKG'] = (total, total_error)
sort_result = list(sorted([(kk, vv) for kk, vv in results.items()], key = lambda kv: kv[1], reverse = True))
maxlen = max(list(map(lambda x: len(x), results.keys())))

for k,v in sort_result:
  if 'signal' in k or 'fakes_mc' in k or k.startswith(('total', 'data_obs')): continue
  print ('{:>{len}} {:.3f} +- {:.3f}'.format(k, v[0], v[1], len=maxlen))
for k,v in sort_result:
  if 'signal' not in k: continue
  print ('{:>{len}} {:.3f} +- {:.3f}'.format(k, v[0], v[1], len=maxlen))
for k,v in sort_result:
  if not k.startswith(('total', 'data_obs')): continue
  print ('{:>{len}} {:.3f} +- {:.3f}'.format(k, v[0], v[1], len=maxlen))
