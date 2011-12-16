"""
Installs git precommit hooks in the local .git/hooks directory.
"""

if __name__ == "__main__":
  import os
  import sys
  from subprocess import Popen, PIPE

  def run(command):
      p = Popen(command.split(), stdout=PIPE, stderr=PIPE)
      p.wait()
      return p.returncode, p.stdout.read(), p.stderr.read()

  hook = "git@github.com:pennappslabs/hooks.git"
  branch = "pcrapi"
  commands = ( 
      'rm -fr .git/hooks',
      'git clone %s %s .git/hooks' % (hook, "-b %s" % branch if branch else ""),
      'chmod +x .git/hooks/pre-commit',
      )
  for command in commands:
    exit_code, _, errors = run(command)
    if exit_code != 0:
      print >>sys.stderr, "\r Failed installing hook. \n%s" % errors
      break
  else:
    print "Sucessfully installed git precommit hook from %s" % hook
