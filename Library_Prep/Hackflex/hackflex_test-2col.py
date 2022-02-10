from opentrons import protocol_api
from opentrons_functions.magbeads import (
    remove_supernatant, bead_wash, transfer_elute)
from opentrons_functions.transfer import add_buffer
from os.path import join, exists
from datetime import datetime
from pathlib import Path

metadata = {'apiLevel': '2.5',
            'author': 'Jon Sanders'}

# Set to `True` to perform a short run, with brief pauses and only
# one column of samples
test_run = True

if test_run:
    pause_bind = 3*60
    pause_mag = 5*60
    pause_dry = 5*60
    pause_elute = 5*60

    # Limit columns
    cols = ['A1', 'A2']
else:
    pause_bind = 3*60
    pause_mag = 5*60
    pause_dry = 5*60
    pause_elute = 5*60

    # Limit columns
    cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
            'A7', 'A8', 'A9', 'A10', 'A11', 'A12']


# bead aspiration flow rate
bead_flow = .25

# wash mix mutliplier
wash_mix = 5

tb1_cols = ['A1', 'A2']

blt_col = 'A3'

tsb_col = 'A4'

i5_col = 'A5'

# PCR MM columns
pcr_cols = ['A6', 'A7']

# Wash 1 (TWB) columns
twb_cols = ['A1', 'A2']

twb_fill = 12000

h2o_col = 'A3'

beads_col = 'A4'

# EtOH columns
eth_cols = ['A5', 'A6', 'A7']

eth_fill = 12000

# i5 primer column addition order
i5_cols = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
           'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

# get a rotation level 
i5_record_fp = join(Path.home(), '.i5_record.txt')

if exists(i5_record_fp):
    with open(i5_record_fp, 'r') as f:
        for line in f:
            last_time, last_rotation = line.rstrip().split('\t')
else:
    with open(i5_record_fp, 'w') as f:
        f.write('Timestamp\ti5_rotation\n'
                '{0}\t{1}\n'.format(datetime.now(), 11))
    last_rotation = 11

i5_rotation = (int(last_rotation) + 1) % 12

i5_cols = i5_cols[i5_rotation:] + i5_cols[:i5_rotation]


def run(protocol: protocol_api.ProtocolContext):

    # ### HackFlex Illumina-compatible library prep protocol

    # ### Deck

    # 1. samples; libraries
    # 2. reagent reservoir
    # 3. reagent strip tubes
    # 4. 300 tips (wash); 200f tips (elute)
    # 5. 10f tips (samples)
    # 6. i7 primers
    # 7. 20 tips (reagents)
    # 8. 300 tips (reagents)
    # 9. 10f tips (primers)
    # 10. mag module
    # 11. i5 primers
    # 12. trash

    # define custom labware for strip tubes block
    # reagent strip tubes:
    # 1: TB1 200 µL
    # 2: TB1 200 µL
    # 3: BLT 150 µL
    # 4: TSB 150 µL
    # 5: i5 primers 150 µL
    # 6: PCR MM 200 µL
    # 7: PCR MM 200 µL

    # buffer reservoirs:
    # 1: TWB (10 mL)
    # 2: TWB (10 mL)
    # 3: H2O (8 mL)
    # 4: beads (6 mL)
    # 5: 80% EtOH
    # 6: 80% EtOH
    # 7: 80% EtOH

    # ### Setup

    # define deck positions and labware

    # define hardware modules
    magblock = protocol.load_module('magnetic module gen2', 10)
    magblock.disengage()

    # tips
    tiprack_samples = protocol.load_labware('opentrons_96_filtertiprack_10ul',
                                            5)
    tiprack_buffers = protocol.load_labware('opentrons_96_tiprack_300ul',
                                            8)
    tiprack_wash = protocol.load_labware('opentrons_96_tiprack_300ul',
                                         4)
    tiprack_primers = protocol.load_labware('opentrons_96_'
                                               'filtertiprack_10ul',
                                               11)
    tiprack_reagents = protocol.load_labware('opentrons_96_tiprack_20ul',
                                             7)

    # reagents
    # should be new custom labware with strip tubes
    reagents = protocol.load_labware('tubeblockvwrpcrstriptube_'
                                     '96_wellplate_250ul',
                                     3,
                                     'reagents')
    buffers = protocol.load_labware('nest_12_reservoir_15ml',
                                    2,
                                    'wash buffers')

    # plates
    samples = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                    1,
                                    'samples')
    i7_primers = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                       6,
                                       'i7 primers')
    i5_primers = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                       9,
                                       'i5 primers')

    # load plate on magdeck
    # mag_plate = magblock.load_labware('vwr_96_wellplate_1000ul')
    mag_plate = magblock.load_labware('biorad_96_wellplate_200ul_pcr')

    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi',
                                            'left',
                                            tip_racks=[tiprack_buffers])
    pipette_right = protocol.load_instrument('p10_multi',
                                             'right',
                                             tip_racks=[tiprack_reagents])

    # TB1 wells
    tb1_wells = [reagents[x] for x in tb1_cols]

    # TWB wash wells
    twb_wells = [buffers[x] for x in twb_cols]

    # PCR MM wells
    pcr_wells = [reagents[x] for x in pcr_cols]

    # EtOH wells
    eth_wells = [buffers[x] for x in eth_cols]

    # DNA plate

    # Step 1: Tagmentation
    # Diluted BLT: 1 mL; 120 (150 µL) per tip
    # TB1: 2.4 mL; 300 (350 µL) per tip

    # add TB1.
    # buffer tips 1

    tb1_wells, tb1_remaining = add_buffer(pipette_left,
                                          tb1_wells,
                                          mag_plate,
                                          cols,
                                          25,
                                          200,
                                          tip=None,
                                          tip_vol=300,
                                          remaining=None,
                                          drop_tip=True,
                                          dead_vol=10)

    # add BLT
    # reagent tips 2

    # mix BLT first
    pipette_right.pick_up_tip()
    pipette_right.mix(10,
                      10,
                      reagents[blt_col])
    pipette_right.transfer(10,
                           reagents[blt_col],
                           [mag_plate[x] for x in cols],
                           mix_before=(2, 10),
                           new_tip='never')
    pipette_right.drop_tip()

    # add sample

    for col in cols:
        pipette_right.pick_up_tip(tiprack_samples[col])
        pipette_right.transfer(10,
                               samples[col],
                               mag_plate[col],
                               # mix_after=(10, 10),
                               new_tip='never',
                               trash=False)
        pipette_right.drop_tip()

    # Prompt user to remove plate and run on thermocycler
    protocol.delay(seconds=2)

    # Prompt user to remove plate and run on thermocycler
    protocol.pause('Remove plate from magblock, seal, and run '
                   'program TAG on thermocycler. Then spin down, unseal, '
                   'and return to magblock.')

    # Step 2: Stop reaction
    # TSB: 1 mL; 120 (150 µL) per tip

    # add TSB to each sample.
    # Prompt user to remove plate and run on thermocycler

    # ## Is this step going to cross-contaminate? Seems wasteful to take.
    # ## new tip for each sample. z = -1 meant to help.

    # reagent tips 2
    pipette_right.transfer(10,
                           reagents[tsb_col],
                           [mag_plate[x].top(z=-1) for x in cols],
                           touch_tip=False,
                           blow_out=True,
                           new_tip='once')

    protocol.pause('Remove plate from magblock, seal, vortex, spin, and run '
                   'program PTC on thermocycler. Then spin down, unseal, '
                   'and return to magblock.')

    # Step 3: Cleanup
    # TWB: 20 mL; 1200 (1500 µL) per tip

    # Magnet wash 2X

    # bind for specified length of time

    protocol.comment('Binding beads to magnet.')
    magblock.engage()

    protocol.delay(seconds=pause_mag)

    # ### Do first wash: 100 µL TWB
    # buffer tips 2

    # ### Do first wash
    protocol.comment('Doing wash #1.')
    twb_remaining, twb_wells = bead_wash(
                                         # global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         protocol.fixed_trash['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments
                                         twb_wells,
                                         twb_fill/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments,
                                         resuspend_beads=False,
                                         super_vol=70,
                                         rate=bead_flow,
                                         wash_vol=100,
                                         drop_super_tip=False,
                                         touch_wash_tip=True,
                                         mix_n=wash_mix,
                                         mix_vol=90,
                                         wash_tip_vol=300,
                                         super_tip_vol=200,
                                         remaining=None,
                                         pause_s=pause_mag)

    # ### Do second wash: 100 µL TWB
    # buffer tips 3
    protocol.comment('Doing wash #2.')

    twb_remaining, twb_wells = bead_wash(
                                         # global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         protocol.fixed_trash['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments
                                         twb_wells,
                                         twb_fill/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments,
                                         resuspend_beads=False,
                                         super_vol=120,
                                         rate=bead_flow,
                                         wash_vol=100,
                                         drop_super_tip=False,
                                         touch_wash_tip=True,
                                         mix_n=wash_mix,
                                         mix_vol=90,
                                         wash_tip_vol=300,
                                         super_tip_vol=200,
                                         remaining=twb_remaining,
                                         pause_s=pause_mag)

    # remove supernatant
    remove_supernatant(pipette_left,
                       mag_plate,
                       cols,
                       tiprack_wash,
                       protocol.fixed_trash['A1'],
                       super_vol=120,
                       rate=bead_flow,
                       bottom_offset=.8,
                       drop_tip=False)

    magblock.disengage()
    # remove supernatant
    # Step 3: amplification
    # MM: 3 mL; 350 (400 µL) per tip
    # buffer tips 4

    # Prompt user to unseal primer plates

    protocol.pause('Now, unseal primer plates, and uncap PCR master mix. '
                   'PLEASE NOTE: record that we are using i5 primer rotation'
                   ' {0}'.format(i5_rotation))

    pcr_wells, pcr_remaining = add_buffer(pipette_left,
                                          pcr_wells,
                                          mag_plate,
                                          cols,
                                          30,
                                          200,
                                          tip=None,
                                          tip_vol=300,
                                          remaining=None,
                                          drop_tip=True,
                                          dead_vol=10)

    # transfer primers
    for col in cols:
        pipette_right.pick_up_tip(tiprack_primers[col])
        pipette_right.transfer(10,
                               i7_primers[col],
                               mag_plate[col],
                               touch_tip=False,
                               new_tip='never',
                               trash=False)
        pipette_right.drop_tip()

    protocol.pause('Replace empty tip box in position {0} with a new box of'
                   '10µL filter tips.'.format(tiprack_primers.parent))

    for i, col in enumerate(cols):
        pipette_right.pick_up_tip(tiprack_primers[col])
        pipette_right.transfer(10,
                               i5_primers[i5_cols[i]],
                               mag_plate[col],
                               touch_tip=False,
                               new_tip='never',
                               trash=False)
        pipette_right.drop_tip()

    if not protocol.is_simulating():
        with open(i5_record_fp, 'a') as f:
            f.write('{0}\t{1}\n'.format(datetime.now(), i5_rotation))

    # Prompt user to remove plate and run on thermocycler

    protocol.pause('Remove plate from magblock, seal, vortex, spin and run '
                   'amplification program on thermocycler. Click continue when'
                   ' done.')

    protocol.delay(seconds=2)
    # Step 4: Size selection
    # H2O: 72 µL per sample; 7.2 mL; 600 per tip
    # EtOH: 400 µL per sample; 5000 per tip
    # Beads: 6 mL; 720 µL per tip

    # Prompt user to remove plate and run on thermocycler

    protocol.pause('Replace tips in position {0}'
                   ' with a fresh box'.format(tiprack_wash.parent))

    protocol.delay(seconds=2)

    protocol.pause('Remove sample plate from position {0}, seal, and store. '
                   'Place a new, clean, 96-well Nest PCR plate in position'
                   ' {0}. Remove library plate from PCR machine and spin at '
                   '280 xg for one minute. Then unseal and return to'
                   ' magblock.'.format(samples.parent))

    protocol.comment('Binding beads to magnet.')
    magblock.engage()

    protocol.delay(seconds=pause_mag)

    # Add buffers for large-cut size selection to new plate
    protocol.comment('Preparing large-cut bead conditions in new plate.')

    # add 40 µL H2O
    # buffer tips 5
    pipette_left.distribute(40,
                            buffers[h2o_col],
                            [samples[x].top(z=-1) for x in cols],
                            touch_tip=True,
                            disposal_volume=10,
                            new_tip='once')

    # Add 45 µL SPRI beads
    # buffer tips 6
    pipette_left.pick_up_tip()
    pipette_left.mix(10, 200, buffers[beads_col])
    pipette_left.distribute(45,
                            buffers[beads_col],
                            [samples[x].top(z=-1) for x in cols],
                            mix_before=(2, 40),
                            touch_tip=True,
                            disposal_volume=10,
                            new_tip='never')
    pipette_left.drop_tip()

    # Transfer 45 µL PCR supernatant to new plate
    transfer_elute(pipette_left,
                   mag_plate,
                   samples,
                   cols,
                   tiprack_wash,
                   45,
                   z_offset=0.5,
                   x_offset=1,
                   rate=0.25,
                   drop_tip=False,
                   mix_n=5,
                   mix_vol=100)

    protocol.pause('Remove and discard plate from mag block. '
                   'Move plate in position {0} to mag block, and replace '
                   'with a new, clean 96-well Nest PCR plate.'.format(
                    samples.parent))

    magblock.disengage()
    protocol.comment('Binding DNA to beads.')
    protocol.delay(seconds=pause_bind)

    protocol.comment('Binding beads to magnet.')
    magblock.engage()
    protocol.delay(seconds=pause_mag)

    # Add buffers for small-cut size selection to new plate
    # Add 20 µL SPRI beads
    # buffer tips 7
    pipette_left.pick_up_tip()
    pipette_left.mix(10, 100, buffers[beads_col])
    pipette_left.distribute(20,
                            buffers[beads_col],
                            [samples[x] for x in cols],
                            mix_before=(2, 15),
                            touch_tip=True,
                            new_tip='never')
    pipette_left.drop_tip()

    # Transfer 115 µL large-cut supernatant to new plate

    transfer_elute(pipette_left,
                   mag_plate,
                   samples,
                   cols,
                   tiprack_wash,
                   115,
                   z_offset=0.5,
                   x_offset=1,
                   rate=0.25,
                   drop_tip=False,
                   mix_n=5,
                   mix_vol=100)

    protocol.pause('Remove and discard plate from mag block. '
                   'Move plate in position {0} to mag block, and replace '
                   'with a new, clean 96-well **BioRad** PCR plate. '
                   'Also, fill Ethanol wells at this stage.'.format(
                    samples.parent))

    magblock.disengage()
    protocol.comment('Binding DNA to beads.')
    protocol.delay(seconds=pause_bind)

    protocol.comment('Binding beads to magnet.')
    magblock.engage()
    protocol.delay(seconds=pause_mag)

    # ### Do first wash: 150 µL EtOH
    # buffer tips 8
    protocol.comment('Doing wash #1.')
    eth_remaining, eth_wells = bead_wash(
                                         # global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         protocol.fixed_trash['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments,
                                         eth_wells,
                                         eth_fill/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments
                                         resuspend_beads=False,
                                         wash_vol=150,
                                         super_vol=125,
                                         drop_super_tip=False,
                                         mix_n=0,
                                         mix_vol=140,
                                         remaining=None,
                                         pause_s=pause_mag)

    # ### Do first wash: 150 µL EtOH
    # buffer tips 9
    protocol.comment('Doing wash #2.')
    eth_remaining, eth_wells = bead_wash(
                                         # global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         protocol.fixed_trash['A1'],
                                         tiprack_wash,
                                         # wash buffer arguments,
                                         eth_wells,
                                         eth_fill/8,
                                         # mix arguments
                                         tiprack_wash,
                                         # optional arguments
                                         resuspend_beads=False,
                                         wash_vol=150,
                                         super_vol=170,
                                         drop_super_tip=False,
                                         mix_n=0,
                                         mix_vol=140,
                                         remaining=eth_remaining,
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
                       protocol.fixed_trash['A1'],
                       super_vol=170,
                       rate=bead_flow,
                       bottom_offset=.3,
                       drop_tip=True)

    # dry
    protocol.delay(seconds=pause_dry)
    
    protocol.pause('Replace empty tiprack in position {0} with new rack of '
                   '200 µL filter tips.'.format(tiprack_wash.parent))

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
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.aspirate(35, buffers[h2o_col], rate=1)
        pipette_left.dispense(35, mag_plate[col].bottom(z=1))
        pipette_left.mix(10, 29, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.touch_tip()
        # we'll use these same tips for final transfer
        pipette_left.return_tip()

    protocol.delay(seconds=pause_elute)

    # bind to magnet
    protocol.comment('Binding beads to magnet.')

    magblock.engage()

    protocol.delay(seconds=pause_mag)

    protocol.comment('Transferring eluted DNA to final plate.')

    transfer_elute(pipette_left,
                   mag_plate,
                   samples,
                   cols,
                   tiprack_wash,
                   30,
                   z_offset=1.5,
                   x_offset=1,
                   rate=0.1,
                   drop_tip=True)

    magblock.disengage()

    protocol.pause('Finished! Please remember to record that this run'
                   'used primer rotation number {0}; in other words, '
                   'sample in position A1 received the i7 primer in '
                   'position A1 and the i5 primer in position {1}. '
                   'A file containing primer rotation positions and '
                   'timestamps for each run of this protocol can be '
                   'found on the robot filesystem at '
                   '{2}.'.format(i5_rotation, i5_cols[0], i5_record_fp))
