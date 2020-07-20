from opentrons import protocol_api
from opentrons.protocols.types import APIVersion
from numpy import ceil

metadata = {
    'apiLevel': '2.5',
    'author': 'Jon Sanders'}


api_version = APIVersion(2, 5)

cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
        'A7', 'A8', 'A9', 'A10', 'A11', 'A12']


def add_buffer(pipette,
               plate,
               cols,
               wash_vol,
               source_wells,
               source_vol,
               tip=None,
               tip_vol=300,
               remaining=None,
               drop_tip=True,
               dead_vol=0.05):

    
    if tip is not None:
        pipette.pick_up_tip(tip)
    else:
        pipette.pick_up_tip()


    source_well = source_wells[0]
    if remaining is None:
        remaining = source_vol

    transfers = int(ceil(wash_vol/(tip_vol-10)))
    transfer_vol = wash_vol/transfers

    for col in cols:
        for i in range(0,transfers):
#             print("%s µL remaining in %s" % (remaining, source_well))
#             print("Transferring %s to %s" % (transfer_vol, col))
            pipette.aspirate(transfer_vol, 
                             source_well)
            pipette.air_gap(10)
            pipette.dispense(transfer_vol + 10, 
                             plate[col].top())

            remaining -= transfer_vol

            if remaining < transfer_vol + source_vol * dead_vol:

#                 print("Only %s remaining in %s\n" % (remaining, source_well))
                source_wells.pop(0)
                try:
                    source_well = source_wells[0]
                except IndexError:
                    print('Ran out of source wells!')
                
#                 print("Moving on to %s\n" % source_well)
                remaining = source_vol

        pipette.blow_out()

    if drop_tip:
        pipette.drop_tip()
    else:
        pipette.return_tip() 

    return(remaining, source_wells)


def run(protocol: protocol_api.ProtocolContext):
    
    # define deck positions and labware
    
    # tips
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    tiprack_10f = protocol.load_labware('opentrons_96_filtertiprack_10ul', 2)
    
    # plates
    reagents = protocol.load_labware('usascientific_12_reservoir_22ml', 6, 'reagents')
    assay = protocol.load_labware('corning_96_wellplate_360ul_flat', 5, 'assay')
    samples = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 4, 'samples')
    
    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi', 
                                            'left',
                                            tip_racks=[tiprack_300])

    pipette_right = protocol.load_instrument('p10_multi', 
                                            'right',
                                            tip_racks=[tiprack_10f])
    
    
    # # home instrument
    # protocol.home()
    
    # distribute 198 µL of quantification reagent into each well of the assay plate. 
    # Use the same tip for the entirety of these transfers, then replace it in the rack.
    
    add_buffer(pipette_left,
               assay,
               cols,
               198,
               [reagents[x] for x in ['A1','A2']],
               22000/8,
               tip=None,
               tip_vol=300,
               remaining=None,
               drop_tip=False)

    
    # add 2 µL of each sample to each of the wells. Mix after dispensing. Dispose of these tips.
    
    pipette_right.transfer(2, 
                           [samples[x] for x in cols], 
                           [assay[x] for x in cols],
                           mix_after=(5, 10),
                           touch_tip=True,
                           trash=False,
                           new_tip='always')
    
    


