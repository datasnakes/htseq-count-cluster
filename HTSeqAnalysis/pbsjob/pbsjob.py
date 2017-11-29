from subprocess import run, CalledProcessError, PIPE
import os
from pkg_resources import resource_filename

from HTSeqAnalysis.logger import Logger
from HTSeqAnalysis.pbsjob.pbsutils import basejobids, writecodefile, import_temp, file2str
from HTSeqAnalysis.pbsjob.pbsconfig import __DEFAULT__
from HTSeqAnalysis import pbsjob
from HTSeqAnalysis.pbsjob.qstat import Qstat


class BasePBSJob(object):
    """Base class for simple jobs."""
    def __init__(self, base_jobname):
        """Initialize job attributes."""
        self.default_job_attributes = __DEFAULT__
        self.file2str = file2str
        self.sgejob_log = Logger().default(logname="SGE JOB", logfile=None)
        self.pbsworkdir = os.getcwd()

        # Import the temp.pbs file using pkg_resources
        self.temp_pbs = resource_filename(pbsjob.__name__, "temp.pbs")

    @classmethod
    def _configure(cls, length, base_jobname):
        """Configure job attributes or set it up."""
        baseid, base = basejobids(length, base_jobname)
        return baseid, base

    def debug(self, code):
        """Debug the SGEJob."""
        raise NotImplementedError

    def _cleanup(self, jobname):
        """Clean up job scripts."""
        self.sgejob_log.warning('Your job will now be cleaned up.')
        os.remove(jobname + '.pbs')
        self.sgejob_log.warning('%s.pbs has been deleted.' % jobname)
        os.remove(jobname + '.py')
        self.sgejob_log.warning('%s.py has been deleted.' % jobname)


class PBSJob(BasePBSJob):
    """Create a qsub/pbs job & script for the job to execute."""
    def __init__(self, email_address, base_jobname=None):
        super().__init__(base_jobname=base_jobname)
        self.email = email_address
        self.attributes = self.default_job_attributes
        self.jobname = self.default_job_attributes['job_name']
        if base_jobname is not None:
            _, self.jobname = self._configure(base_jobname=base_jobname,
                                              length=5)
            self.attributes = self._update_default_attributes()

    def _update_default_attributes(self):
        pyfile_path = os.path.join(self.pbsworkdir, self.jobname + '.py')
        # These attributes are automatically updated if a jobname is given.
        new_attributes = {'email': self.email,
                          'job_name': self.jobname,
                          'outfile': self.jobname + '.o',
                          'errfile': self.jobname + '.e',
                          'script': self.jobname,
                          'log_name': self.jobname + '.log',
                          'cmd': 'python3 ' + pyfile_path,
                          }
        self.default_job_attributes.update(new_attributes)

        return self.default_job_attributes

    def submit_code(self, code, cleanup=True, default=True):
        """Create and submit a qsub job.

        Submit python code."""
        # TIP If python is in your environment as only 'python' update that.
        # If default, a python file will be created from code that is used.
        # Allow user input to be a python file
        if os.path.isfile(code) and str(code).endswith('.py'):
            code_str = self.file2str(code)
            self.sgejob_log.info('%s converted to string.' % code)
        elif type(code) == str:
            code_str = code

        if default:
            self.sgejob_log.info('You are running a job with default attributes.')
            writecodefile(filename=self.jobname, code=code_str, language='python')
            pyfilename = self.jobname + '.py'
            self.sgejob_log.info('%s python file has been created.' % pyfilename)

            # Create the pbs script from the template or dict
            pbstemp = import_temp(self.temp_pbs)
            pbsfilename = self.jobname + '.pbs'

            with open(pbsfilename, 'w') as pbsfile:
                pbsfile.write(pbstemp.substitute(self.attributes))
                pbsfile.close()
            self.sgejob_log.info('%s has been created.' % pbsfilename)
        else:
            msg = 'Custom SGEJob creation is not yet implemented.'
            raise NotImplementedError(msg)
            # TODO Add custom job creation

        # Submit the job using qsub
        try:
            cmd = ['qsub ' + self.jobname + '.pbs']  # this is the command
            # Shell MUST be True
            cmd_status = run(cmd, stdout=PIPE, stderr=PIPE, shell=True, check=True)
        except CalledProcessError as err:
            self.sgejob_log.error(err.stderr.decode('utf-8'))
            if cleanup:
                self._cleanup(self.jobname)
        else:
            if cmd_status.returncode == 0:  # Command was successful.
                # The cmd_status has stdout that must be decoded.
                # When a qsub job is submitted, the stdout is the job id.
                submitted_jobid = cmd_status.stdout.decode('utf-8')
                self.sgejob_log.info(self.jobname + ' was submitted.')
                self.sgejob_log.info('Your job id is: %s' % submitted_jobid)
                return submitted_jobid
                if cleanup:
                    self._cleanup(self.jobname)

            else:  # Unsuccessful. Stdout will be '1'
                self.sgejob_log.error('PBS job not submitted.')

    def submit_cmd(self, cmd, cleanup=True):
        """Create and submit a qsub job.

        Submit python code."""

        cmddict = {'cmd': cmd}
        self.attributes.update(cmddict)

        # Create the pbs script from the template or dict
        pbstemp = import_temp(self.temp_pbs)
        pbsfilename = self.jobname + '.pbs'

        with open(pbsfilename, 'w') as pbsfile:
            pbsfile.write(pbstemp.substitute(self.attributes))
            pbsfile.close()
        self.sgejob_log.info('%s has been created.' % pbsfilename)

        # Submit the job using qsub
        try:
            cmd = ['qsub ' + self.jobname + '.pbs']  # this is the command
            # Shell MUST be True
            cmd_status = run(cmd, stdout=PIPE, stderr=PIPE, shell=True, check=True)
        except CalledProcessError as err:
            self.sgejob_log.error(err.stderr.decode('utf-8'))
            if cleanup:
                self._cleanup(self.jobname)
        else:
            if cmd_status.returncode == 0:  # Command was successful.
                # The cmd_status has stdout that must be decoded.
                # When a qsub job is submitted, the stdout is the job id.
                submitted_jobid = cmd_status.stdout.decode('utf-8')
                self.sgejob_log.info(self.jobname + ' was submitted.')
                self.sgejob_log.info('Your job id is: %s' % submitted_jobid)
                return submitted_jobid
                if cleanup:
                    self._cleanup(self.jobname)

            else:  # Unsuccessful. Stdout will be '1'
                self.sgejob_log.error('PBS job not submitted.')

