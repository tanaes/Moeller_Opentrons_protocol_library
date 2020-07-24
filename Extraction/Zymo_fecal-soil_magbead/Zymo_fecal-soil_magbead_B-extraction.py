from opentrons import protocol_api
from numpy import ceil
from time import clock

metadata = {'apiLevel': '2.5',
            'author': 'Jon Sanders'}

# Set to `True` to perform a short run, with brief pauses and only 
# one column of samples
test_run = True

if test_run:
    pause_bind = 5
    pause_mag = 3
    pause_dry = 5
    pause_elute = 5

    # Limit columns
    cols = ['A1', 'A2']
else:
    pause_bind = 5*60
    pause_mag = 3*60
    pause_dry = 5*60
    pause_elute = 5*60

    # Limit columns
    cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
            'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

# define magnet engagement height for plates
mag_engage_height = 6


# MagBinding + beads cols
mbb_cols = ['A1', 'A2', 'A3']

# MagBinding cols
mbw_cols = ['A4', 'A5', 'A6']


# Wash 1 columns
w1_cols = ['A1', 'A2', 'A3']

# Wash 2 columns
w2_cols = ['A4', 'A5', 'A6', 'A7', 'A8', 'A9',
           'A10', 'A11', 'A12']

# bead aspiration flow rate
bead_flow = .25

# wash mix mutliplier
wash_mix = 5


def bead_mix(pipette,
             plate,
             cols,
             tiprack,
             n=5,
             mix_vol=200,
             drop_tip=False):
    for col in cols:
        pipette.pick_up_tip(tiprack.wells_by_name()[col])
        pipette.mix(n, 
                    mix_vol,
                    plate[col].bottom(z=2))
        pipette.blow_out(plate[col].top())

        if drop_tip:
            pipette.drop_tip()
        else:
            pipette.return_tip()
    return()


def remove_supernatant(pipette,
                       plate,
                       cols,
                       tiprack,
                       waste,
                       super_vol=600,
                       rate=0.25,
                       bottom_offset=2,
                       drop_tip=False):

    # remove supernatant
    
    for col in cols:
        vol_remaining = super_vol
        # transfers to remove supernatant:
        pipette.pick_up_tip(tiprack.wells_by_name()[col])
        transfers = int(ceil(super_vol/190))
        while vol_remaining > 0:
            transfer_vol = min(vol_remaining, 190)
            if vol_remaining <= 190:
                z_height = bottom_offset
            else:
                z_height = 4
            pipette.aspirate(transfer_vol,
                             plate[col].bottom(z=z_height),
                             rate=rate)
            pipette.air_gap(10)
            pipette.dispense(transfer_vol + 10, waste.top())
            vol_remaining -= transfer_vol
            pipette.blow_out()
        # we're done with these tips at this point
        if drop_tip:
            pipette.drop_tip()
        else:
            pipette.return_tip() 
    return()


def add_buffer(pipette,
               plate,
               cols,
               wash_vol,
               source_wells,
               source_vol,
               tip=None,
               tip_vol=300,
               remaining=None,
               drop_tip=True):

    
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

            if remaining < transfer_vol + source_vol*0.1:
#                 print("Only %s remaining in %s\n" % (remaining, source_well))
                source_wells.pop(0)
                source_well = source_wells[0]
                
#                 print("Moving on to %s\n" % source_well)
                remaining = source_vol

        pipette.blow_out()

    if drop_tip:
        pipette.drop_tip()
    else:
        pipette.return_tip() 

    return(remaining, source_wells)


def bead_wash(# global arguments
              protocol,
              magblock,
              pipette,
              plate,
              cols,
              # super arguments
              super_waste,
              super_tiprack,
              # wash buffer arguments
              source_wells,
              source_vol,
              # mix arguments
              mix_tiprack,
              # optional arguments
              super_vol=600,
              rate=bead_flow,
              super_bottom_offset=2,
              drop_super_tip=True,
              wash_vol=300,
              remaining=None,
              wash_tip=None,
              drop_wash_tip=True,
              mix_vol=200,
              mix_n=wash_mix,
              drop_mix_tip=False,
              mag_engage_height=mag_engage_height,
              pause_s=pause_mag
              ):
    # Wash

    # This should:
    # - pick up tip from position 7
    # - pick up 190 µL from the mag plate
    # - air gap
    # - dispense into position 11
    # - repeat x 
    # - trash tip
    # - move to next column
    # - disengage magnet

    # remove supernatant
    remove_supernatant(pipette,
                       plate,
                       cols,
                       super_tiprack,
                       super_waste,
                       super_vol=super_vol,
                       rate=bead_flow,
                       bottom_offset=super_bottom_offset,
                       drop_tip=drop_super_tip)
        
    # disengage magnet
    magblock.disengage()


    # This should:
    # - Pick up tips from column 3 of location 2
    # - pick up isopropanol from position 5 column 3
    # - dispense to `cols` in mag plate
    # - pick up isopropanol from position 5 column 4
    # - dispense to `cols` in mag plate
    # - drop tips at end


    # add isopropanol

    wash_wells, wash_remaining = add_buffer(pipette,
                                            plate,
                                            cols,
                                            wash_vol=wash_vol,
                                            source_wells=source_wells,
                                            source_vol=source_vol,
                                            tip=wash_tip,
                                            remaining=remaining,
                                            drop_tip=drop_wash_tip)


    # This should:
    # - grab a tip from position 8
    # - mix 5 times the corresponding well on mag plate
    # - blow out
    # - return tip
    # - do next col
    # - engage magnet

    # mix
    bead_mix(pipette,
             plate,
             cols,
             mix_tiprack,
             n=mix_n,
             mix_vol=mix_vol,
             drop_tip=drop_mix_tip)

    # engage magnet
    magblock.engage(height_from_base=mag_engage_height)

    protocol.delay(seconds=pause_s)

    return(wash_wells, wash_remaining)


def run(protocol: protocol_api.ProtocolContext):

    # # Magnetic DNA extraction protocol

    # #### This follows the Bio-On-Magnetic_Beads protocol 7.1 for genomic DNA extraction. 
    # 
    # Samples should have been bead-beaten in 2 mL screw-top tubes and then transferred
    # to deep-well plates in the Zymoe_Magbead_A-tubes_to_96well.py protocol. 
    # 
    # Reagents needed:
    # magbinding buffer: 1100 µL per sample / 
    # - reservoir plate with 15 mL lysis buffer in columns 1-4
    # - reservoir plate with 15 mL Isopropanol in columns 5-8
    # - reservoir plate with 15 mL 80% EtOH in columns 9-12
    # - deep well plate with ≥300 µL beads in each well of column 1
    # - deep well plate with 1 mL elution buffer in each well of column 2

    # ### Deck

    # 1. deep well plate (empty)
    # 2. 300 µL tips - buffer transfer
    # 3. PCR plate (final samples)
    # 4. Lysate
    # 5. reservoir plate (wash buffers)
    # 6. 200 µL filter tips - final transfer
    # 7. 200 µL filter tips - lysate transfer
    # 8. 300 µL tips - bead washes
    # 9. empty
    # 10. deep well plate (reagents)
    # 11. mag module
    # 12. trash

    # ### Setup


    # define deck positions and labware

    # define hardware modules
    magblock = protocol.load_module('Magnetic Module', 10)
    magblock.disengage()

    # tips
    tiprack_buffers = protocol.load_labware('opentrons_96_tiprack_300ul', 
                                            5)
    tiprack_elution = protocol.load_labware('opentrons_96_filtertiprack_200ul', 
                                            6)
    # tiprack_lysate = protocol.load_labware('opentrons_96_filtertiprack_200ul', 7)
    tiprack_wash = protocol.load_labware('opentrons_96_tiprack_300ul', 
                                         4)

    # plates
    wash_buffers = protocol.load_labware('usascientific_12_reservoir_22ml', 
                                         11, 'wash buffers')
    reagents = protocol.load_labware('usascientific_12_reservoir_22ml',
                                     9, 'reagents')
    eluate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                   3, 'eluate')
    waste = protocol.load_labware('nest_1_reservoir_195ml',
                                  7, 'liquid waste')

    # load plate on magdeck
    # mag_plate = magblock.load_labware('vwr_96_wellplate_1000ul')
    mag_plate = magblock.load_labware('vwr_96_wellplate_1000ul')

    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi', 
                                            'left',
                                            tip_racks=[tiprack_buffers])

    # MagBindingBuffer + beads wells
    mbb_wells = [reagents[x] for x in mbb_cols]

    # MagBindingBuffer wells
    mbw_wells = [reagents[x] for x in mbw_cols]

    # Wash 1 columns
    w1_wells = [wash_buffers[x] for x in w1_cols]

    # Wash 2 columns
    w2_wells = [wash_buffers[x] for x in w2_cols]


    # ### Prompt user to place plate on mag block


    protocol.pause('Add plate containing 200 µL per well of lysis supernatant'
                   ' onto the magdeck in position 10.')

    # ### Add 600 µL MagBinding buffer
    # ### Add beads to plate
    protocol.comment('Adding beads to plate.')


    pipette_left.pick_up_tip()

    # mix beads
    for col in mbb_cols:
        
    pipette_left.mix(10, 
                     200, 
                     reagents.wells_by_name()['A1'].bottom(z=2))
    pipette_left.mix(10, 
                     200, 
                     reagents.wells_by_name()['A1'].bottom(z=2))

    mbb_remaining, mbb_wells = add_buffer(pipette_left,
                                          mag_plate,
                                          cols,
                                          625,
                                          mbb_wells,
                                          21000/8)

    pipette_left.drop_tip()
    
    # mix again
    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.mix(10, 250, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top(z=-2))
        pipette_left.touch_tip()
        pipette_left.return_tip()

    # bind
    protocol.comment('Binding DNA to beads.')
    protocol.delay(seconds=pause_bind)

    # mix again
    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.mix(10, 250, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top(z=-2))
        pipette_left.touch_tip()
        pipette_left.return_tip()

    # bind for specified length of time

    protocol.comment('Binding beads to magnet.')
    magblock.engage(height_from_base=mag_engage_height)

    protocol.delay(seconds=pause_mag)


    # ### Do first wash: Wash 500 µL MagBinding buffer
    protocol.comment('Doing wash #1.')
    mbb_remaining, mbb_wells = bead_wash(# global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         waste['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments,
                                         mbb_wells,
                                         21000/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments
                                         wash_vol=500,
                                         super_vol=800,
                                         drop_super_tip=False,
                                         mix_n=wash_mix,
                                         remaining=mbb_remaining)


    # ### Do second wash: Wash 500 µL MagWash 1
    protocol.comment('Doing wash #2.')
    w1_remaining, w1_wells = bead_wash(# global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         waste['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments
                                         w1_wells,
                                         21000/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments,
                                         wash_vol=500,
                                         super_vol=500,
                                         drop_super_tip=False,
                                         mix_n=wash_mix,
                                         remaining=None)

    # ### Do third wash: Wash 900 µL MagWash 2
    protocol.comment('Doing wash #3.')
    w2_remaining, w2_wells = bead_wash(# global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         waste['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments
                                         w2_wells,
                                         21000/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments,
                                         wash_vol=900,
                                         super_vol=500,
                                         drop_super_tip=False,
                                         mix_n=wash_mix,
                                         remaining=None)


    # ### Do third wash: Wash 900 µL MagWash 2
    protocol.comment('Doing wash #3.')
    w2_remaining, w2_wells = bead_wash(# global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         waste['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments
                                         w2_wells,
                                         21000/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments,
                                         wash_vol=900,
                                         super_vol=900,
                                         drop_super_tip=False,
                                         mix_n=wash_mix,
                                         remaining=w2_remaining)


    # ### Dry
    protocol.comment('Removing wash and drying beads.')

    # This should:
    # - pick up tip in position 8
    # - pick up supernatant from magplate
    # - dispense in waste, position 11
    # - repeat
    # - trash tip
    # - leave magnet engaged


    # remove supernatant

    remove_supernatant(pipette_left,
                       mag_plate,
                       cols,
                       tiprack_wash,
                       waste['A1'],
                       super_vol=1000,
                       rate=bead_flow,
                       bottom_offset=.5,
                       drop_tip=True)

    # dry

    protocol.delay(seconds=pause_dry)


    # ### Elute
    protocol.comment('Eluting DNA from beads.')

    # This should:
    # - disengage magnet
    # - pick up tip from position 6
    # - pick up reagents from column 2 of position 9
    # - dispense into magplate
    # - mix 10 times
    # - blow out, touch tip
    # - return tip to position 6
    # - wait (5 seconds)
    # - engage magnet
    # - wait (5 seconds)
    # - pick up tip from position 6
    # - aspirate from magplate
    # - dispense to position 3
    # - trash tip


    # transfer elution buffer to mag plate

    magblock.disengage()

    # add elution buffer and mix
    for col in cols:
        pipette_left.pick_up_tip(tiprack_elution.wells_by_name()[col])
        pipette_left.aspirate(50, reagents['A2'], rate=1)
        pipette_left.dispense(50, mag_plate[col].bottom(z=1))
        pipette_left.mix(10, 40, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.touch_tip()
        # we'll use these same tips for final transfer
        pipette_left.return_tip()
    
    protocol.delay(seconds=pause_elute)
    # # start timer
    # t0 = clock()
    # # mix again
    # t_mix = 0
    # while t_mix < pause_elute():
    for col in cols:
        pipette_left.pick_up_tip(tiprack_elution.wells_by_name()[col])
        pipette_left.mix(10, 40, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.touch_tip()
        # we'll use these same tips for final transfer
        pipette_left.return_tip()
        # t_mix = clock() - t0

    # bind to magnet
    protocol.comment('Binding beads to magnet.')

    magblock.engage(height_from_base=mag_engage_height)

    protocol.delay(seconds=pause_mag)

    protocol.comment('Transferring eluted DNA to final plate.')
    for col in cols:
        pipette_left.pick_up_tip(tiprack_elution.wells_by_name()[col])
        pipette_left.aspirate(50, 
                              mag_plate[col].bottom(z=2),
                              rate=bead_flow)
        pipette_left.dispense(50, eluate[col])
        pipette_left.blow_out(eluate[col].top())
        pipette_left.touch_tip()
        # we're done with these tips now
        pipette_left.drop_tip()

    magblock.disengage()


















