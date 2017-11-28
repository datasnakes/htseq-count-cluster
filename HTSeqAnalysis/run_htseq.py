# -*- coding: utf-8 -*-
import os

from HTSeqAnalysis.utils import csvtolist


def main(samplesfile, outpath):
    samplenames = csvtolist(samplesfile)
    command = 'htseq-count'

    for samplename in samplenames:
        samplepath = os.path.join(outpath, samplename)
        print(samplepath)


if __name__ == '__main__':
    main(samplesfile='impulsivity_samplenames.csv', outpath=os.getcwd())