from opentrons import protocol_api
from opentrons.protocols.types import APIVersion

metadata = {
    'apiLevel': '2.2',
    'author': 'Jon Sanders'}


api_version = APIVersion(2, 2)

def get_96_from_384_wells(method='interleaved', start=1):
    
    if method == 'interleaved':
        rows = [chr(64 + x*2 - (start % 2)) for x in range(1,9)]
        cols = [x*2 - int((start+1) / 2)%2 for x in range(1,13)]
        
        for col in cols:
            for row in rows:
                yield('%s%s' % (row, col))
                
    if method == 'packed':
        for col in range((start-1)*6+1, (start-1)*6 + 7):
            for row in [chr(x+65) for x in range(0,16,2)]:
                yield('%s%s' % (row,col))
        for col in range((start-1)*6+1, (start-1)*6 + 7):
            for row in [chr(x+65) for x in range(1,17,2)]:
                yield('%s%s' % (row,col))

def run(protocol: protocol_api.ProtocolContext(api_version=api_version)):
    
    # define deck positions and labware
    
    # tips
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    
    tipracks_10f = [protocol.load_labware('opentrons_96_filtertiprack_10ul', x)
                    for x in [1, 4, 7, 10]]
    
    # plates
    reagents = protocol.load_labware('nest_12_reservoir_15ml', 3, 'reagents')
    assay = protocol.load_labware('corning_384_wellplate_112ul_flat', 9, 'assay')
    
    samples = [protocol.load_labware('biorad_96_wellplate_200ul_pcr', x, 'samples')
               for x in [2, 5, 8, 11]]
    
    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi', 
                                            'left',
                                            tip_racks=[tiprack_300])

    pipette_right = protocol.load_instrument('p10_multi', 
                                            'right',
                                            tip_racks=tipracks_10f)
    
    
    # # home instrument
    protocol.home()
    
    # distribute 38 µL of quantification reagent into each well of the assay plate. 
    # Use the same tip for the entirety of these transfers, then replace it in the rack.
    
    pipette_left.distribute(38,
                            [reagents.wells_by_name()['A1'],
                             reagents.wells_by_name()['A2']],
                            assay.wells(),
                            disposal_volume=10,
                            trash=False,
                            blow_out=False,
                            new_tip='once')
    
    # add 2 µL of each sample to each of the wells. Mix after dispensing. Dispose of these tips.
    
    for i, plate in enumerate(samples):
        start = i + 1
        assay_wells = get_96_from_384_wells(method='interleaved', start=start)
        pipette_right.transfer(2, 
                               plate.wells(), 
                               [assay[x] for x in assay_wells],
                               mix_after=(1, 10),
                               touch_tip=True,
                               trash=True,
                               new_tip='always')
    
    



