# -*- coding: utf-8 -*-
import os

from HTSeqAnalysis.utils import csvtolist


def main(samplesfile, path):
    samplenames = csvtolist(samplesfile)
    command = 'htseq-count'

    for samplename in samplenames:
        samplepath = os.path.join(path, samplename)
        print(samplepath)
