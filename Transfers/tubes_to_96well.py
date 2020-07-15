from opentrons import protocol_api
from numpy import floor

metadata = {
    'apiLevel': '2.5',
    'author': 'Jon Sanders'}


quantity = 200
z_height = 20

def run(protocol: protocol_api.ProtocolContext):
    
    # define deck positions and labware
    
    # tips
    tiprack_200f = protocol.load_labware('opentrons_96_filtertiprack_200ul', 6)
    
    # tubes
    tuberack_4 = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', 4)
    tuberack_1 = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', 1)
    tuberack_5 = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', 5)
    tuberack_2 = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', 2)

    # plates
    samples = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 3, 'samples')
    
    # initialize pipettes
    pipette_right = protocol.load_instrument('p300_single_gen2', 
                                            'right',
                                            tip_racks=[tiprack_200f])

    # # home instrument
    protocol.home()
    
    # distribute quantity 
    for i, rack in enumerate([tuberack_4,
                              tuberack_5,
                              tuberack_1,
                              tuberack_2]):

        x = int(i % 2)
        y = int(floor(i/2.0))

        # print('x: %s  y: %s' % (x,y))
        
        a = (x*6)
        b = ((x+1)*6)
        i = (y*4)
        j = ((y+1)*4)
        
        # print('a: %s  b: %s' % (a, b))
        # print('i: %s  j: %s' % (i, j))
        
        d_rows = [c[i:j] for c in samples.columns()]
        # print(d_rows)
        d_wells = d_rows[a:b]
        # print(d_wells)
        
        pipette_right.transfer(quantity,
                               [w.bottom(z=z_height) for w in rack.wells()],
                               d_wells,
                               new_tip='always',
                               trash=True)
        
    


