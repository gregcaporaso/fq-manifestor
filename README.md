# fq-manifestor

`fq-manifestor.py` is script to assist with generating [QIIME 2 paired-end fastq manifest files](https://docs.qiime2.org/2022.2/tutorials/importing/#fastq-manifest-formats). This is not widely test or very general purpose, but is designed as a starting point to assist users of the [NAU Genetics Core Facility](https://in.nau.edu/gcf/) load their data in QIIME 2.

## Requirements

### Software

`fq-manifestor.py` requires Python 3. There are no dependencies beyond the Python 3 standard library (i.e., you don't have to have QIIME 2 installed on the computer where this script is run).

### Input data format

Assume you have a directory of files, `/sequence-data/humanure-run1`, containing demultiplexed paired end Illumina sequence data. This script will assume the directory is structured as follows:

```
$ tree /sequence-data/humanure-run1
/sequence-data/humanure-run1
├── 07717ac5_L001-ds.0795510ce4044fbab87b5c0b08aec105
│   ├── 07717ac5_S71_L001_R1_001.fastq.gz
│   └── 07717ac5_S71_L001_R2_001.fastq.gz
├── 08a10d08_L001-ds.060074faec87417b88e83d07470e7b10
│   ├── 08a10d08_S30_L001_R1_001.fastq.gz
│   └── 08a10d08_S30_L001_R2_001.fastq.gz
├── 091cbf06_L001-ds.9e1f729478e645bfa87b695aec93300d
│   ├── 091cbf06_S35_L001_R1_001.fastq.gz
│   └── 091cbf06_S35_L001_R2_001.fastq.gz
├── 10583739_1_L001-ds.0e7c88a021984a38b930ce5c60ddadfd
│   ├── 10583739-1_S72_L001_R1_001.fastq.gz
│   └── 10583739-1_S72_L001_R2_001.fastq.gz
```

In this case there are four samples, `07717ac5`, `08a10d08`, `091cbf06`, and `10583739-1`. The samples are grouped into per-sample directories, and there is a forward (R1) and reverse (R2) read file for each sample.

## Running this script from the command line

Call the following command:

```
./fq-manifestor.py /sequence-data/humanure-run1 humanure-run1-fq-manifest.txt
```

This will either error with a hopefully-informative error message (but no guarantees!) or succeed with output that looks something like:

```
Searching directory: /sequence-data/humanure-run1
Found 160 fastq files.
To import, try running:
qiime tools import --type 'SampleData[PairedEndSequencesWithQuality]' --input-path humanure-run1-fq-manifest.txt --output-path demux.qza --input-format PairedEndFastqManifestPhred33V2
```

Try running that command in a QIIME 2 conda environment, and it should import successfully.

## Running this script from the Python API

Some customization is possible if you call the underlying Python function directly. Take a look at the `.py` in the GitHub repo if you want to try.

## What if it doesn't work?

Let me know on the issue tracker, and I may be able to help. But this is very experimental so no promises!
