# plugin.py
import sys
import logging
from string import Template
from subprocess import Popen, STDOUT, PIPE
from tempfile import TemporaryFile
from util import cmd_from_config, size_to_bytes, cmd_to_size
from holland.core.exceptions import BackupError
from holland.core.util.path import directory_size

LOG = logging.getLogger(__name__)

class ScriptPlugin(object):
    def __init__(self, name, config, target_directory, dry_run=False):
        config.validate_config(self.configspec())
        self.name = name
        self.config = config
        self.path = target_directory
        self.dry_run = dry_run

    def estimate_backup_size(self):
        method = self.config['script']['estimation-method']
        if method.startswith('const:'):
            try:
                return size_to_bytes(method.lstrip('const:'))
            except ValueError, exc:
                raise BackupError("Estimation failed: %s" % exc)
        elif method.startswith('dir:'):
            return directory_size(method[4:])
        elif method.startswith('cmd:'):
            try:
                return cmd_to_size(method[4:])
            except ValueError, exc:
                raise BackupError("Estimation failed: %s" % exc)
        else:
            raise BackupError("Unknown estimation method: %s" % method)
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
        estimation-method = string(default="const:4M")
        """).strip().splitlines())
    configspec = classmethod(configspec)

CONFIGSPEC = ScriptPlugin.configspec()
