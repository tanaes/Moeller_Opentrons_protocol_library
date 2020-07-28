#!/bin/bash

opentrons_simulate \
-L ../Labware/custom_labware \
../Quantification/Quantifluor_DNA_quant/Quantifluor_DNA_one-plate.py \
> test_Quantifluor_DNA_one-plate.out
