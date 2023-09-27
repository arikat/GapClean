# GapClean (v0.5) 
###### Written by Aarya Venkat
<img src="gapclean.png" width="350">

#### Description:  
GapClean takes a gappy multiple sequence alignment and removes columns with gaps at a  
specified threshold value to produce a "cleaner" and easier to visualize sequence alignment.  

#### Usage: gapclean [options]

   `-i`   Input file       (Required)

   `-o`   Output file      (Required)

   `-t`   Threshold value  (Optional) Default is 99.

   `-h`   Display this help message


#####  Example: `gapclean -i input.fa -o output.fa -t 95`
  
  
## INSTALLATION:

1. Download gapclean and the bucket folder and copy both to your local bin (EG: `/usr/local/bin/`)

2. `chmod +x gapclean`

3. scrub behind your ears
