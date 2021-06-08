import argparse
from create_makefile_dependency import *
import os

parser = argparse.ArgumentParser()
parser.add_argument("--method ", dest="method", help="type of training", default='lbn', choices=['lbn', 'bdt'])
parser.add_argument("--spin ", dest="spin", help="spin to be considered", default='spin0', choices=['spin0', 'spin2'])
parser.add_argument("--mass ", dest="mass", help="mass to be considered", nargs='+', default=['300','800'], choices=['300', '800'])
parser.add_argument("--signal_type ", dest="signal_type", help="nonresLO or nonresNLO or res to be considered", default='res', choices=['res', 'nonresNLO', 'nonresLO'])
parser.add_argument("--input_path", type=str, dest="input_path", help="path of finaldatacard txt.file for one era")
parser.add_argument("--output_path", type=str, dest="output_path", help="path of output datacard.txt file")
parser.add_argument("--channel", dest="channel", help="which channels to be considered", default='1l_0tau')
parser.add_argument("--cat", type=str, nargs='+', dest="special_category", help="which special category to be considered", default=['all', 'bkg'])
parser.add_argument("--fitdiagnostic", dest="fit", help="run fitdiagnostic", action='store_true', default=False)
options = parser.parse_args()
method = options.method
spin = options.spin
mass = options.mass
signal_type = options.signal_type
input_path = options.input_path
output_path = options.output_path
channel = options.channel
cat = options.special_category
fit = options.fit

output_path += '/Run2_woelephant_wWmerged/%s' %(signal_type)
if signal_type == "res":
    output_path += "/%s" %spin
if not os.path.exists(output_path):
        os.makedirs(output_path)
era = '2016' if '/2016/' in input_path else '2017' if '/2017/' in input_path else '2018'
path_2016 = input_path.replace(era, '2016')
path_2017 = input_path.replace(era, '2017')
path_2018 = input_path.replace(era, '2018')

makefile = os.path.join(output_path, "Makefile_%s_%s_%s_%s" %(channel, method, era, signal_type))
stderr_file_path = os.path.join(output_path, "Makefile_%s_%s_%s_%s_stderr.log" %(channel, method, era, signal_type))
stdout_file_path = os.path.join(output_path, "Makefile_%s_%s_%s_%s_stdout.log" %(channel, method, era, signal_type))
phoniesToAdd = []
lines =[]

for m in mass:
    for c in cat:
        datacard = '%s/%s_%s_%s_%s_%s_%s_%s.txt' %(path_2016, c, m, spin, method, channel, era, signal_type)
        cmd = 'combineCards.py era_2016=%s ' %datacard
        datacard = datacard.replace('2016', '2017')
        cmd += 'era_2017=%s ' %datacard
        datacard = datacard.replace('2017', '2018')
        cmd += 'era_2018=%s ' %datacard
        combinecard = 'combine_%s_%s_%s.txt' % (c, m, spin)
        cmd += ' >%s/%s' %(output_path, combinecard)
        os.system(cmd)
        with open(os.path.join(output_path,combinecard), 'r') as f:
            line = f.read()
            line = line.replace(path_2016, '')
            line = line.replace(path_2017, '')
            line = line.replace(path_2018, '')
            f.close()
        with open(os.path.join(output_path,combinecard), 'w') as f:
            f.write(line)
        if fit:
            #addToMakefile_analyze(lines, phoniesToAdd, 'ulimit -s unlimited', 'ulimit')
            output_path_fit = output_path + '/fitdiagnostic'
            if not os.path.exists(output_path_fit):
                os.makedirs(output_path_fit)
            #target = 'ws_%s_%s' %(c, m)
            output = '%s/%s' %(output_path_fit, combinecard.replace('.txt', '_WS.root'))
            '''cmd = 'text2workspace.py %s/%s -o %s' %(output_path, combinecard, output)
            addToMakefile_analyze(lines, phoniesToAdd, cmd, target, 'ulimit')'''
            n = '_shapes_combine_%s_%s' %(m,c)
            combine_target = 'combine_%s_%s' %(m,c)
            cmd = "combineTool.py -M FitDiagnostics %s --verbose 3 --redefineSignalPOIs r --setParameters r=1.0 --setParameterRanges r=-1000,1000 --saveShapes --saveWithUncertainties --saveNormalization --saveOverallShapes --saveWorkspace --saveToys --saveNLL --cminFallbackAlgo Minuit2,0:1.0 --X-rtd MINIMIZER_no_analytic --keepFailures --ignoreCovWarning -n %s" %(output, n)
            addToMakefile_analyze(lines, phoniesToAdd, cmd, combine_target)#, target)
            cmd = 'mv higgsCombine%s.FitDiagnostics.mH120.root %s' %(n, output_path_fit)
            mv1_target = 'mv1_%s_%s' %(c,m)
            addToMakefile_analyze(lines, phoniesToAdd, cmd, mv1_target, combine_target)
            cmd = 'mv fitDiagnostics%s.root %s' %(n, output_path_fit)
            mv2_target = 'mv2_%s_%s' %(c,m)
            addToMakefile_analyze(lines, phoniesToAdd, cmd, mv2_target, combine_target)

if fit:
    createMakefile(makefile, phoniesToAdd, lines, filesToClean=None, isSbatch=False, phoniesToAdd=phoniesToAdd)
    run_cmd( "make -f %s -j %i 2>%s 1>%s" % \
     (makefile, 16, stderr_file_path, stdout_file_path),
     False)
