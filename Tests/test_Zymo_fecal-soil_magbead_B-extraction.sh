#!/bin/bash

opentrons_simulate \
-L ../Labware/custom_labware \
../Extraction/Zymo_fecal-soil_magbead/Zymo_fecal-soil_magbead_B-extraction.py \
> test_Zymo_fecal-soil_magbead_B-extraction.out
