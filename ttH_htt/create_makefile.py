from create_makefile_dependency import *
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--method ", dest="method", help="type of res/nonres", default='lbn', choices=['lbn', 'bdt'])
parser.add_option("--era ", dest="era", help="era", default='2016', choices=['2016', '2017', '2018'])
parser.add_option("--spin ", dest="spin", help="spin to be considered", default='spin0', choices=['spin0', 'spin2'])
parser.add_option("--signal_type ", dest="signal_type", help="nonresLO or nonresNLO or res to be considered", default='nonresNLO', choices=['res', 'nonresNLO', 'nonresLO'])
parser.add_option("--input_path", type='string', dest="input_path", help="path of preparedatacard file")
parser.add_option("--output_path", type='string', dest="output_path", help="path of output datacard.txt file")
parser.add_option("--channel", dest="channel", help="which channels to be considered", default='1l_0tau')
parser.add_option("--drawLimitsOnly", action="store_true", dest="drawLimitsOnly", help="will do the plot for a particular bin")
parser.add_option("--append",      type="string", dest="append",   help="DL or SL", default="sl")
parser.add_option("--do_signalFlat", action="store_true", dest="do_signalFlat", help="whether want to signal flat")
parser.add_option("--do_signalFlat_only", action="store_true", dest="do_signalFlat_only", help="whether want to signal flat only")
(options, args) = parser.parse_args()
method = options.method
era = options.era
spin = options.spin
signal_type = options.signal_type
input_path = options.input_path
output_path = options.output_path
channel = options.channel
drawLimitsOnly = options.drawLimitsOnly
do_signalFlat = options.do_signalFlat
do_signalFlat_only =options.do_signalFlat_only
append = options.append
dir_ = "create_make_files"
proc=subprocess.Popen(['mkdir %s' % dir_],shell=True,stdout=subprocess.PIPE)
if signal_type == 'nonresNLO':
    modes = ['SM']
elif signal_type == 'nonresLO':
    modes = ['SM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5', 'BM6', 'BM7', 'BM8', 'BM9', 'BM10', 'BM11', 'BM12']
else:
    #modes = ['400_overlap', '450_overlap']
    #modes = ['250', '260', '270', '280', '350', '400', '450', '500', '550', '600', '650', '700', '1000', '900']
    modes = ['300']
allsubcat = []
'''if signal_type == 'res':
    allsubcat.extend( ['HH_resolved_1b', 'HH_resolved_2b', 'HH_boosted'] )
else:
    allsubcat.extend( ['HH_resolved_1b_nonvbf', 'HH_resolved_2b_vbf', 'HH_resolved_1b_vbf', 'HH_resolved_2b_nonvbf', 'HH_boosted_vbf', 'HH_boosted_nonvbf'] )'''
allsubcat.extend(['Other', 'DY_resolved', 'DY_boosted', 'W_resolved', 'W_boosted', 'TT_resolved', 'TT_boosted', 'SingleTop_resolved', \
                  'SingleTop_boosted', 'H_resolved_2b', 'H_resolved_1b', 'H_boosted'] )

if channel == '2l_0tau':
    if 'W_resolved' in allsubcat:
        allsubcat.remove('W_resolved')
    if 'W_boosted' in allsubcat:
        allsubcat.remove('W_boosted')
elif channel == '1l_0tau':
    if 'DY_resolved' in allsubcat:
        allsubcat.remove('DY_resolved')
    if 'DY_boosted' in allsubcat:
        allsubcat.remove('DY_boosted')
    if 'SingleTop_resolved' in allsubcat:
        allsubcat.remove('SingleTop_resolved')  
    if 'SingleTop_boosted' in allsubcat:
        allsubcat.remove('SingleTop_boosted')
makefile = os.path.join(dir_+"/Makefile_%s_%s_%s_%s" %(channel, method, era, signal_type))
stderr_file_path = os.path.join(dir_+"/Makefile_%s_%s_%s_%s_stderr.log" %(channel, method, era, signal_type))
stdout_file_path = os.path.join(dir_+"/Makefile_%s_%s_%s_%s_stdout.log" %(channel, method, era, signal_type))
phoniesToAdd = []
filesToClean = []
lines =[]
mass = "none"
for subcats in allsubcat:
    for mode in modes:
        BDTfor = mode
        if signal_type == 'res':
            mass = spin + '_' + mode
            BDTfor = mode + '_' + spin
        cmd = 'python test/rebin_datacards_HH_v1.py --channel %s  --signal_type %s --mass %s  --HHtype bbWW%s --era %s --prepareDatacards_path %s --output_path %s --subcats %s --BDTfor %s --BINtype quantiles ' %(channel, signal_type, mass, append, era, input_path, output_path,subcats, BDTfor)
        if do_signalFlat:
            cmd += ' --do_signalFlat'
        elif do_signalFlat_only:
            cmd += ' --do_signalFlat_only'
        if drawLimitsOnly:
            cmd += ' --drawLimitsOnly '
        cmd += ' 1> %s_%s_out.txt 2> %s_%s_err.txt' %(dir_+'/'+subcats, mode, dir_+'/'+subcats,mode)
        target = "%s_%s" %(mode, subcats)
        phoniesToAdd.append(target)
        lines.append("%s: " %target)
        lines.append("\t%s" %cmd)
        lines.append("\t")
createMakefile(makefile, phoniesToAdd, lines, filesToClean=None, isSbatch=False, phoniesToAdd=phoniesToAdd)
run_cmd( "make -f %s -j %i 2>%s 1>%s" % \
         (makefile, 17, stderr_file_path, stdout_file_path),
         False
)


