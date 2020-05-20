from opentrons import protocol_api
from opentrons.protocols.types import APIVersion

metadata = {
    'apiLevel': '2.2',
    'author': 'Jon Sanders'}


api_version = APIVersion(2, 2)


def run(protocol: protocol_api.ProtocolContext(api_version=api_version)):
    
    # define deck positions and labware
    
    # tips
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    tiprack_10f = protocol.load_labware('opentrons_96_filtertiprack_10ul', 2)
    
    # plates
    reagents = protocol.load_labware('nest_12_reservoir_15ml', 6, 'reagents')
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
    
    # distribute 38 µL of quantification reagent into each well of the assay plate. 
    # Use the same tip for the entirety of these transfers, then replace it in the rack.
    
    pipette_left.distribute(38,
                            reagents.wells_by_name()['A1'],
                            assay.rows_by_name()['A'],
                            disposal_volume=10,
                            trash=False,
                            blow_out=False,
                            new_tip='once')
    
    # add 2 µL of each sample to each of the wells. Mix after dispensing. Dispose of these tips.
    
    pipette_right.transfer(2, 
                           samples.wells(), 
                           assay.wells(),
                           mix_after=(5, 10),
                           touch_tip=True,
                           trash=False,
                           new_tip='always')
    
    


