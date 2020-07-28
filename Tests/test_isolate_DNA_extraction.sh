#!/bin/bash

opentrons_simulate \
-L ../Labware/custom_labware \
../Extraction/isolate_DNA_extraction/isolate_DNA_extraction.py \
> test_isolate_DNA_extraction.out
