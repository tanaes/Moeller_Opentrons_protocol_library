from opentrons import protocol_api
from opentrons_functions.magbeads import (
    remove_supernatant, bead_wash, transfer_elute)
from opentrons_functions.transfer import add_buffer


metadata = {'apiLevel': '2.5',
            'author': 'Jon Sanders'}

# Set to `True` to perform a short run, with brief pauses and only 
# one column of samples
test_run = True

if test_run:
    pause_bind = 5*60
    pause_mag = 10*60
    pause_dry = 5*60
    pause_elute = 5*60

    # Limit columns
    cols = ['A1', 'A2']
else:
    pause_bind = 5*60
    pause_mag = 10*60
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
    # 11. waste
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
    # tiprack_samples = protocol.load_labware('opentrons_96_filtertiprack_10ul', 
    #                                         5)
    tiprack_buffers = protocol.load_labware('opentrons_96_tiprack_300ul', 
                                            8)
    tiprack_wash = protocol.load_labware('opentrons_96_tiprack_300ul', 
                                         4)
    #tiprack_primers = protocol.load_labware('opentrons_96_filtertiprack_10ul', 
                                            # 9)
    # tiprack_reagents = protocol.load_labware('opentrons_96_tiprack_20ul', 
    #                                          7)

    # reagents
    # should be new custom labware with strip tubes
    reagents = protocol.load_labware('tubeblockvwrpcrstriptube_96_wellplate_250ul',
                                     3, 'reagents')
    buffers = protocol.load_labware('nest_12_reservoir_15ml', 
                                    2, 'wash buffers')
    waste = protocol.load_labware('nest_1_reservoir_195ml',
                                  11, 'liquid waste')

    # plates
    samples = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                   1, 'samples')
    elution = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                       6, 'elution')

    # load plate on magdeck
    # mag_plate = magblock.load_labware('vwr_96_wellplate_1000ul')
    mag_plate = magblock.load_labware('biorad_96_wellplate_200ul_pcr')

    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi', 
                                            'left',
                                            tip_racks=[tiprack_buffers])
    # pipette_right = protocol.load_instrument('p10_multi', 
    #                                         'right',
    #                                         tip_racks=[tiprack_reagents])

    # TB1 wells
    tb1_wells = [reagents[x] for x in tb1_cols]

    # TWB wash wells
    twb_wells = [buffers[x] for x in twb_cols]

    # PCR MM wells
    pcr_wells = [reagents[x] for x in pcr_cols]

    # EtOH wells
    eth_wells = [buffers[x] for x in eth_cols]



    protocol.pause('Start with 45 µL test DNA in columns 1 and 2 of a plate on the '
                   'mag block'.format(samples.parent))


    # Add buffers for large-cut size selection to new plate
    protocol.comment('Adding beads for large-cut size selection to plate.')
    cols=['A1', 'A2']
    # add 40 µL H2O
    # buffer tips 5
    pipette_left.distribute(40,
                            buffers[h2o_col],
                            [mag_plate[x].top(z=-1) for x in cols],
                            touch_tip=False,
                            disposal_volume=10,
                            new_tip='once') 

    # Add 45 µL SPRI beads
    # buffer tips 6
    pipette_left.pick_up_tip()
    pipette_left.mix(10, 200, buffers[beads_col])
    pipette_left.distribute(45,
                            buffers[beads_col],
                            [mag_plate[x].top(z=-1) for x in cols],
                            mix_before=(2,40),
                            touch_tip=False,
                            disposal_volume=10,
                            new_tip='never')
    pipette_left.drop_tip() 

    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.mix(10,
                         80,
                         mag_plate[col])
        pipette_left.return_tip()



    protocol.comment('Binding beads to magnet.')
    magblock.engage()
    protocol.delay(seconds=pause_mag)


    protocol.pause('Make sure a clean PCR plate is in position 1 for '
                   'small-cut size selection.')

    # Add buffers for small-cut size selection to new plate
    # Add 15 µL SPRI beads
    # buffer tips 7
    pipette_left.pick_up_tip()
    pipette_left.mix(10, 100, buffers[beads_col])
    pipette_left.distribute(14,
                            buffers[beads_col],
                            [samples[x] for x in cols],
                            mix_before=(2,15),
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
                   mix_n=7,
                   mix_vol=100)



    ########
    # Elute large-cut fraction into elution plate
    ########

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

    protocol.comment('Transferring large-cut DNA to final plate.')

    dest_cols = ['A1', 'A2']
    for i, col in enumerate(cols):
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.aspirate(30, mag_plate[col].bottom(z=1), rate=0.1)
        pipette_left.dispense(30, elution[dest_cols[i]].bottom(z=1))
        pipette_left.return_tip()  

    magblock.disengage()




    protocol.pause('Remove plate from mag block and discard. '
                   'Move plate in position {0} to mag block.'.format(
                    samples.parent))

    protocol.comment('Binding beads to magnet.')
    magblock.engage()
    protocol.delay(seconds=pause_mag)



    ########
    # Elute small-cut fraction into elution plate
    ########


    protocol.comment('Transferring small-cut DNA to final plate.')

    dest_cols = ['A3', 'A4']
    for i, col in enumerate(cols):
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.aspirate(110, mag_plate[col].bottom(z=1), rate=0.1)
        pipette_left.dispense(110, elution[dest_cols[i]].bottom(z=1))
        pipette_left.return_tip()  

    magblock.disengage()




    cols = ['A2']

    # ### Do first wash: 150 µL EtOH
    # buffer tips 8
    protocol.comment('Doing wash #1.')
    eth_remaining, eth_wells = bead_wash(# global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         waste['A1'],
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
    eth_remaining, eth_wells = bead_wash(# global arguments
                                         protocol,
                                         magblock,
                                         pipette_left,
                                         mag_plate,
                                         cols,
                                         # super arguments
                                         waste['A1'],
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

    cols = ['A1', 'A2']

    remove_supernatant(pipette_left,
                       mag_plate,
                       cols,
                       tiprack_wash,
                       waste['A1'],
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


    protocol.comment('Transferring small-cut DNA to final plate.')

    dest_cols = ['A5', 'A6']
    for i, col in enumerate(cols):
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.aspirate(30, mag_plate[col].bottom(z=1), rate=0.1)
        pipette_left.dispense(30, elution[dest_cols[i]].bottom(z=1))
        pipette_left.return_tip()  


    magblock.disengage()
