from opentrons import protocol_api
from opentrons_functions.magbeads import (
    remove_supernatant, bead_wash, transfer_elute)
from opentrons_functions.transfer import add_buffer

metadata = {'apiLevel': '2.5',
            'author': 'Jon Sanders'}

test_run = True

if test_run:
    pause_bind = 5*60
    pause_mag = 5*60
    pause_dry = 7*60
    pause_elute = 5*60

    # Limit columns
    cols = ['A1', 'A2']
else:
    pause_bind = 5*60
    pause_mag = 5*60
    pause_dry = 7*60
    pause_elute = 5*60

    # Limit columns
    cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
            'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

# Define minimum tip height for beadbeating tubes
min_height = 14

# define magnet engagement height for plates
mag_engage_height = 6

# Isopropanol columns
ipa_cols = ['A5', 'A6', 'A7', 'A8']

# Isopropanol binding volume
ipa_vol = 400

# Isopropanol fill volume
ipa_fill = 20000

# Ethanol columns
eth_cols = ['A9', 'A10', 'A11', 'A12']

# Ethanol fill volume
eth_fill = 18000

# Lysis buffer columns
lys_cols = ['A1', 'A2', 'A3', 'A4']

# bead aspiration flow rate
bead_flow = .25

# wash mix mutliplier
wash_mix = 10


def run(protocol: protocol_api.ProtocolContext):

    # # Magnetic DNA extraction protocol

    # #### This follows the Bio-On-Magnetic_Beads protocol 7.1 for
    # genomic DNA extraction.
    #
    # Isolates should have been bead-beat in our strip tubes and spun down in
    # the plate centrifuge.
    #
    # Reagents needed:
    # - reservoir plate with 15 mL lysis buffer in columns 1-4
    # - reservoir plate with 15 mL Isopropanol in columns 5-8
    # - reservoir plate with 15 mL 80% EtOH in columns 9-12
    # - deep well plate with ≥300 µL beads in each well of column 1
    # - deep well plate with 1 mL elution buffer in each well of column 2

    # ### Deck

    # 1. Lysate
    # 2. empty
    # 3. PCR plate (final samples)
    # 4. 200 µL filter tips - bead washes
    # 5. 200 µL filter tips - elution
    # 6. 200 µL filter tips - final transfer
    # 7. 195 µL reservoir (liquid waste)
    # 8. 300 µL tips - buffers
    # 9. 22 mL USA Scientific reservoir (reagents)
    # 10. mag module w/ 1 mL VWR deep well plate
    # 11. 22 mL USA  Scientific reservoir (wash buffers)
    # 12. trash

    # ### Setup

    # define deck positions and labware

    # define hardware modules
    magblock = protocol.load_module('Magnetic Module', 10)
    magblock.disengage()

    # tips
    tiprack_buffers = protocol.load_labware('opentrons_96_tiprack_300ul',
                                            8)
    tiprack_elution_1 = protocol.load_labware(
                            'opentrons_96_filtertiprack_200ul', 5)
    tiprack_elution_2 = protocol.load_labware(
                            'opentrons_96_filtertiprack_200ul', 6)
    tiprack_wash = protocol.load_labware('opentrons_96_filtertiprack_200ul',
                                         4)

    # plates
    wash_buffers = protocol.load_labware('usascientific_12_reservoir_22ml',
                                         11, 'wash buffers')
    eluate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                   3, 'eluate')
    waste = protocol.load_labware('nest_1_reservoir_195ml',
                                  7, 'liquid waste')
    reagents = protocol.load_labware('usascientific_12_reservoir_22ml',
                                     9, 'reagents')
    lysate = protocol.load_labware('axygen_96_wellplate_1100ul',
                                   1, 'lysate')

    # load plate on magdeck
    mag_plate = magblock.load_labware('vwr_96_wellplate_1000ul')

    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi',
                                            'left',
                                            tip_racks=[tiprack_buffers])

    # Lysis buffer wells
    lys_wells = [wash_buffers[x] for x in lys_cols]

    # Isopropanol wells
    ipa_wells = [wash_buffers[x] for x in ipa_cols]

    # Ethanol columns
    eth_wells = [wash_buffers[x] for x in eth_cols]

    # ### Prompt user to place cells with beads loaded on position 4
    protocol.pause('Add lysis beads to strip tubes containing dry cell pellet'
                   ' and place on position 1 for addition of lysis buffer.')

    # ### Add lysis buffer
    add_buffer(pipette_left,
               lys_wells,
               lysate,
               cols,
               580,
               18000/8)

    # ### Prompt user to remove plate
    protocol.pause('Remove plate from position 1. \n\n'
                   'Cap tubes in tube plate and beadbeat for required time. '
                   'Then spin down, uncap, and return to position 1. \n\n'
                   'Press continue to start filling plate on mag deck during '
                   'this time. There will be another pause after plate is '
                   'filled to allow you to return strip tube plate to '
                   'position 1 before continuing.')

    # ### Add beads to new plate
    protocol.comment('Adding beads to wash plate.')

    # This should:
    # - pick up a tip from location 2
    # - pick up reagents from column 1 of location 9
    # - distribute 20 µL to each column from `cols` in location 1.
    # - trash tip

    pipette_left.pick_up_tip()

    # mix beads
    pipette_left.mix(10,
                     150,
                     reagents.wells_by_name()['A1'].bottom(z=2))

    pipette_left.distribute(20,
                            reagents.wells_by_name()['A1'],
                            [mag_plate[x] for x in cols],
                            mix_before=(2, 20),
                            touch_tip=False,
                            disposal_volume=10,
                            trash=True,
                            new_tip='never')

    pipette_left.drop_tip()

    # ### Add 1/2 of isopropanol
    protocol.comment('Adding isopropanol to wash plate.')

    # This should:
    # - Pick up tips from column 2 of location 2
    # - pick up isopropanol from position 5 column 1
    # - dispense to `cols` in position 1
    # - pick up isopropanol from position 5 column 2
    # - dispense to `cols` in position 1
    # - return tip at end

    ipa_remaining, ipa_wells = add_buffer(pipette_left,
                                          ipa_wells,
                                          mag_plate,
                                          cols,
                                          ipa_vol/2,
                                          ipa_fill/8,
                                          tip_vol=300,
                                          drop_tip=True)

    protocol.pause('Decap and return spun-down strip tube plate to position '
                   '1. \n\nPress continue when ready.')

    # ### Transfer 1/2 of lysate to new plate

    # # This should:
    # - pick up tips in position 7
    # - pick up 180 µL lysate from plate in position 4
    # - air gap
    # - dispense into corresponding well in position 1
    # - blow out and touch tip
    # - return tip to position 7

    # this needs to be modified to position transfer aspirate
    # location accurately.

    protocol.comment('Transferring lysate to wash plate.')

    for col in cols:
        # do first transfer.
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.aspirate(180,
                              lysate[col].bottom(z=min_height+5),
                              rate=0.25)
        pipette_left.air_gap(10)
        pipette_left.dispense(190, mag_plate[col].top(z=-5))
        pipette_left.mix(5, 200, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top(z=-2))
        pipette_left.touch_tip(v_offset=-1)
        pipette_left.return_tip()

    # bind
    protocol.comment('Binding DNA to beads.')
    protocol.delay(seconds=pause_bind)

    # mix
    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.mix(5, 200, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top(z=-2))
        pipette_left.touch_tip()
        pipette_left.return_tip()

    # bind for specified length of time
    protocol.comment('Binding beads to magnet.')
    magblock.engage(height_from_base=mag_engage_height)

    protocol.delay(seconds=pause_mag)

    # remove supernatant

    remove_supernatant(pipette_left,
                       mag_plate,
                       cols,
                       tiprack_wash,
                       waste['A1'],
                       super_vol=380,
                       tip_vol=200,
                       rate=bead_flow,
                       bottom_offset=2,
                       drop_tip=False)

    # ### Add second half of lysate

    # ### Add 1/2 of isopropanol
    protocol.comment('Adding isopropanol to wash plate.')

    ipa_remaining, ipa_wells = add_buffer(pipette_left,
                                          ipa_wells,
                                          mag_plate,
                                          cols,
                                          ipa_vol/2,
                                          ipa_fill/8,
                                          remaining=ipa_remaining,
                                          tip_vol=300)

    # ### Transfer 1/2 of lysate to new plate

    protocol.comment('Transferring lysate to wash plate.')

    for col in cols:

        # do second transfer.
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.aspirate(180,
                              lysate[col].bottom(z=min_height),
                              rate=0.1)
        pipette_left.air_gap(10)
        pipette_left.dispense(190, mag_plate[col].top(z=-5))
        pipette_left.blow_out()
        pipette_left.touch_tip(v_offset=-1)
        pipette_left.mix(5, 200, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top(z=-2))
        pipette_left.touch_tip(v_offset=-1)
        pipette_left.return_tip()

    # bind
    protocol.comment('Binding DNA to beads.')
    protocol.delay(seconds=pause_bind)

    # mix
    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.mix(5, 200, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top(z=-2))
        pipette_left.touch_tip()
        pipette_left.return_tip()

    # bind for specified length of time
    protocol.comment('Binding beads to magnet.')
    magblock.engage(height_from_base=mag_engage_height)

    protocol.delay(seconds=pause_mag)

    # ### Do first wash
    protocol.comment('Doing wash #1.')
    ipa_remaining, ipa_wells = bead_wash(
                                         # global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         waste['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments
                                         ipa_wells,
                                         ipa_fill/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments
                                         super_vol=380,
                                         drop_super_tip=False,
                                         mix_n=wash_mix,
                                         mix_vol=200,
                                         wash_tip_vol=300,
                                         super_tip_vol=200,
                                         remaining=ipa_remaining,
                                         mag_engage_height=mag_engage_height,
                                         pause_s=pause_mag)

    # ### Do second wash
    protocol.comment('Doing wash #2.')
    eth_remaining, eth_wells = bead_wash(
                                         # global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         waste['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments
                                         eth_wells,
                                         eth_fill/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments,
                                         super_vol=300,
                                         drop_super_tip=False,
                                         mix_n=wash_mix,
                                         mix_vol=200,
                                         wash_tip_vol=300,
                                         super_tip_vol=200,
                                         remaining=None,
                                         mag_engage_height=mag_engage_height,
                                         pause_s=pause_mag)

    # ### Do third wash
    protocol.comment('Doing wash #3.')
    eth_remaining, eth_wells = bead_wash(
                                         # global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         waste['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments
                                         eth_wells,
                                         eth_fill/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments,
                                         super_vol=300,
                                         drop_super_tip=False,
                                         mix_n=wash_mix,
                                         mix_vol=200,
                                         wash_tip_vol=300,
                                         super_tip_vol=200,
                                         remaining=eth_remaining,
                                         mag_engage_height=mag_engage_height,
                                         pause_s=pause_mag)

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
                       super_vol=380,
                       tip_vol=200,
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
        pipette_left.pick_up_tip(tiprack_elution_1.wells_by_name()[col])
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
        pipette_left.pick_up_tip(tiprack_elution_1.wells_by_name()[col])
        pipette_left.mix(10, 40, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.touch_tip()
        # we'll use these same tips for final transfer
        pipette_left.drop_tip()
        # t_mix = clock() - t0

    # bind to magnet
    protocol.comment('Binding beads to magnet.')

    magblock.engage(height_from_base=mag_engage_height)

    protocol.delay(seconds=pause_mag)

    protocol.comment('Transferring eluted DNA to final plate.')

    transfer_elute(pipette_left,
                   mag_plate,
                   eluate,
                   cols,
                   tiprack_elution_2,
                   50,
                   z_offset=0.5,
                   x_offset=1,
                   rate=0.25,
                   drop_tip=True,
                   mix_n=None,
                   mix_vol=None)

    magblock.disengage()
