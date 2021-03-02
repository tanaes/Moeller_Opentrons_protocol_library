from opentrons import protocol_api
from opentrons_functions.transfer import add_buffer


metadata = {
    'apiLevel': '2.5',
    'author': 'Jon Sanders'}

cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
        'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

trash_tips = True

def run(protocol: protocol_api.ProtocolContext):

    # define deck positions and labware

    # tips
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    tiprack_10f = protocol.load_labware('opentrons_96_filtertiprack_10ul', 2)

    # plates
    reagents = protocol.load_labware('usascientific_12_reservoir_22ml',
                                     6, 'reagents')
    assay = protocol.load_labware('corning_96_wellplate_360ul_flat',
                                  5, 'assay')
    samples = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                    4, 'samples')

    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi',
                                            'left',
                                            tip_racks=[tiprack_300])

    pipette_right = protocol.load_instrument('p10_multi',
                                             'right',
                                             tip_racks=[tiprack_10f])

    # # home instrument
    # protocol.home()

    # distribute 198 µL of quantification reagent into each well of the assay
    # plate. Use the same tip for the entirety of these transfers, then
    # replace it in the rack.

    add_buffer(pipette_left,
               [reagents[x] for x in ['A1']],
               assay,
               cols,
               95,
               12000/8,
               tip=None,
               tip_vol=300,
               remaining=None,
               drop_tip=trash_tips)

    # add 2 µL of each sample to each of the wells. Mix after dispensing.
    # Dispose of these tips.
    pipette_right.transfer(5,
                           [samples[x] for x in cols],
                           [assay[x] for x in cols],
                           mix_after=(5, 10),
                           touch_tip=True,
                           trash=trash_tips,
                           new_tip='always')
