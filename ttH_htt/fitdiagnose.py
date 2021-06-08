from create_makefile_dependency import *
import argparse
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
cat = options.cat
channel = options.channel

era = '2016' if '/2016/' in input_path else '2017' if '/2017/' in input_path else '2018'

output_path = input_path[:input_path.rfind('/')] + '/' + 'fitdiagnostic/'
if not os.path.exists(output_path):
        os.makedirs(output_path)

makefile = os.path.join(output_path, "Makefile_fitdiagnostic")
stderr_file_path = os.path.join(output_path, "Makefile_fitdiagnostic_stderr.log")
stdout_file_path = os.path.join(output_path, "Makefile_fitdianostic_stdout.log")
phoniesToAdd = []
filesToClean = []
lines =[]


for m in mass:
    for s in spin:
        for c in cat:
            datacard = input_path + '/%s_%s_%s_lbn_%s_%s_%s.txt' %(c,m,s,channel,era,signal_type)
            output = '%s/%s_%s_%s_WS.root' %(output_path, c,m,s)
            ws_target = 'ws_%s_%s_%s' %(m,s,c)
            cmd = 'text2workspace.py %s -o %s/%s_%s_%s_WS.root' %(datacard, output_path, c,m,s)
            phoniesToAdd.append(ws_target)
            lines.append("%s: " %ws_target)
            lines.append("\t%s" %cmd)
            lines.append("\t")
            n = '_shapes_combine_%s_%s_%s' %(m,s,c)
            combine_target = 'combine_%s_%s_%s' %(m,s,c)
            cmd = "combineTool.py -M FitDiagnostics %s --saveShapes --saveWithUncertainties --saveNormalization --skipBOnlyFit --saveOverallShapes --cminDefaultMinimizerType Minuit2 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,0:1.0 -n %s" %(output, n)
            phoniesToAdd.append(combine_target)
            lines.append("%s:%s " %(combine_target,ws_target))
            lines.append("\t%s" %cmd)
            lines.append("\t")
            cmd = 'mv higgsCombine%s.FitDiagnostics.mH120.root %s' %(n, output_path)
            mv1_target = 'mv_%s_%s_%s' %(c,m,s)
            phoniesToAdd.append(mv1_target)
            lines.append("%s:%s " %(mv1_target, combine_target))
            lines.append("\t%s" %cmd)
            lines.append("\t")
            cmd = 'mv fitDiagnostics%s.root %s' %(n, output_path)
            mv2_target = 'mv_%s_%s_%s' %(c,m,s)
            phoniesToAdd.append(mv2_target)
            lines.append("%s:%s " %(mv2_target, combine_target))
            lines.append("\t%s" %cmd)
            lines.append("\t")


createMakefile(makefile, phoniesToAdd, lines, filesToClean=None, isSbatch=False, phoniesToAdd=phoniesToAdd)
run_cmd( "make -f %s -j %i 2>%s 1>%s" % \
         (makefile, 13, stderr_file_path, stdout_file_path),
         False
)


