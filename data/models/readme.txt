-------------------------------
Model & corpus history
-------------------------------

A number of models were created:

Ignore
1) 0811: Very early models to get things moving - early August
2) 0831: Good corpus and models created across 4 AWS instances : all_models_final_20240831.zip
            - Corpus: uniref100_e_corpus_20240810.txt (also word2vec_sentences.pkl)

                mc = minumum count (4 variations)   : 1, 3, 5, 8
                w  = window size   (6 variations)   : 3, 5, 8, 13, 21, 44
                v  = vector size   (6 variations)   : 5, 10, 25, 50, 75, 100
            - The logs for these are in separate files such as aws0
            - Unfortunately I found a few gaps in the corpus - not too many but still had time to redo

Use
3) 0910: 
            - 20240910 Revised corpus (first one had missing items)
            - Used precorpus uniref100_e_tokens_combined_20240910.dat (which had all data)
            - Full set of cbow and skip models (cbow all on one AWS instance)
4) 0920 : 
            - 20240920 Gap corpus with gaps of <50 not being gaps
            - Used precorpus uniref100_e_tokens_combined_20240910.dat (which had all data
            - NOt a full set of models but a decent mix


1)  Initial models in early August
2)  Loads of models in late August
    - These were created on a mac but also across 4 separate AWS instances on dates 20240831 to 20240901.
    - The logs for these are in separate files such as aws01
    - Corpus: uniref100_e_corpus_20240810.txt

    mc = minumum count (4 variations)   : 1, 3, 5, 8
    w  = window size   (6 variations)   : 3, 5, 8, 13, 21, 44
    v  = vector size   (6 variations)   : 5, 10, 25, 50, 75, 100

    These models are in the zip file 'all_models_final_20240831.zip'

    Model Creation
    Apart from those models with the name _mac in their title, all models were created on AWS hardware - one EC2 instance was created
    to process each minimum count (ie each instance created 36 models). Each instance was of the same size (t3.2xlarge) and was given 
    its own separate EBS store (ie disk) - 150GB (although that was cutting it a bit fine). The terraform scripts to create the EC@ 
    instances can be found in code/terraform/hpc.

    Models were created using this corpus : uniref100_e_corpus_20240810.txt

3) Sept 09 :  I then found a small issue with the corpus - for some reason the innerjoin had missed the last set of Data
    - Regenerated the innerjoin, precorpus and corpus
    - uniref100_e_corpus_20240910.txt
    - Note I originally just called this uniref100_e_corpus.dat

    - I then re-ran a load of models:
        - All cbow models were run on AWS
        - All skip models were run on mac

4) Sept 20 : After consultation with Daniel, decided to modify the corpus such that gaps would not be included if the gap was <50
    - Used precorpus uniref100_e_tokens_combined_20240910.dat
    - Corpus : uniref100_e_corpus_gap_50_20240920_1643.txt
    - Models : In folder 0920

