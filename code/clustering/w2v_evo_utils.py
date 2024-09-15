import re
import numpy as np
#
# vectors in evo matrix have format K1SVA3.1/50-86|PF02829
# need to extract these
#
def extract_evo_pfam_ids(evo_vector):
    pfam_ids = []
    for item in evo_vector:
        #print(f"searching in {item}")
        pfam_search  = re.search("\|(PF.*)", item)
        if pfam_search is not None:
            pfam_id       = pfam_search.group(1)
            pfam_ids.append(pfam_id)
        else:
            print(f"No pfam found for {item}")

    return pfam_ids

#
# extract vocab vector and matrix from npy file
#                
def extract_evo_matrix_vector_files(npy_file_name):
    npy_f               = open(npy_file_name, 'rb')
    dist_matrix_norm    = np.load(npy_f) #loads second matrix
    vocab_vector        = np.load(npy_f)
    
    return vocab_vector, dist_matrix_norm

#
# returns list of pfams from the evo vectorand a matrix
#
def get_evo_pfams_from_npy(npy_file_name):
    print(f"\n- Extracting from {npy_file_name}")
    evo_vector, evo_matrix = extract_evo_matrix_vector_files(npy_file_name)
    
    evo_pfam_ids = extract_evo_pfam_ids(evo_vector)
    print(f"- Extracted {len(evo_pfam_ids)} pfams from {npy_file_name}\n")
    return evo_pfam_ids, evo_matrix
