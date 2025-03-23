#!/usr/bin/env python

import glob
import os.path
import re

_default_fq_extensions = ['fastq.gz', 'fq.gz', 'fastq', 'fq']
_default_split_pattern = '_'
_default_f_read_pattern='_R1_'
_default_r_read_pattern='_R2_'
_default_exclude_patterns=[]

def fq_manifestor(input_dir,
                  output_fp,
                  fq_extensions=_default_fq_extensions,
                  split_pattern=_default_split_pattern,
                  f_read_pattern=_default_f_read_pattern,
                  r_read_pattern=_default_r_read_pattern,
                  exclude_patterns=_default_exclude_patterns,
                  verbose=True):

    input_dir = os.path.abspath(input_dir)
    if verbose: print("Searching directory: %s" % input_dir)

    fq_filepaths = []
    for fq_extension in fq_extensions:
        fq_filepaths += glob.glob('%s/**/*.%s' % (input_dir, fq_extension),
                                 recursive = True)
    n_fq_filepaths = len(fq_filepaths)

    if verbose: print('Found %d fastq files.' % n_fq_filepaths)

    sids_to_fps = {}

    for fq_filepath in fq_filepaths:
        fq_filename = os.path.basename(fq_filepath)

        # Skip if the fq_filepath matches any exclude pattern
        if exclude_patterns and any(pattern in fq_filepath for pattern in exclude_patterns):
            for pattern in exclude_patterns:
                if pattern in fq_filepath:
                    if verbose: print("Excluding filepath matching exclude pattern %s: %s" % (pattern, fq_filepath))
                    n_fq_filepaths -= 1
            continue

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
            raise ValueError('Missing forward read for sample: %s' % sid)

        if rev_fq_filepath is None:
            raise ValueError('Missing reverse read for sample: %s' % sid)

        lines.append('%s\t%s\t%s' % (sid, fwd_fq_filepath, rev_fq_filepath))

    if (len(lines) - 1) != (n_fq_filepaths / 2) and verbose:
        print("\n** WARNING**: "
              "The number of manifest records doesn't align with the number of "
              "fastq files that were found. It's possible that the match "
              "patterns aren't working correctly for your files. These can "
              "be customized when using the API.\n")


    output_path = os.path.abspath(output_fp)
    with open(output_fp, 'w') as of:
        of.write('\n'.join(lines))
        of.write('\n')

    if verbose:
        print("To import, try running:")
        print("qiime tools import "
              "--type 'SampleData[PairedEndSequencesWithQuality]' "
              "--input-path %s --output-path demux.qza "
              "--input-format PairedEndFastqManifestPhred33V2" % output_fp)