-----------------------------------------
            Key Files
-----------------------------------------

Pre-Corpus
- uniref100_e_tokens_combined_20240910.dat
- 50,894,561 lines

Corpus Versions

- ** Original **
- July version deleted as there were some tokens mising from the SQL inner join

- ** Main ** (note that I renamed this to add a date)
- uniref100_e_corpus_20240910.dat
- 46,554,318 lines


- ** Created Fri Sept 20 with a minimum gap of 50 
uniref100_e_corpus_gap_50_20240920_1643.txt
- 37,721,172 lines
- created in : 294.23s

Good:
A0A010PZP5:297:1:1:0|PF00106:22:225
PF00106  STOP_GAP

A0A010PZP8:632:5:2:3|PF00172:16:53|PF04082:216:322|DISORDER:50:103|DISORDER:50:109|DISORDER:553:598
PF00172 GAP PF04082 GAP DISORDER

A0A010PZQ1:578:2:0:2|DISORDER:1:28|DISORDER:13:28
IGNORED

A0A010PZQ6:694:10:1:9|PF11696:70:693|DISORDER:1:73|DISORDER:13:36|DISORDER:38:58|DISORDER:249:275|DISORDER:299:348|DISORDER:311:325|DISORDER:326:348|DISORDER:470:495|DISORDER:473:487
START_GAP  PF11696
Good > PFAM takes up a lot of space

A0A010PZR7:646:13:1:12|PF10453:383:409|DISORDER:1:18|DISORDER:1:369|DISORDER:68:98|DISORDER:136:152|DISORDER:153:167|DISORDER:251:266|DISORDER:318:336|DISORDER:392:493|DISORDER:418:473|
DISORDER DISORDER DISORDER  DISORDER GAP DISORDER GAP DISORDER PF10453 DISORDER GAP DISORDER

A0A010PZU0:453:3:3:0|PF03463:19:140|PF03464:146:276|PF03465:281:418
PF03463 PF03464 PF03465

A0A010PZU2:933:6:2:4|PF10373:196:470|PF10374:70:186|DISORDER:553:624|DISORDER:588:605|DISORDER:606:624|DISORDER:722:745
START_GAP  PF10374 PF10373 GAP DISORDER GAP DISORDER  STOP_GAP 






W2V_PFAM_CLAN_MC1
- Populated by calling interpro for each pfam id in any of the mc1 models
- Has mappping to clan for every vocab item in mc1 models and therfore for all models

- 15,481 entries (4 less than vocab as vocab has GAP, DISORDER, START_GAP, STOP_GAP)
- 7,966 pfams have an undefined clan ('undef')

To get number of pfams in each clan
SELECT CLAN_ID, COUNT(*) AS item_count FROM W2V_PFAM_CLAN_MC1 GROUP BY CLAN_ID ORDER BY item_count DESC

202409120709_evo_pfam_clans.txt
- This file contains all the clans from pfam vector from the evolutionary matrix that Daniel created
- It was filled by calling the interpro api - see w2v_clan_utils.py



         vocab      reduced dist
evo     20,651      as below
mc1     15,485      15,040
mc3     13,539      13,179
mc5     12,819      12,484
mc8     12,201      11,888
