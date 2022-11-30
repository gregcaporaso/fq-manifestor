#!/usr/bin/env python

import glob
import sys
import os.path
import re

def fq_manifestor(input_dir,
                  output_fp,
                  fq_extensions=['fastq.gz', 'fq.gz'],
                  split_pattern='_',
                  f_read_pattern='_R1_',
                  r_read_pattern='_R2_',
                  filter_pattern=None,
                  verbose=True):

    input_dir = os.path.abspath(input_dir)
    if verbose: print("Searching directory: %s" % input_dir)

    fq_filepaths = []
    for fq_extension in fq_extensions:
        fq_filepaths += glob.glob('%s/**/*.%s' % (input_dir, fq_extension),
                                 recursive = True)
    if filter_pattern is not None:
        fq_filepaths = [fp for fp in fq_filepaths if filter_pattern in fp]

    if verbose: print('Found %d fastq files.' % len(fq_filepaths))

    sids_to_fps = {}

    for fq_filepath in fq_filepaths:
        fq_filename = os.path.basename(fq_filepath)
        sid_fields = re.split(split_pattern, fq_filename)

        if len(sid_fields) == 1:
            raise ValueError('Sample ID not found in file: %s' % fq_filepath)
        else:
            sid = sid_fields[0]

        if bool(re.search(f_read_pattern, fq_filename)):
            forward = True
            reverse = False
        elif bool(re.search(r_read_pattern, fq_filename)):
            forward = False
            reverse = True
        else:
            raise ValueError('Forward/reverse patterns not found in file: %s' % fq_filepath)

        try:
            sid_fps = sids_to_fps[sid]
        except KeyError:
            sid_fps = [None, None]

        if forward:
            sid_fps[0] = fq_filepath
        else:
            sid_fps[1] = fq_filepath
        sids_to_fps[sid] = sid_fps

    lines = ['sample-id\tforward-absolute-filepath\treverse-absolute-filepath']
    for sid, (fwd_fq_filepath, rev_fq_filepath) in sids_to_fps.items():
        if fwd_fq_filepath is None:
            raise ValueError('Missing forward read for sample: %s' % s)

        if rev_fq_filepath is None:
            raise ValueError('Missing reverse read for sample: %s' % s)

        lines.append('%s\t%s\t%s' % (sid, fwd_fq_filepath, rev_fq_filepath))

    with open(output_fp, 'w') as of:
        of.write('\n'.join(lines))
        of.write('\n')



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('USAGE: fq-manifestor input-directory output-filepath')
        exit(0)

    input_dir = sys.argv[1]
    output_fp = sys.argv[2]

    fq_manifestor(input_dir, output_fp)
    output_fp = os.path.abspath(output_fp)

    print("To import, try running:")
    print("qiime tools import "\
          "--type 'SampleData[PairedEndSequencesWithQuality]' "\
          "--input-path %s --output-path demux.qza "\
          "--input-format PairedEndFastqManifestPhred33V2" % output_fp)

