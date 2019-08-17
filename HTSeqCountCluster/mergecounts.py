# -*- coding: utf-8 -*-
import os
import argparse
import textwrap

import pandas as pd

from HTSeqCountCluster.logger import Logger

# Create a merge-counts logger
mc_log = Logger().default(logname="merge-counts", logfile=None)


def merge_counts_tables(files_dir):
    """Merge multiple counts tables into 1 counts table.

    After running htseq-count-cluster, there will be a counts table for each
    sample in the output directory. This function will use the genes column as
    the first column and then insert each subsequent sample name as column
    header with counts data as the column rows.

    :param files_dir: The directory of the individual counts files.
    :type files_dir: str
    """
    mc_log.info("Running merge-counts script.")
    if files_dir is ".":
        files_dir = os.getcwd()

    mc_log.info("Your directory location is: %s" % files_dir)
    files = os.listdir(files_dir)

    samplenames = []
    sample_dfs = []

    for file in files:
        filename, ext = file.split('.')
        if ext == 'out':
            samplename, barcode = filename.split('-')
            samplenames.append(samplename)
            filep = os.path.join(files_dir, file)
            data = pd.read_table(filep, header=None,
                                 names=['Genes', samplename])
            mc_log.info("A dataframe has been created for %s." % samplename)
            sdf = 'df_' + samplename
            sdf = pd.DataFrame(data=data)
            sample_dfs.append(sdf[samplename])
            genes = list(sdf['Genes'])
    samplenames.sort()
    mc_log.info("Samples names have been sorted.")
    genes_df = pd.DataFrame(genes, columns=['Genes'])
    samples_df = pd.concat(sample_dfs, axis=1)
    sorted_samples_df = samples_df[samplenames]
    final_df = pd.concat([genes_df, sorted_samples_df], axis=1)
    mc_log.info("Your dataframes have been merged.")

    csv_file = 'merged_counts_table.csv'
    final_df.to_csv(csv_file, index=False)
    mc_log.info("Your counts have been merged and saved in %s." % csv_file)


def main():
    """Run the merge_counts_tables function."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                Merge multiple counts tables into 1 counts .csv file.

                                Your output file will be named:  merged_counts_table.csv
                                '''))
    parser.add_argument('-d', '--directory',
                        help='Path to folder of counts files.',
                        required=True,
                        type=str)
    args = parser.parse_args()

    merge_counts_tables(files_dir=args.directory)


if __name__ == '__main__':
    main()
