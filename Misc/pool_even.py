from opentrons import protocol_api
from opentrons_functions.magbeads import (
    remove_supernatant, bead_wash, transfer_elute)
from opentrons_functions.transfer import add_buffer
from os.path import join, exists
from datetime import datetime
from pathlib import Path

metadata = {'apiLevel': '2.5',
            'author': 'Jon Sanders'}

# Limit columns
cols = ['1', '2', '3', '4', '5', '6',
        '7', '8', '9', '10', '11', '12']

# Pool volume
vol = 2

# Change tips between aspirations?
tip_change = False

tuberack_labware = 'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap'

def run(protocol: protocol_api.ProtocolContext):

    # ### HackFlex Illumina-compatible library prep protocol

    # ### Deck

    # 1. tube rack
    # 2. 20f tips (samples)
    # 4. library plate
    # 12. trash

    # ### Setup

    # define deck positions and labware
    
    # Libraries
    library = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                   1, 'library')

    # Destination tube
    tuberack = protocol.load_labware(tuberack_labware, 4)

    # tips
    tiprack_samples = protocol.load_labware('opentrons_96_filtertiprack_20ul',
                                            2)
    # initialize pipettes
    pipette_right = protocol.load_instrument('p20_single_gen2',
                                             'right',
                                             tip_racks=[tiprack_samples])

    if tip_change:
        for col in cols:
            pipette_right.transfer(vol, 
                                   library.columns_by_name()[col],
                                   tuberack.wells_by_name()['A1'],
                                   new_tip='always',
                                   touch_tip=True,
                                   trash=True)
    else:
        pipette_right.consolidate(vol, 
                                  [library.columns_by_name()[y] for y in cols],
                                  tuberack.wells_by_name()['A1'],
                                  touch_tip=True,
                                  trash=True)



