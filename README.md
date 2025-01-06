# GapClean (v1.0.1) 
###### Written by Aarya Venkat, PhD
<img src="gapclean.png" width="350">

#### Description:  
GapClean takes a gappy multiple sequence alignment and removes columns with gaps at a  
specified threshold value to produce a "cleaner" and easier to visualize sequence alignment.

Can also be used to remove gaps in an alignment relative to a seed sequence to assess site-wise mutational
information.  

#### Usage: gapclean [options]

   `-i`   Input file       (Required)

   `-o`   Output file      (Required)

   `-t`   Threshold value  (Optional) Cannot be used with seed argument

   `-s`   Seed index       (Optional) Cannot be used with threshold argument

   `-h`   Display this help message


#####  Example: `gapclean -i input.fa -o output.fa -t 75` Removes column from alignment when >75 percent of the column are gaps 

#####  Example: `gapclean -i input.fa -o output.fa -s 0` Takes first sequence as the seed and removes gaps relative to seed.

  
  
## INSTALLATION:

1. pip install gapclean

2. Thank Gappy for his service. He is a retired detective.
