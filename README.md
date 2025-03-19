# fq-manifestor

`fq-manifestor` is script to assist with generating [QIIME 2 paired-end fastq manifest files](https://docs.qiime2.org/2022.2/tutorials/importing/#fastq-manifest-formats). This is not widely tested and likely not very general purpose, but is designed as a starting point to assist Illumina users with importing paired-end demultiplexed fastq files for use with QIIME 2. This script does not actually import your data into QIIME 2, but rather generates a fastq manifest file and suggests an import command to use with QIIME 2. That increases portability of the script as it can be run on systems without QIIME 2 installed on them.

This script was originally developed to facilitate work with the [NAU Genetics Core Facility](https://in.nau.edu/gcf/).

## Why is this script needed?

Importing can be hard. I talk a little about why [here](https://gregcaporaso.github.io/q2book/using/importing.html#importing-data-into-qiime-2).

## Requirements

### Software

`fq-manifestor` requires Python 3. There are no dependencies beyond the Python 3 standard library (i.e., you don't have to have QIIME 2 installed on the computer where this script is run).

### Input data format

If you have a directory of files, `/sequence-data/humanure-run1`, containing demultiplexed paired end Illumina sequence data this script will assume the directory is structured as follows:

```
$ tree /sequence-data/humanure-run1
/sequence-data/humanure-run1
├── 07717ac5_L001-ds.0795510ce4044fbab87b5c0b08aec105
│   ├── 07717ac5_S71_L001_R1_001.fastq.gz
│   └── 07717ac5_S71_L001_R2_001.fastq.gz
├── 08a10d08_L001-ds.060074faec87417b88e83d07470e7b10
│   ├── 08a10d08_S30_L001_R1_001.fastq.gz
│   └── 08a10d08_S30_L001_R2_001.fastq.gz
├── 091cbf06_L001-ds.9e1f729478e645bfa87b695aec93300d
│   ├── 091cbf06_S35_L001_R1_001.fastq.gz
│   └── 091cbf06_S35_L001_R2_001.fastq.gz
├── 10583739_1_L001-ds.0e7c88a021984a38b930ce5c60ddadfd
│   ├── 10583739-1_S72_L001_R1_001.fastq.gz
│   └── 10583739-1_S72_L001_R2_001.fastq.gz
```

In this case there are four samples, `07717ac5`, `08a10d08`, `091cbf06`, and `10583739-1`. The samples are grouped into per-sample directories, and there is a forward (R1) and reverse (R2) read file for each sample. This script will assume that the text before the first `_` in the fastq filenames (not the directory names) is the sample id.

For example, the sample id that will be associated with the following files:

```
├── 10583739_1_L001-ds.0e7c88a021984a38b930ce5c60ddadfd
│   ├── 10583739-1_S72_L001_R1_001.fastq.gz
│   └── 10583739-1_S72_L001_R2_001.fastq.gz
```

is `10583739-1`. This is the text before the first `_` in the file name. Notice that the `-` in the sample id is replaced with an `_` in the directory name - this script is building sample ids from the file names, not the directory names.

## Running this script from the command line

### Basic Usage

Call the following command:

```
python3 fq-manifestor input-directory output-filepath
```

For example:

```
python3 fq-manifestor /sequence-data/humanure-run1 humanure-run1-fq-manifest.txt
```

This will either error with a hopefully-informative error message (but no guarantees!) or succeed with output that looks something like:

```
Searching directory: /sequence-data/humanure-run1
Found 160 fastq files.
To import, try running:
qiime tools import --type 'SampleData[PairedEndSequencesWithQuality]' --input-path humanure-run1-fq-manifest.txt --output-path demux.qza --input-format PairedEndFastqManifestPhred33V2
```

Try running that command in a QIIME 2 conda environment, and it should import successfully.

### Advanced Usage

The command line interface now offers additional options to customize the behavior:

```
python3 fq-manifestor input-directory output-filepath [options]
```

Available options:

* `--fq-extensions LIST` - List of fastq file extensions to look for (default: fastq.gz fq.gz)
* `--split-pattern PATTERN` - Pattern to split filename to extract sample ID (default: _)
* `--f-read-pattern PATTERN` - Pattern to identify forward reads (default: _R1_)
* `--r-read-pattern PATTERN` - Pattern to identify reverse reads (default: _R2_)
* `--filter-pattern PATTERN` - Only include files containing this pattern
* `--exclude-patterns LIST` - List of patterns to exclude from sample IDs (default: Undetermined)
* `--quiet` - Suppress verbose output

For example, if your files use a different naming pattern:

```
python3 fq-manifestor /data/sequences output.txt --split-pattern "-" --f-read-pattern "_1." --r-read-pattern "_2."
```

For a full list of options:

```
python3 fq-manifestor --help
```

## Running this script from the Python API

Some customization is possible if you call the underlying Python function directly:

```python
import fq_manifestor

fq_manifestor.fq_manifestor(
    input_dir='/path/to/fastq/files',
    output_fp='manifest.txt',
    fq_extensions=['fastq.gz', 'fq.gz'],
    split_pattern='_',
    f_read_pattern='_R1_',
    r_read_pattern='_R2_',
    filter_pattern=None,
    exclude_patterns=['Undetermined'],
    verbose=True
)
```

## What if it doesn't work?

Let me know on the [issue tracker](https://github.com/gregcaporaso/fq-manifestor/issues), and I may be able to help. But this is very experimental so no promises!