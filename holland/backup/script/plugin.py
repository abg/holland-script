# plugin.py
import sys
import logging
from string import Template
from subprocess import Popen, STDOUT, PIPE
from tempfile import TemporaryFile
from util import cmd_from_config, stream2log
from holland.core.exceptions import BackupError

LOG = logging.getLogger(__name__)

class ScriptPlugin(object):
    def __init__(self, name, config, target_directory, dry_run=False):
        config.validate_config(self.configspec())
        self.name = name
        self.config = config
        self.path = target_directory
        self.dry_run = dry_run

    def estimate_backup_size(self):
        return 1

    def backup(self):
        if self.dry_run:
            return self._dry_run()

        config = self.config['script']
        cmd = Template(config['cmd']).safe_substitute(backupdir=self.path)

        LOG.info("+ %s", cmd)
        LOG.info("::")
        try:
            pid = Popen([
                        config['shell'],
                        '-c',
                        cmd
                    ],
                    stdin=open('/dev/null', 'r'),
                    stdout=PIPE,
                    stderr=STDOUT,
                    close_fds=True
                )
            for line in pid.stdout:
                LOG.info("+ %s", line.rstrip())
            pid.wait()
            if pid.returncode != 0:
                raise Exception("Command with exited non-zero status")
        except:
            raise BackupError("%s failed: %s" % (cmd, sys.exc_info()[1]))

    def _dry_run(self):
        config = self.config['script']
        cmd = Template(config['cmd']).safe_substitute(backupdir=self.path)
        LOG.info("+ %s", cmd)

    def info(self):
        return ""

    #@classmethod
    def configspec(cls):
        from textwrap import dedent
        return (dedent("""
        [script]
        shell = string(default="/bin/sh")
        cmd = string
        """).strip().splitlines())
    configspec = classmethod(configspec)

CONFIGSPEC = ScriptPlugin.configspec()
