"""Utility methods"""
import logging
from string import Template

LOG = logging.getLogger(__name__)

def cmd_from_config(config, **kwargs):
    """Extract and format the script command
    from the dictionary config
    """
    tmpl = Template(config['cmd'])
    if not tmpl:
        raise BackupError("No command specified")
    return tmpl.safe_substitute(**kwargs)

def stream2log(stream):
    """Flush lines from an output file
    into the LOG
    """
    stream.flush()
    stream.seek(0)
    for line in stream:
        LOG.info("- %s", line.rstrip())
