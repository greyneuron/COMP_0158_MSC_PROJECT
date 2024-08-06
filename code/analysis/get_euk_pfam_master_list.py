import re


#
# Creating a list of pfam ids without the 'PF' - this will alow me to store them in a 
# numpy array. Also going to save to a database
#
def create_pfam_analysis_list():
    
    pfam_file   = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/unique_eukaryotic_pfam.txt"
    output_file = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/unique_eukaryotic_pfam_ids.txt"
    
    output = open(output_file, "w")
    with open(pfam_file, "r") as pfam_data:
        for line_number, line in enumerate(pfam_data):
            
            line = line.rstrip()
            line = line.lstrip()
            
            my_search  = re.search("PF([0-9]*)", line)
            pf_root      = my_search.group(1)
            
            buffer = "|".join([str(line_number + 1), pf_root, line])
            print(buffer)
            output.write(buffer +'\n')
    output.close()        

create_pfam_analysis_list()