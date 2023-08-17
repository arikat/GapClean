#!/usr/bin/perl 

open (SEQFILE, $ARGV[0]);

my $first = <SEQFILE>;

print "$first";

while (<SEQFILE>){
	$_=~s/[\n\r]+//g;
#        chomp $_;
        if ($_ =~ /^>/){
                print "\n$_\n";
        }else{
                print "$_";
        }
}
print "\n";
