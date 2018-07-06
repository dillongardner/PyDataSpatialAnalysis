# Introduction to Geospatial Analysis in Python

This repository is in support of a talk on geospatial data.

## Data

To recreate all of the examples, the data are available here:

The exception is the Demographics and Health Survey ([DHS](https://www.dhsprogram.com/)) as this requires registering to download and use. Downloading the data into the `data` folder is necessary to recreate the examples. The `extract_dhs` script will format the DHS data into the form used in the examples. If the DHS data are not available, it will create synthetic random data that are structually similar, but the will not reveal the same relationships between cluster median asset and nighttime light intensity.

## Examples

There are two examples in notebooks. The first, `Nigeria Nightlights` is what is discussed in the talk. The second `US Nightlights` performs similar analysis on U.S. data. 