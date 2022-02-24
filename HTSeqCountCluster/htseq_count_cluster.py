# -*- coding: utf-8 -*-
import os
import argparse
import textwrap

from HTSeqCountCluster.utils import csvtolist
from HTSeqCountCluster.pbsjob import PBSJob
from HTSeqCountCluster.pbsjob.qstat import Qstat
from HTSeqCountCluster.logger import Logger


htseq_log = Logger().default(logname="htseq-count-cluster", logfile=None)


def call_htseq(infile, gtf, outfile):
    """Call the htseq-count script.

    :param infile: An alignment file of aligned reads in SAM format.
    :type infile: str
    :param gtf: The gtf (Gene transfer format) file.
    :type gtf: str
    :param outfile: The name of the output SAM alignment file.
    :type outfile: str
    """
    cmd = 'htseq-count -f bam -s no {} {} -o {}_htseq.out'.format(
        infile, gtf, outfile)
    return cmd


def htseq_jobber(input_path, inputlist, gtf, outpath, email):
    """Create multiple pbs jobs based on input list of files.

    :param input_path: [description]
    :type input_path: [type]
    :param inputlist: [description]
    :type inputlist: [type]
    :param gtf: The gtf (Gene transfer format) file.
    :type gtf: str
    :param outpath: [description]
    :type outpath: [type]
    :param email: An email address to send notifications.
    :type email: str
    """
    jobids = []
    for item in inputlist:
        htseqjob = PBSJob(email_address=email, base_jobname=item)
        itempath = os.path.join(input_path, item)
        itemfilepath = os.path.join(itempath, 'accepted_hits.bam')
        output_path = os.path.join(outpath, item)
        cmd = call_htseq(infile=itemfilepath, gtf=gtf, outfile=output_path)
        jobid = htseqjob.submit_cmd(cmd, cleanup=False)
        jobids.append(jobid)
    return jobids


def check_job_status(job_id, email=True):
    """Use Qstat to monitor your job status.

    :param job_id: The job's id.
    :type job_id: str
    :param email: A flag to decide whether to send email, defaults to True
    :type email: bool, optional
    """
    # TODO Allow either slack notifications or email or text.
    qwatch = Qstat().watch(job_id)
    if qwatch == 'Job id not found.':
        return 'Finished'
    elif qwatch == 'Waiting for %s to start running.' % job_id:
        return 'Queued'
    elif qwatch == 'Waiting for %s to finish running.' % job_id:
        return 'Running'


def main():
    """Run the htseq_jobber function."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="*Ensure that htseq-count is in your path.",
                                     description=textwrap.dedent('''\
                                    This is a command line wrapper around htseq-count.
                                    '''))
    parser.add_argument('-p', '--inpath', help='Path of your samples/sample folders.',
                        required=True)
    parser.add_argument('-f', '--infile', help='Name or path to your input csv file.',
                        required=True)
    parser.add_argument('-g', '--gtf', help='Name or path to your gtf/gff file.',
                        required=True)
    parser.add_argument('-o', '--outpath',
                        help='Directory of your output counts file. The counts file will be named.',
                        required=True)
    parser.add_argument('-e', '--email',
                        help='Email address to send script completion to.')

    args = parser.parse_args()

    samplenames = csvtolist(args.infile)

    htseq_jobber(input_path=args.inpath, inputlist=samplenames, gtf=args.gtf,
                 outpath=args.outpath, email=args.email)


if __name__ == '__main__':
    main()
