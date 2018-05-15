#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os
import argparse
import textwrap


def merge_counts_tables(filesdirectory):
    """Merge multiple counts tables into 1 counts table.

    After running htseq-count-cluster, there will be a counts table for each
    sample in the output directory. This function will use the genes column as
    the first column and then insert each subsequent sample name as column
    header with counts data as the column rows.
    """
    files = os.listdir(filesdirectory)

    samplenames = []
    sample_dfs = []

    for file in files:
        filename, ext = file.split('.')
        samplename, barcode = filename.split('-')
        samplenames.append(samplename)
        filep = os.path.join(filesdirectory, file)
        data = pd.read_table(filep, header=None, names=['Genes', samplename])
        sdf = 'df_' + samplename
        sdf = pd.DataFrame(data=data)
        sample_dfs.append(sdf[samplename])
        genes = list(sdf['Genes'])

    genes_df = pd.DataFrame(genes, columns=['Genes'])
    samples_df = pd.concat(sample_dfs, axis=1)
    final_df = pd.concat([genes_df, samples_df], axis=1)

    final_df.to_csv('merged_counts_table.csv', index=False)


def main(directory):
    """Run the merge_counts_tables function."""
    merge_counts_tables(filesdirectory=directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                    Merge multiple counts tables into 1 counts .csv file.

                                    Your output file will be named:  merged_counts_table.csv
                                    '''))
    parser.add_argument('-d', '--directory',
                        help='Path to folder of counts files.',
                        required=True)

    args = parser.parse_args()
    main(args.directory)

