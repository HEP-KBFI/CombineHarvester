from create_makefile_dependency import *
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--signal_type ", dest="signal_type", help="type of res/nonres", default='res', choices=['res', 'nonresLO', 'nonresNLO'])
parser.add_argument("--input_path ", dest="input_path",  help="path of addSystfile")

options = parser.parse_args()
input_path = options.input_path
mass = ['250', '260', '270', '300', '350', '400', '450', '500', '550', '600', '650', '700', '800', '900', '1000']
cat = ['H_resolved_2b', 'H_resolved_1b']
for m in mass:
    hists = []
    for c in cat:
        hists.append('%s/addSystFakeRates_hh_bb1l_LBN_%s_MVAOutput_%s_spin0.root' %(input_path, c,m))
    sf = ' '.join('%s' %h for h in hists)
    cmd = 'hadd -f addSystFakeRates_hh_bb1l_LBN_H_resolved_MVAOutput_%s_spin0.root %s' %(m, sf)
    os.system(cmd)
    cmd = 'mv addSystFakeRates_hh_bb1l_LBN_H_resolved_MVAOutput_%s_spin0.root %s' %(m, input_path)
    os.system(cmd)
