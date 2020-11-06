from opentrons import protocol_api


metadata = {'apiLevel': '2.5',
            'author': 'Jon Sanders'}

cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
        'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

vol = 50
extra = 20

def run(protocol: protocol_api.ProtocolContext):


    # tips
    tiprack = protocol.load_labware('opentrons_96_filtertiprack_200ul', 
                                            1)

    # stock plate
    stock = protocol.load_labware('tubeblockvwrhalfskirtpcrplate_96_wellplate_250ul',
                                     2, 'stock')

    # dest plates

    plate_1 = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                   4, 'plate_1')
    plate_2 = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                   5, 'plate_2')
    plate_3 = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                   6, 'plate_3')

    # initialize pipettes
    pipette = protocol.load_instrument('p300_multi', 
                                        'left',
                                        tip_racks=[])


    for col in cols:
        pipette.pick_up_tip(tiprack[col])
        pipette.aspirate(vol*3 + extra, stock[col])
        pipette.dispense(vol, plate_1[col])
        pipette.dispense(vol, plate_2[col])
        pipette.dispense(vol, plate_3[col])
        pipette.dispense(extra, stock[col])
        pipette.drop_tip()