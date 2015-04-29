# klusta-pipeline
data pipeline for analyzing spike2 collected data in klustakwik 

## Klustakwik helper scripts

There are two scripts which will get your data from [probe-the-broab](https://github.com/gentnerlab/probe-the-broab) into the KWD format that KlustaKwik requires. These are assuming you are running the analysis on lintu, where klustakwik is installed for the lab to use. You can download the latest [`KlustaViewa` release here](https://github.com/klusta-team/klustaviewa/releases) to install on a local machine.

### Determine which Epoch files to compile for spike sorting

1. From a single Site directory, run `make_s2mat_list`. This will generate a text file (`files_to_compile.txt`) in the site directory listing all of the .mat files exported from Spike2 by `probe-the-broab`.
2. Edit `files_to_compile.txt` and delete any lines for epoch files which you do not wish to sort (e.g. from searching)
3. (Optional) Rename `files_to_compile.txt` if you want to test multiple compilations.

### Compile probe-the-broab mat files into a single KWD file

1. From the site directory, run `s2mat_to_kwd {files_to_compile.txt ProbeName}` e.g. `s2mat_to_kwd files_to_compile.txt A1x16-5mm50`
2. (optional) Edit the generated `.prm` file to tweak any parameters
3. Copy the necessary probe file into the Site directory (TODO: do this in the script)
4. `source activate klusta` to enter into the klustakwik conda environment
4. `klusta params.prm` will run spike detection and clustering
5. `klustaviewa` will launch the GUI to combine and rate clusters. [The DeWeese Lab has a nice HowTo for this final part of spike sorting](http://deweeselab.berkeley.edu/Home/research-interests/spike-sorting). 

