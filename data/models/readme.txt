This directory contains all models 144 models (4 x 6 x 6) models based upon the following parameters:

mc = minumum count (4 variations)   : 1, 3, 5, 8
w  = window size   (6 variations)   : 3, 5, 8, 13, 21, 44
v  = vector size   (6 variations)   : 5, 10, 25, 50, 75, 100

These models are in the zip file 'all_models_final.zip'

Model Creation
Apart from those models with the name _mac in their title, all models were created on AWS hardware - one EC2 instance was created
to process each minimum count (ie each instance created 36 models). Each instance was of the same size (t3.2xlarge) and was given 
its own separate EBS store (ie disk) - 150GB (although that was cutting it a bit fine). The terraform scripts to create the EC@ 
instances can be found in code/terraform/hpc.

Models were created using this corpus : uniref100_e_corpus_20240810.txt

Best Models
When compared to the evolutionary distance matrix from Daniel Buchan's work, the 'best' two models based upon a Mantel test can be found in the 
'best' folder. 
- Model sg1_mc8_w44_v25 was the best overall model with a correlation of 0.07 - based upon euclidean distances
- Model sg1_mc8_w13_v5 was only the 46th best but is included because it was best based upon cosine distance

Mantel test output:
286	1	20240904	 mantel 	" w2v_20240903_sg1_mc8_w44_v25_euc_dist"	 32.9s 	50	0.071337064	0.019607843	11878
40	46	20240904	 mantel 	" w2v_20240901_sg1_mc8_w13_v5_cos_dist"	 35.92s 	50	0.049696487	0.019607843	11878