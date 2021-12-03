from opentrons import protocol_api
from opentrons_functions.transfer import add_buffer, get_96_from_384_wells

metadata = {
    'apiLevel': '2.5',
    'author': 'Jon Sanders'}

 
cols = ['{0}{1}'.format(row, col) for col in range(1, 3)
        for row in ['A', 'B']]

trash_tips = True

def run(protocol: protocol_api.ProtocolContext):

    # define deck positions and labware

    # tips
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)

    tipracks_10f = [protocol.load_labware('opentrons_96_filtertiprack_10ul', x)
                    for x in [4]]

    # plates
    reagents = protocol.load_labware('usascientific_12_reservoir_22ml',
                                     3, 'reagents')
    assay = protocol.load_labware('corning_384_wellplate_112ul_flat',
                                  1, 'assay')

    standards = protocol.load_labware('tubeblockvwrpcrstriptube_'
                                    '96_wellplate_250ul',
                                    2,
                                    'standards')

    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi',
                                            'left',
                                            tip_racks=[tiprack_300])

    pipette_right = protocol.load_instrument('p10_multi',
                                             'right',
                                             tip_racks=tipracks_10f)

    # distribute 38 µL of quantification reagent into each well of the assay
    # plate. 

    pipette_left.distribute(38,
                          reagents['A1'],
                          [assay[x] for x in cols],
                          touch_tip=True,
                          trash=trash_tips,
                          new_tip='once')

    # add 2 µL of each std to each of the wells. Mix after dispensing.
    # Dispose of these tips.
    pipette_right.transfer(2,
                           standards['A1'],
                           [assay[x] for x in cols],
                           mix_after=(5, 10),
                           touch_tip=True,
                           trash=trash_tips,
                           new_tip='always')
