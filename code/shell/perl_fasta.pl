
use DateTime; 

my $protein_file = "/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr.dat";
my $ipr_file = "/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr_pfam.dat";

open (my $fh, '<', $protein_file) or die "Can't open file: $!";
open (my $ipr, '<', $ipr_file) or die "Can't open file: $!";

print DateTime->now . "\n";

#
# Given an id from fasta file, find corresponding lines in ipr
#
sub find_pfam
{
    $protein_id = $_[0];
    #print "looking for " . $protein_id;
    while (my $pfam_line = <$ipr>){
        chomp $pfam_line;
        if($pfam_line =~ /$protein_id/ ){
            printf "Found protein " . $protein_id . " domains : " . $pfam_line . "\n";
        }
    }
}

#
# Loop through fasta entries and get id (characters after >UniRef100_ )
# Pass this to subroutine to find pfam entries in ipr file
#


while (my $line = <$fh>){
    chomp $line;
    #if($line =~ /\>UniRef100_([A-Z0-9]*)/){
    #    my $protein_id = $1;
    #    find_pfam($protein_id);
    #}
    print 'Processing protein ' . $line . "\n";
    find_pfam($line);
}

print DateTime->now . "\n";