#!/usr/bin/env python
import os, shlex
from subprocess import Popen, PIPE
import glob
import shutil
import ROOT
from collections import OrderedDict

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--inputPaths", type="string", dest="inputPaths", help="Full path of where prepareDatacards.root are ")
parser.add_option("--kls", type="string", dest="kls", help="Full path of where prepareDatacards.root are ")
parser.add_option("--kts", type="string", dest="kts", help="Full path of where prepareDatacards.root are ")
parser.add_option("--c2s", type="string", dest="c2s", help="Full path of where prepareDatacards.root are ")
parser.add_option("--outPath", type="string", dest="outPath", help="Full path of where prepareDatacards.root are ")
parser.add_option("--smFromLO", action='store_true',dest="smFromLO", default=False)
(options, args) = parser.parse_args()

inputPaths = options.inputPaths.split(":")
kls = options.kls.split(":")
kts = options.kts.split(":")
c2s = options.c2s.split(":")
outPath = options.outPath
smFromLO = options.smFromLO

print c2s, kls, kts
A13tev = [62.5088, 345.604, 9.63451, 4.34841, 39.0143, -268.644, -44.2924, 96.5595, 53.515, -155.793, -23.678, 54.5601, 12.2273, -26.8654, -19.3723, -0.0904439, 0.321092, 0.452381, -0.0190758, -0.607163, 1.27408, 0.364487, -0.499263] # from https://github.com/pmandrik/VSEVA/blob/master/HHWWgg/reweight/reweight_HH.C#L117

def functionGF(kl,kt,c2,cg,c2g,A): 
    return A[0] * kt**4 + \
    A[1] * c2**2 + \
    A[2] * kt**2 * kl**2 + \
    A[3] * cg**2 * kl**2 + \
    A[4] * c2g**2 + \
    A[5] * c2 * kt**2 + \
    A[6] * kl * kt**3 + \
    A[7] * kt * kl * c2 + \
    A[8] * cg * kl * c2 + \
    A[9] * c2 * c2g + \
    A[10] * cg * kl * kt**2 + \
    A[11] * c2g * kt**2 + \
    A[12] * kl**2 * cg * kt + \
    A[13] * c2g * kt * kl + \
    A[14] * cg * c2g * kl + \
    A[15] * kt**3 * cg + \
    A[16] * kt * c2 * cg + \
    A[17] * kt * cg**2 * kl + \
    A[18] * cg * kt * c2g + \
    A[19] * kt**2 * cg**2 + \
    A[20] * c2 * cg**2 + \
    A[21] * cg**3 * kl + \
    A[22] * cg**2 * c2g


def getTotalXS(kl, kt, c2, cg, c2g):
    return functionGF(kl,kt,c2,cg,c2g,A13tev)

def copyProcs(inputShapesL,inputShapesLnew, kl, kt, c2, base= False) :
    scenario = 'kl_'+kl + '_kt_' + kt +'_c2_'+c2
    scenario = scenario.replace('-','m')
    scenario = scenario.replace('.','p')
    tfileout1 = ROOT.TFile(inputShapesL, "READ")
    rootmode = "UPDATE"
    if base: rootmode = "RECREATE"
    tfileout2 = ROOT.TFile(inputShapesLnew, rootmode)
    tfileout1.cd()

    for nkey, key in enumerate(tfileout1.GetListOfKeys()) :
        obj =  key.ReadObj()
        obj_name = key.GetName()
        if type(obj) is not ROOT.TH1F :
            if type(obj) is ROOT.TH1 :
                print ("data_obs can be be TH1")
                continue
            else :
                print ("WARNING: All the histograms that are not data_obs should be TH1F - otherwhise combine will crash!!!")
                sys.exit()
        if not (base or 'ggHH_h' in obj_name):
            continue
        if ('ggHH_kl_1_kt_1' in obj_name or 'kl_0_kt_1' in obj_name) and smFromLO:
            continue
        obj_newname = obj_name
        if 'kl_2p45_kt_1' in obj_name: obj_newname = obj_newname.replace('kl_2p45_kt_1','kl_2p45_kt_1p00_c2_0p00')
        if 'kl_5_kt_1' in obj_name: obj_newname = obj_newname.replace('kl_5_kt_1','kl_5p00_kt_1p00_c2_0p00')
        if 'kl_0_kt_1' in obj_name: obj_newname = obj_newname.replace('kl_0_kt_1','kl_0p00_kt_1p00_c2_0p00')
        if 'kl_1_kt_1' in obj_name: obj_newname = obj_newname.replace('kl_1_kt_1','kl_1p00_kt_1p00_c2_0p00')
        if 'ggHH_h' in obj_name:
            obj_newname = obj_newname.replace('ggHH_h', 'ggHH_'+scenario+'_h')
        tfileout2.cd()
        nominal = obj.Clone()
        nominal.SetName( obj_newname )
        if 'ggHH_h' in obj_name:
            nominal.Scale(1.115*getTotalXS(float(kl),float(kt),float(c2),0.,0.)/1000.)
        nominal.Write()
        tfileout1.cd()
    tfileout1.Close()
    tfileout2.Close()

if (len(inputPaths) is not len(kls)) or (len(inputPaths) is not len(kts)) or (len(inputPaths) is not len(c2s)):
    raise AttributeError('All inputs must have the same length!')
for i,inputPath in enumerate(inputPaths):
    base = False
    if i is 0: base = True
    kl = kls[i]
    kt = kts[i]
    c2 = c2s[i]
    copyProcs(inputPath,outPath, kl, kt, c2, base)
    
