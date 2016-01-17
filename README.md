# klusta-pipeline
Data pipeline for analyzing spike2 collected data in phy

## phy helper scripts

There is one script which will get your data from [probe-the-broab](https://github.com/gentnerlab/probe-the-broab) into the KWD format that phy requires. 

### Make KWD file from spike2 matfiles

1. Run `make_kwd {rig} {probe} {path_to_matfiles} {path_to_save_kwd}` 
2. See make_kwd.py for a list of other arguments you may supply.
3. `make_kwd` will spit out all the data and config files necessary for phy in the directory you specified.
4. You may now run `phy spikesort params.prm` to begin automatic clustering.
5. Run `phy cluster-manual {output.kwik}` to begin manual sorting. 

### Merging Stimuli Information

1. After manual sorting, run `merge_stim_kwik {path_to_matfiles} {path_to_kwikfile}` to merge events into the kwikfile
2. All of the auxiliary files (such as the .json, .kwd, etc.) are necessary for `merge_stim_kwik` to run successfully
3. Your kwikfile now contains all the event times from your experiment.
