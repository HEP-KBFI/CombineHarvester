from create_makefile_dependency import *
from optparse import OptionParser
import glob
parser = OptionParser()
parser.add_option("--method ", dest="method", help="type of res/nonres", default='lbn', choices=['bdt', 'lbn'])
parser.add_option("--era ", dest="era", help="era", default='2018', choices=['2016', '2017', '2018'])
parser.add_option("--signal_type ", dest="signal_type", help="nonresLO or nonresNLO or res to be considered", default='nonresNLO', choices=['res', 'nonresNLO', 'nonresLO'])
parser.add_option("--spin ", dest="spin", help="spin to be considered", default='spin0', choices=['spin0', 'spin2'])
parser.add_option("--input_path", type='string', dest="input_path", help="path of preparedatacard file")
parser.add_option("--output_path", type='string', dest="output_path", help="path of output datacard.txt file")
parser.add_option("--channel", dest="channel", help="which channel is considering", default = '1l_0tau')
parser.add_option("--run", dest="run_combine", action="store_true", help="want to run combine command", default = False)
(options, args) = parser.parse_args()
method = options.method
era = options.era
print era
signal_type = options.signal_type
spin = options.spin
inputdir = options.input_path
output_path = options.output_path
channel = options.channel
dir_ = output_path
run_combine = options.run_combine
proc=subprocess.Popen(['mkdir %s' % dir_],shell=True,stdout=subprocess.PIPE)
if signal_type == 'nonresNLO':
    modes = ['SM']
elif signal_type == 'res':
    #modes = ['250', '260', '270', '300', '350', '400', '450', '500', '550', '600', '650', '700', '800', '1000', '900']
    #modes = ['400_overlap', '450_overlap']
    modes = ['300']
else:
    modes = ['SM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5', 'BM6', 'BM7', 'BM8', 'BM9', 'BM10', 'BM11', 'BM12']
evtcats = []
'''if signal_type in ['nonresNLO', 'nonresLO']:
    evtcats.extend(['HH_resolved_1b_nonvbf', 'HH_resolved_2b_vbf', 'HH_resolved_1b_vbf', 
                'HH_resolved_2b_nonvbf', 'HH_boosted_vbf', 'HH_boosted_nonvbf'])
else:
    evtcats.extend(['HH_boosted', 'HH_resolved_2b', 'HH_resolved_1b'])'''
evtcats.extend(['DY_resolved', 'DY_boosted', 'TT_resolved', 'TT_boosted', 'SingleTop_resolved',
                'SingleTop_boosted','Other', 'W_resolved', 'W_boosted',
                'H_boosted', 'H_resolved_2b', 'H_resolved_1b'])
if channel == '2l_0tau':
    evtcats.remove('W_resolved')
    evtcats.remove('W_boosted')
    evtcats.remove('H_resolved_2b')
    evtcats.remove('H_resolved_1b')
    evtcats.remove('H_boosted')
if channel == '1l_0tau':
    evtcats.remove('DY_resolved')
    evtcats.remove('DY_boosted')
    evtcats.remove('SingleTop_resolved')
    evtcats.remove('SingleTop_boosted')
phoniesToAdd = []
lines =[]
for mode in modes:
    if signal_type == 'res':
        mode += '_' + spin
    cmd = 'combineCards.py '
    for evtcat in evtcats:
        datacard = glob.glob('%s/*_%s_*%s*%s_final*txt' %(inputdir, evtcat, mode, signal_type))[0]
        print datacard
        cmd+= ' %s=%s ' %(evtcat, datacard)
    cmd += " >%s/%s_%s_%s_%s_%s.txt" %(output_path, mode, method, channel, era, signal_type)
    print cmd

    p=subprocess.Popen(['%s' %cmd],shell=True,stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stderr:
        print stderr
    if run_combine:
        makefile = os.path.join(output_path, 'Makefile_combine')
        make_stdout = os.path.join(output_path, 'Makefile_combine_stdout')
        make_stderr = os.path.join(output_path, 'Makefile_combine_stderr')
        target = 'combine_%s' %mode
        phoniesToAdd.append(target)
        cmd = "combineTool.py  -M AsymptoticLimits  -t -1 -n %s %s/%s_%s_%s_%s_%s.txt >%s/%s_%s_%s_%s.log" % (mode, output_path, mode, method, channel, era, signal_type, output_path, mode, method, channel, era)
        lines.append('%s:' %target)
        lines.append('\t%s\n' %cmd)
        cmd2 = "mv higgsCombine%s.AsymptoticLimits.mH120.root %s/" %(mode, output_path)
        target = 'mv_%s' %mode
        phoniesToAdd.append(target)
        lines.append('%s:combine_%s' %(target,mode))
        lines.append('\t%s\n' %cmd2)
if run_combine:
    createMakefile(makefile, phoniesToAdd, lines, filesToClean=None, isSbatch=False, phoniesToAdd=phoniesToAdd)
    run_cmd( "make -f %s -j %i 2>%s 1>%s" % \
             (makefile, 14, make_stderr, make_stdout),
             False)
