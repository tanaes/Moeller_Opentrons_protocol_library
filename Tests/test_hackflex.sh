#!/bin/bash

opentrons_simulate \
-L ../Labware/custom_labware \
../Library_Prep/Hackflex/hackflex.py \
> test_hackflex.out
