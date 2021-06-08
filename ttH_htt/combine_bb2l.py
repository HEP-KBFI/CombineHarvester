from create_makefile_dependency import *
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--method ", dest="method", help="type of res/nonres", default='lbn', choices=['bdt', 'lbn'])
parser.add_option("--era ", dest="era", help="era", default='2018', choices=['2016', '2017', '2018'])
parser.add_option("--input_path", type='string', dest="input_path", help="path of preparedatacard file")
parser.add_option("--output_path", type='string', dest="output_path", help="path of output datacard.txt file")
parser.add_option("--channel", dest="channel", help="which channel is considering", default = '2l_0tau')
parser.add_option("--combine", action='store_true', dest="run_combine", help="run combine command", default = False)
(options, args) = parser.parse_args()
method = options.method
era = options.era
input_path = options.input_path
output_path = options.output_path
channel = options.channel
combine = options.run_combine
dir_ = output_path
proc=subprocess.Popen(['mkdir %s' % dir_],shell=True,stdout=subprocess.PIPE)

makefile = os.path.join(dir_+"/Makefile_combine_%s" %era)
stderr_file_path = os.path.join(dir_+"/Makefile_combine_%s_stderr.log" %era)
stdout_file_path = os.path.join(dir_+"/Makefile_combine_%s_stdout.log" %era)
phoniesToAdd = []
filesToClean = []
lines =[]
modes = ['allBMs']#, 'BM1', 'BM2', 'BM3', 'BM4', 'BM5', 'BM6', 'BM7', 'BM8', 'BM9', 'BM10', 'BM11', 'BM12']
firstpart ='/home/snandan/hh_Analysis/CombineHarvestr/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/dumb_bb2l_allBM/datacards_rebined//datacard_hh_bb2l_BDT'
lastpart = 'quantiles_10bins_quantiles.txt'
lastpart_resolved_2b_vbf = 'quantiles_5bins_quantiles.txt'
lastpart_boosted = 'quantiles_4bins_quantiles.txt'
makefile = os.path.join(dir_+"/Makefile_combine_%s_%s" %(method, era))
stderr_file_path = os.path.join(dir_+"/Makefile_combine_%s_%s_stderr.log" %(method, era))
stdout_file_path = os.path.join(dir_+"/Makefile_combine_%s_%s_stdout.log" %(method, era))
phoniesToAdd = []
filesToClean = []
lines =[]

for mode in modes:
    if method == 'bdt':
        cmd = 'combineCards.py resolved_2b_vbf=%s_resolved_2b_vbf_OS_MVAOutput_%s_%s resolved_2b_nonvbf=%s_resolved_2b_nonvbf_OS_MVAOutput_%s_%s resolved_1b=%s_resolved_1b_OS_MVAOutput_%s_%s boosted=%s_boosted_OS_MVAOutput_%s_%s' %(firstpart, mode, lastpart_resolved_2b_vbf, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart_boosted)
    else:
        cmd = 'combineCards.py HH_resolved_2b_vbf=%s_HH_resolved_2b_vbf_OS_MVAOutput_%s_%s HH_resolved_2b_nonvbf=%s_HH_resolved_2b_nonvbf_OS_MVAOutput_%s_%s HH_resolved_1b=%s_HH_resolved_1b_OS_MVAOutput_%s_%s HH_boosted=%s_HH_boosted_OS_MVAOutput_%s_%s TT_resolved=%s_TT_resolved_OS_MVAOutput_%s_%s TT_boosted=%s_TT_boosted_OS_MVAOutput_%s_%s W_resolved=%s_W_resolved_OS_MVAOutput_%s_%s W_boosted=%s_W_boosted_OS_MVAOutput_%s_%s DY_resolved=%s_DY_resolved_OS_MVAOutput_%s_%s DY_boosted=%s_DY_boosted_OS_MVAOutput_%s_%s SingleTop_resolved=%s_SingleTop_resolved_OS_MVAOutput_%s_%s SingleTop_boosted=%s_SingleTop_boosted_OS_MVAOutput_%s_%s Other=%s_Other_OS_MVAOutput_%s_%s' %(firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart, firstpart, mode, lastpart)
    cmd += " >%s/%s_%s_%s_%s.txt" %(output_path, mode, method, channel, era)
    target = "%s" %mode
    phoniesToAdd.append(target)
    lines.append("%s: " %target)
    lines.append("\t%s" %cmd)
    lines.append("\t")
    if combine:
        phoniesToAdd.append(target+'_combine')
        lines.append("%s_combine:%s " %(target,target))
        cmd1 = "combineTool.py  -M AsymptoticLimits  -t -1 %s/%s_%s_%s_%s.txt >%s/%s_%s_%s_%s.log" % (output_path, mode, method, channel, era, output_path, mode, method, channel, era)
        lines.append("\t%s" %cmd1)
        lines.append("\t")
createMakefile(makefile, phoniesToAdd, lines, filesToClean=None, isSbatch=False, phoniesToAdd=phoniesToAdd)
run_cmd( "make -f %s -j %i 2>%s 1>%s" % \
        (makefile, 13, stderr_file_path, stdout_file_path),
        False
)


