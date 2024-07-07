
use DateTime; 

my $taxonomy_file = "/Users/patrick/dev/ucl/comp0158_mscproject/data/taxonomy/names.dmp";

open (my $tf, '<', $taxonomy_file) or die "Can't open file: $!";

#print DateTime->now . "\n";

#
# Loop through fasta entries and get id (characters after >UniRef100_ )
# Pass this to subroutine to find pfam entries in ipr file
#

my $count = 0;
while (my $line = <$tf>){
    chomp $line;
   
        #if($line =~ /([0-9]*)[\s\t\|]+([0-9a-zA-Z\s"\-()]*)[\t\|]*([0-9a-zA-Z\s]*)|/ ){
        #if($line =~ /([0-9]*)[\t\|]+([0-9a-zA-Z\s"\-()]*)[\t\|]*([0-9a-zA-Z\s]*)|/ ){
        #    my $id = $1;
        #    print $1 . ":" . $2 . ":" . $3 . ":" . "\n";
        #    print 'Processing line ' . $line . "\n";
        #}
      
    # Tokenize the content
    my @tokens = split(/[\|\t]+/, $line);

    # Print the tokens
    foreach my $token (@tokens) {
        my $clean = chomp $token;
        print $token . "|";
    }
    print "\n";
}

#print "\n" . DateTime->now . "\n";