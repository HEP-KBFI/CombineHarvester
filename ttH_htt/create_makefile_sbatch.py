'''
Call with 'python' 
Usage:
    create_makefile_sbatch.py 
    create_makefile_sbatch.py [--channel=STR --era=INT --inputpath=STR --outputpath=STR]

Options:
    -channel --channel=INT          which channel to be considered [default: bb1l]
    -era --era=INT           which era to be considered [default: 2016]
    -inputpath --inputpath=STR  inputpath
    -outputpath --outputpath=STR  outputpath
'''
import docopt
import subprocess
import os
import glob
from textwrap import dedent
from create_makefile_dependency import *

def create_sbatchfile(cmd, output_dir, append):
    job_file = os.path.join('%s/sbatch_%s' %(output_dir, append))
    error_file = os.path.join('%s/sbatch_%s_err.log' %(output_dir, append))
    output_file = os.path.join('%s/sbatch_%s_out.log' %(output_dir, append))
    with open(job_file, 'wt') as filehandle:
        filehandle.writelines(dedent(
            """
                #!/bin/bash
                #SBATCH --job-name=%s
                #SBATCH --ntasks=1
                #SBATCH --time=24:00:00
                #SBATCH --cpus-per-task=8
                #SBATCH -e %s
                #SBATCH -o %s
                env
                date
                %s
            """ % (
                    append, error_file, output_file, cmd
            )
        ).strip('\n'))
    return job_file

def main(channel, era, input_dir, output_dir):
    phoniesToAdd = []
    lines =[]
    pwd = os.getcwd()
    dir = "%s/create_make_files" %(pwd)
    proc=subprocess.Popen(['mkdir %s' % dir],shell=True,stdout=subprocess.PIPE)
    evtcats = ['HH_resolved_1b_nonvbf', 'HH_resolved_2b_vbf', 'HH_resolved_1b_vbf', 'HH_resolved_2b_nonvbf', 'HH_boosted',
            'DY_resolved', 'DY_boosted', 'TT_resolved', 'TT_boosted', 'SingleTop_resolved',
            'SingleTop_boosted','Other', 'W_resolved', 'W_boosted'
           ]
    if channel == '2l_0tau':
        evtcats.remove('W_resolved')
        evtcats.remove('W_boosted')
    makefile = os.path.join(dir, 'Makefile_fit')
    make_stdout = os.path.join(dir, 'Makefile_fit_%s_stdout' %(era))
    make_stderr = os.path.join(dir, 'Makefile_fit_%s_stderr' %(era))
    for evtcat in evtcats:
        stdout = os.path.join(dir, '%s_%s_stdout.txt' %(evtcat, era))
        stderr = os.path.join(dir, '%s_%s_stderr.txt' %(evtcat, era))
        datacard = glob.glob('%s/*%s*SM*final.txt' %(input_dir, evtcat))[0]
        cmd = "text2workspace.py %s -o %s_WS.root" %(datacard, datacard.replace('.txt', ''))
        target = 'text2ws_%s' %evtcat
        phoniesToAdd.append(target)
        lines.append('%s:' %target)
        #lines.append('\t%s\n' %cmd)
        sbatchfile = create_sbatchfile(cmd, output_dir, 'text2ws_%s_%s_%s' %(channel, evtcat, era))
        lines.append('\tsbatch %s\n' %sbatchfile)
        phoniesToAdd.append('combine_%s' %evtcat)
        lines.append('combine_%s:%s' %(evtcat, target))
        cmd = "combineTool.py -M FitDiagnostics %s_WS.root --saveShapes --saveWithUncertainties --saveNormalization  --skipBOnlyFit -n _shapes_combine_%s_%s_%s 1>%s 2>%s" %(datacard.replace('.txt', ''), channel, evtcat, era, stdout, stderr)
        #lines.append('\t%s' %cmd)
        sbatchfile = create_sbatchfile(cmd, output_dir, 'combine_%s_%s_%s' %(channel, evtcat, era))
        lines.append('\tsbatch %s\n' %sbatchfile)
        lines.append("\t")
        '''target = 'plots_%s' %evtcat
        phoniesToAdd.append(target)
        cmd = 'python test/makePlots.py  --input fitDiagnostics_shapes_combine_%s_%s.root' %(evtcat, era)
        cmd += ' --odir %s' %input_dir
        cmd += ' --era %s' %era 
        cmd += ' --nameOut %s_final' %evtcat
        cmd += ' --channel %s' %channel
        cmd += ' --HH --binToRead HH_%s' %channel
        cmd += ' --binToReadOriginal HH_%s' %channel
        cmd += ' --signal_type nonresNLO --mass none  --HHtype bbWW --do_bottom --unblind'
        print cmd
        lines.append('%s:' %target)
        lines.append('\t%s\n' %cmd)'''
    createMakefile(makefile, phoniesToAdd, lines, filesToClean=None, isSbatch=False, phoniesToAdd=phoniesToAdd)
    run_cmd( "make -f %s -j %i 2>%s 1>%s" % \
            (makefile, 14, make_stderr, make_stdout),
             False)

if __name__ == '__main__':
    try:
        arguments = docopt.docopt(__doc__)
        print arguments
        channel = arguments['--channel']
        era = arguments['--era']
        input_dir = arguments['--inputpath']
        output_dir = arguments['--outputpath']
        main(channel, era, input_dir, output_dir)
    except docopt.DocoptExit as e:
        print(e)
