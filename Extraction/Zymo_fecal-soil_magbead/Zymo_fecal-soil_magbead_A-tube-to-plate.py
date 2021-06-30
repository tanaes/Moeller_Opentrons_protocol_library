from opentrons import protocol_api
from numpy import floor
from itertools import chain

metadata = {
    'apiLevel': '2.8',
    'author': 'Jon Sanders'}

# Define parameters for protocol

# Quantity of supernatant to transfer
quantity = 200

# Height above bottom of source tube to aspirate from
z_height = 16

# Rate of aspiration (1 is default for pipette)
rate = 0.25

# Tuberack labware
tuberack_labware = 'opentrons_24_tuberack_generic_2ml_screwcap'

# Subset columns if desired
cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def run(protocol: protocol_api.ProtocolContext):

    # define deck positions and labware

    # tips
    tiprack_200f = protocol.load_labware('opentrons_96_filtertiprack_200ul', 6)

    # tube racks, named for deck position
    tuberack_4 = protocol.load_labware(tuberack_labware, 4)
    tuberack_1 = protocol.load_labware(tuberack_labware, 1)
    tuberack_5 = protocol.load_labware(tuberack_labware, 5)
    tuberack_2 = protocol.load_labware(tuberack_labware, 2)

    # plates
    samples = protocol.load_labware('vwr_96_wellplate_1000ul',
                                    3, 'samples')

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

        # Indices to locate source racks
        # X and Y are indices of tube rack positions
        # (0 left/top, 1 right/bottom)
        x = int(i % 2)
        y = int(floor(i/2.0))

        # Indices to locate destination wells
        # a and b are from:to columns of the destination plate
        a = (x*6)
        b = ((x+1)*6)
        # i and j are the from:to rows of the destination plate
        i = (y*4)
        j = ((y+1)*4)

        # In this arrangement, the source tube racks are combined into four
        # quadrants of the destination plate, for a 1:1 spatial relationship
        # between the tubes on the deck and the wells in the destination plate.

        d_rows = [c[i:j] for c in samples.columns()]
        d_wells = list(chain(*d_rows[a:b]))
        
        s_wells = rack.wells()
        
        # filter wells to just the ones we want
        
        pairs = tuple(zip([s for s in s_wells],
                          [d for d in d_wells]))
        
        pairs_filtered = [(x, y) for x, y in pairs
                          if int(y.display_name[1:3].strip()) in cols]        

        s_wells_filtered = [x for x, y in pairs_filtered]
        d_wells_filtered = [y for x, y in pairs_filtered]
        
        if not s_wells_filtered:
            continue

        pipette_right.transfer(quantity,
                               [w.bottom(z=z_height) for w in s_wells_filtered],
                               d_wells_filtered,
                               new_tip='always',
                               rate=rate,
                               trash=True)


