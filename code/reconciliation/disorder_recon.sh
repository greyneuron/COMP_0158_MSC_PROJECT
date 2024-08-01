#!/bin/bash

extras_file='/Volumes/My Passport/data/disorder/raw/extra.xml'

# works
#head -100 '/Volumes/My Passport/data/disorder/raw/extra.xml'

# doesn't work
#head -100 $extras_file

# works
#head -100 "$extras_file"

# 01/08/24 : When run against the full extra.xml file, this returns : 230,397,847 entries
grep -c "<protein" "$extras_file"

# each chunk file should have the entries that overall sum to the same amount
