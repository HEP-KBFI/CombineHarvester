import logging
import os
import ROOT as r
import shutil,subprocess
def createFile(fileName, lines, nofNewLines = 2):
    """Auxiliary function to write new config file,                                                                                                                                                         
       containg the lines given as argument.                                                                                                                                                                
    """
    content = "\n".join(lines)
    content += nofNewLines * "\n"
    with open(fileName, "w") as f:
      f.write(content)

def createMakefile(makefileName, targets, lines_makefile, filesToClean = None, isSbatch = False, phoniesToAdd = []):
    """Creates Makefile that runs the complete analysis workfow.
    """
    lines_makefile_with_header = []
    lines_makefile_with_header.append(".DEFAULT_GOAL := all")
    lines_makefile_with_header.append("SHELL := /bin/bash")
    lines_makefile_with_header.append("")
    lines_makefile_with_header.append("all: %s" % " ".join(targets))
    lines_makefile_with_header.append("")
    phonies = []
    if filesToClean:
        phonies.append('clean')
    if isSbatch:
        phonies.append(' '.join(phoniesToAdd))
    if len(phonies) > 0:
        lines_makefile_with_header.append(".PHONY: %s" % ' '.join(phonies))
    if filesToClean:
        lines_makefile_with_header.append("clean:")
        for fileToClean in filesToClean:
            lines_makefile_with_header.append("\trm -f %s" % fileToClean)
        lines_makefile_with_header.append("")
    lines_makefile_with_header.extend(lines_makefile)
    createFile(makefileName, lines_makefile_with_header)

def run_cmd(command, do_not_log = False, stdout_file = None, stderr_file = None,
            return_stderr = False):
  """Runs given commands and logs stdout and stderr to files 
  """
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  # Remove trailing newline
  stdout = stdout.rstrip('\n')
  stderr = stderr.rstrip('\n')

  if stdout_file:
    stdout_file.write(command + "\n")
    stdout_file.write('%s\n' % stdout)
  if stderr_file:
    stderr_file.write('%s\n' % stderr)

  if not do_not_log:
    logging.debug("Executed command: '%s'" % command)
    logging.debug("stdout: '%s'" % stdout)
    logging.debug("stderr: '%s'" % stderr)

  if return_stderr:
    return stdout, stderr
  return stdout

def addToMakefile_analyze(lines, phoniesToAdd, cmd, target, dependency = ""):
    phoniesToAdd.append(target)
    lines.append("%s:%s " %(target,dependency))
    lines.append("\t%s" %cmd)
    lines.append("\t")
