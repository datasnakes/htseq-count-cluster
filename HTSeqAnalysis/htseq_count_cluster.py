# -*- coding: utf-8 -*-
import os
import argparse
import textwrap

from HTSeqAnalysis.utils import csvtolist
from HTSeqAnalysis.pbsjob import PBSJob
from HTSeqAnalysis.pbsjob.qstat import Qstat
from HTSeqAnalysis.logger import Logger


htseq_log = Logger().default(logname="htseq count cluster", logfile=None)


def call_htseq(infile, gtf, outfile):
    cmd = 'htseq-count -f bam -s no {} {} -o {}_htseq.out'.format(infile, gtf, outfile)
    return cmd


def htseq_jobber(input_path, inputlist, gtf, outpath, email):
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
    """Use Qstat to monitor your job status."""
    # TODO Allow either slack notifications or email or text.
    qwatch = Qstat().watch(job_id)
    if qwatch == 'Job id not found.':
        return 'Finished'
    elif qwatch == 'Waiting for %s to start running.' % job_id:
        return 'Queued'
    elif qwatch == 'Waiting for %s to finish running.' % job_id:
        return 'Running'


def main(folderpath, samplescsv, gtf, outpath, email):
    samplenames = csvtolist(samplescsv)
    htseq_jobber(input_path=folderpath, inputlist=samplenames, gtf=gtf,
                 outpath=outpath, email=email)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="*Ensure that htseq-count is in your path.",
                                     description=textwrap.dedent('''\
                                    This is a command line wrapper around htseq-count.
                                    '''))
    parser.add_argument('-p', '--inpath', help='Path of your samples/sample folders.')
    parser.add_argument('-f', '--infile',
                        help='Name or path to your input csv file.')
    parser.add_argument('-g', '--gtf',
                        help='Name or path to your gtf/gff file.')
    parser.add_argument('-o', '--outpath',
                        help='Directory of your output counts file. The counts file will be named.')
    parser.add_argument('-e', '--email',
                        help='Email address to send script completion to.')

    args = parser.parse_args()
    main(args.inpath, args.infile, args.gtf, args.outpath, args.email)
