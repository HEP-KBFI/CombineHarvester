import glob
from create_makefile_dependency import *
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--method ", dest="method", help="type of training", default='lbn', choices=['lbn', 'bdt'])
parser.add_argument("--spin ", dest="spin", help="spin to be considered", default='spin0', choices=['spin0', 'spin2'])
parser.add_argument("--signal_type ", dest="signal_type", help="nonresLO or nonresNLO or res to be considered", default='nonresNLO', choices=['res', 'nonresNLO', 'nonresLO'])
parser.add_argument("--input_path", type=str, dest="input_path", help="path of preparedatacard file")
parser.add_argument("--output_path", type=str, dest="output_path", help="path of output datacard.txt file")
parser.add_argument("--channel", dest="channel", help="which channels to be considered", default='1l_0tau')
parser.add_argument("--drawLimitsOnly", action="store_true", dest="drawLimitsOnly", help="will do the plot for a particular bin")
parser.add_argument("--do_signalFlat", action="store_false", dest="do_signalFlat", help="whether want to signal flat", default=True)
parser.add_argument("--do_signalFlat_only", action="store_true", dest="do_signalFlat_only", help="whether want to signal flat only")
parser.add_argument("--cat", type=str, nargs='+', dest="special_category", help="which special category to be considered", default='all')
parser.add_argument("--rebinning", action="store_true", dest="rebinning", help="whether want to rebinning the histogram", default=False)
parser.add_argument("--run", dest="run_combine", action="store_true", help="want to run combine command", default = False)
parser.add_argument("--writedatacard", dest="writedatacard", action="store_true", help="want to create new datacard", default = False)

options = parser.parse_args()
method = options.method
spin = options.spin
signal_type = options.signal_type
input_path = options.input_path
output_path = options.output_path
channel = options.channel
drawLimitsOnly = options.drawLimitsOnly
do_signalFlat = options.do_signalFlat
do_signalFlat_only =options.do_signalFlat_only
cat = options.special_category
rebinning = options.rebinning
run_combine = options.run_combine
writedatacard = options.writedatacard

era = '2016' if '/2016/' in input_path else '2017' if '/2017/' in input_path else '2018'

output_path += '/%s/%s' %(era, signal_type)
if signal_type == "res":
    output_path += "/%s" %spin
if not os.path.exists(output_path):
        os.makedirs(output_path)

if signal_type == 'nonresNLO':
    modes = ['SM']
elif signal_type == 'nonresLO':
    modes = ['SM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5', 'BM6', 'BM7', 'BM8', 'BM9', 'BM10', 'BM11', 'BM12']
else:
    #modes = ['400_overlap', '450_overlap']
    #modes = ['260', '270', '300', '350', '400', '450', '500', '550', '600', '650', '700', '800', '1000', '900']
    modes = ['300', '800']

allsubcat = []
sigcat = []
if signal_type == 'res':
    sigcat.extend( ['HH_resolved_1b', 'HH_resolved_2b', 'HH_boosted'] )
else:
    sigcat.extend( ['HH_resolved_1b_nonvbf', 'HH_resolved_2b_vbf', 'HH_resolved_1b_vbf', 'HH_resolved_2b_nonvbf', 'HH_boosted_vbf', 'HH_boosted_nonvbf'] )
allsubcat.extend(sigcat)
bkgcat = ['Other', 'DY_resolved', 'DY_boosted', 'W', 'TT_resolved', 'TT_boosted', 'SingleTop_resolved',\
          'SingleTop_boosted', 'H_boosted', 'H_resolved']#_2b', 'H_resolved_1b']

append = ''
if channel == '2l_0tau':
    append = 'dl'
    if 'W_resolved' in bkgcat:
        bkgcat.remove('W_resolved')
    if 'W_boosted' in bkgcat:
        bkgcat.remove('W_boosted')
elif channel == '1l_0tau':
    append = 'sl'
    if 'DY_resolved' in bkgcat:
        bkgcat.remove('DY_resolved')
    if 'DY_boosted' in bkgcat:
        bkgcat.remove('DY_boosted')
    if 'SingleTop_resolved' in bkgcat:
        bkgcat.remove('SingleTop_resolved')  
    if 'SingleTop_boosted' in bkgcat:
        bkgcat.remove('SingleTop_boosted')

allsubcat.extend(bkgcat)

if cat[0] == "bkg":
    allsubcat = list( set(allsubcat) - set(sigcat) )
elif cat[0] == "sig":
    allsubcat = list( set(allsubcat) - set(bkgcat) )
elif cat[0] != 'all':
    allsubcat = cat

makefile = os.path.join(output_path, "Makefile_%s_%s_%s_%s" %(channel, method, era, signal_type))
stderr_file_path = os.path.join(output_path, "Makefile_%s_%s_%s_%s_stderr.log" %(channel, method, era, signal_type))
stdout_file_path = os.path.join(output_path, "Makefile_%s_%s_%s_%s_stdout.log" %(channel, method, era, signal_type))
phoniesToAdd = []
filesToClean = []
lines =[]
mass = "none"

if rebinning or writedatacard:
    for subcats in allsubcat:
        for mode in modes:
            BDTfor = mode
            if signal_type == 'res':
                mass = spin + '_' + mode
                BDTfor = mode + '_' + spin
            cmd = 'python test/rebin_datacards_HH_v1.py --channel %s  --signal_type %s --mass %s  --HHtype bbWW%s --era %s --prepareDatacards_path %s --output_path %s --subcats %s --BDTfor %s --BINtype quantiles ' %(channel, signal_type, mass, append, era, input_path, output_path,subcats, BDTfor)
            if rebinning:
                cmd += ' --rebinning'
            if do_signalFlat:
                cmd += ' --do_signalFlat'
            elif do_signalFlat_only:
                cmd += ' --do_signalFlat_only'
            if drawLimitsOnly:
                cmd += ' --drawLimitsOnly '
            cmd += ' 1> %s_%s_out.txt 2> %s_%s_err.txt' %(output_path +'/'+subcats, mode, output_path+'/'+subcats,mode)
            target = "%s_%s_%s" %(mode, spin, subcats) if signal_type == 'res' else "%s_%s" %(mode, subcats)
            addToMakefile_analyze(lines, phoniesToAdd, cmd, target)

input_path = output_path + '/datacards_rebined'
combine_datacard_path = output_path + '/combine/datacard/'
if not os.path.exists(combine_datacard_path):
    os.makedirs(combine_datacard_path)

if len(cat) == 1:
    if cat[0] == 'sig':
        allsubcat.extend(bkgcat)
        append = 'all'
    else:
        append = cat[0]
else:
    append = '_'.join(c for c in cat)

for mode in modes:
    if signal_type == 'res':
        mode += '_' + spin
    combine_datacard = combine_datacard_path + append + '_%s_%s_%s_%s_%s.txt' %(mode, method, channel, era, signal_type)
    cmd = 'combineCards.py '
    for subcat in allsubcat:
        datacard = glob.glob('%s/*_%s_MVAOutput_*%s*%s_final*txt' %(input_path, subcat, mode, signal_type))
        print '***************', datacard
        if len(datacard) == 0:
            print 'final datacard root file is not fixed yet for %s_%s, cant run combine' %(subcat, mode)
            break
        datacard = datacard[0]
        cmd+= ' %s=%s ' %(subcat, datacard)
    if cmd == 'combineCards.py ':
        break
    cmd += " >%s" %combine_datacard
    if rebinning or writedatacard:
        dep = ' '.join('%s_%s' %(mode,c) for c in allsubcat)
    else:
        dep = '' 
    datacard_target = "combine_datacard_%s" %(mode)
    addToMakefile_analyze(lines, phoniesToAdd, cmd, datacard_target, dep)

    if run_combine:
        limit_path = output_path + '/combine/limits/'
        if not os.path.exists(limit_path):
            os.makedirs(limit_path)
        limit_target = 'limit_%s' %mode
        cmd = "combineTool.py  -M AsymptoticLimits  -t -1 -n %s %s/all_%s_%s_%s_%s_%s.txt >%s/%s_%s_%s_%s.log" % (mode, combine_datacard_path, mode, method, channel, era, signal_type, limit_path, mode, method, channel, era)
        addToMakefile_analyze(lines, phoniesToAdd, cmd, limit_target,datacard_target)
        cmd2 = "mv higgsCombine%s.AsymptoticLimits.mH120.root %s/" %(mode, limit_path)
        target = 'mv_%s' %mode
        addToMakefile_analyze(lines, phoniesToAdd, cmd2, target, limit_target)

createMakefile(makefile, phoniesToAdd, lines, filesToClean=None, isSbatch=False, phoniesToAdd=phoniesToAdd)
run_cmd( "make -f %s -j %i 2>%s 1>%s" % \
   (makefile, 16, stderr_file_path, stdout_file_path),
   False)
