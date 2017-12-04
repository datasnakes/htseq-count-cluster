"""Configuration dictionaries for SGEJob class."""
import getpass
from datetime import datetime as d
import sys
import os

from HTSeqAnalysis.pbsjob.pbsutils import randomid

if sys.version_info.major < 3:
    raise NotImplementedError('This is not designed for the python version in your \
                              path')
elif sys.version_info.major >= 3 and sys.version_info.minor < 5:
    raise NotImplementedError('This is not designed for the python version in your \
                              path')

_format1 = '%a %b %d %I:%M:%S %p %Y'

_jobname = 'htseq_{}'.format(randomid(length=4))

__DEFAULT__ = {
            'author': getpass.getuser(),
            'description': 'This is a default pbs job.',
            'date': d.now().strftime(_format1),
            'proj_name': 'htseq-cluster',
            'select': '1',
            'memgb': '2gb',
            'cput': '24:00:00',
            'wt': '12:00:00',
            'job_name': _jobname,
            'outfile': _jobname + '.o',
            'errfile': _jobname + '.e',
            'script': _jobname,
            'log_name': _jobname,
            'pbsworkdir': os.getcwd(),
            'cmd': 'python3 ' + os.path.join(os.getcwd(), _jobname + '.py'),
            'email': 'n/a'
             }
