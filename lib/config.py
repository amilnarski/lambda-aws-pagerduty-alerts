"""Config lib methods."""
import os
import logging

logger = logging.getLogger('alerter')


class Config(object):
    """Attempt to load ENV vars from a file."""

    def __init__(self):
        """Gather facts."""
        self._file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..',
            'deploy.env')

    def load(self):
        """Attempt to load up environment vars."""
        try:
            if os.path.exists(self._file):
                contents = file(self._file, 'r').read()

            for line in contents.split('\n'):
                split = line.split('=')
                if len(split) > 1:
                    os.environ[split[0].strip()] = split[1].strip()
        except:
            logging.info('Could not correctly read env file!')
