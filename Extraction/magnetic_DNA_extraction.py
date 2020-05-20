from opentrons import protocol_api
from opentrons.protocols.types import APIVersion

metadata = {
    'apiLevel': '2.2',
    'author': 'Jon Sanders'}


api_version = APIVersion(2, 2)

def run(protocol: protocol_api.ProtocolContext(api_version=api_version)):

    # define deck positions and labware

    # tips
    tiprack_buffers = protocol.load_labware('opentrons_96_tiprack_300ul', 2)
    tiprack_elution = protocol.load_labware('opentrons_96_filtertiprack_200ul', 6)
    tiprack_lysate = protocol.load_labware('opentrons_96_filtertiprack_200ul', 7)
    tiprack_wash = protocol.load_labware('opentrons_96_tiprack_300ul', 8)

    # plates
    wash_buffers = protocol.load_labware('nest_12_reservoir_15ml', 5, 'wash buffers')
    reagents = protocol.load_labware('usascientific_96_wellplate_2.4ml_deep', 10, 'reagents')
    lysate = protocol.load_labware('usascientific_96_wellplate_2.4ml_deep', 4, 'lysate')
    transfer = protocol.load_labware('usascientific_96_wellplate_2.4ml_deep', 1, 'transfer plate')
    eluate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 3, 'eluate')
    waste = protocol.load_labware('nest_1_reservoir_195ml', 9, 'liquid waste')

    # define hardware modules\
    magblock = protocol.load_module('Magnetic Module', 11)

    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi', 
                                            'left',
                                            tip_racks=[tiprack_buffers])

    pipette_right = protocol.load_instrument('p10_multi', 
                                            'right',
                                            tip_racks=[])
    
    protocol.home()
    
    cols = ['A1', 'A2', 'A3']
    
    pipette_left.distribute(20,
                        reagents.wells_by_name()['A1'],
                        [transfer[x] for x in cols],
                        touch_tip=True,
                        disposal_volume=10,
                        trash=True,
                        new_tip='once')
    
    # this needs to be modified to position transfer aspirate location accurately. 

    for col in cols:
        # do first transfer.
        pipette_left.pick_up_tip(tiprack_lysate.wells_by_name()[col])
        pipette_left.aspirate(180, lysate[col].bottom(z=15), rate=0.25)
        pipette_left.air_gap(10)
        pipette_left.dispense(200, transfer[col])
        pipette_left.blow_out()
        pipette_left.touch_tip(v_offset=-1)

        # do second transfer.
        pipette_left.aspirate(180, lysate[col].bottom(z=10), rate=0.25)
        pipette_left.air_gap(10)
        pipette_left.dispense(200, transfer[col])
        pipette_left.blow_out()
        pipette_left.touch_tip(v_offset=-1)

        pipette_left.return_tip()

    isopropanol_wells = ['A1','A2','A3','A4','A5','A6']
    ethanol_wells = ['A7','A8','A9','A10','A11','A12']

    protocol.pause('Seal plate in Position 1 and place on rotater for 5 minutes.'
                   ' Then return to magnetic module in position 11 and press Resume')
    
    mag_plate = magblock.load_labware('usascientific_96_wellplate_2.4ml_deep')

    # bind for 7 minutes

    magblock.engage()
    protocol.delay(minutes=7)
    
    # remove supernatant
    for col in cols:
        # four transfers to remove supernatant:
        pipette_left.pick_up_tip(tiprack_lysate.wells_by_name()[col])
        for i in range(0,4):
            pipette_left.aspirate(190, mag_plate[col], rate=1)
            pipette_left.air_gap(10)
            pipette_left.dispense(200, waste['A1'])
            pipette_left.blow_out()
        # we're done with these tips at this point
        pipette_left.drop_tip()

    # disengage magnet
    magblock.disengage()

    # add isopropanol
    pipette_left.transfer(400,
                          [wash_buffers[x] for x in isopropanol_wells],
                          [transfer[x] for x in cols],
                          touch_tip=False,
                          trash=True,
                          new_tip='once')

    # mix
    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.mix(5, 200, mag_plate[col].bottom(z=4))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.return_tip()

    # engage magnet
    magblock.engage()
    protocol.delay(minutes=7)
    
    # remove supernatant
    for col in cols:
        # two transfers to remove supernatant:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        for i in range(0,2):
            pipette_left.aspirate(200, mag_plate[col], rate=1)
            pipette_left.air_gap(10)
            pipette_left.dispense(200, waste['A1'])
            pipette_left.blow_out()
        # return tips
        pipette_left.return_tip()

    # disengage magnet
    magblock.disengage()

    # add ethanol
    pipette_left.transfer(300,
                          [wash_buffers[x] for x in ethanol_wells],
                          [transfer[x] for x in cols],
                          touch_tip=False,
                          trash=True,
                          new_tip='once')

    # mix
    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.mix(5, 200, mag_plate[col].bottom(z=4))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.return_tip()

    # engage magnet
    magblock.engage()
    protocol.delay(minutes=7)

    # remove supernatant
    for col in cols:
        # two transfers to remove supernatant:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        for i in range(0,2):
            pipette_left.aspirate(180, mag_plate[col], rate=1)
            pipette_left.air_gap(10)
            pipette_left.dispense(180, waste['A1'])
            pipette_left.blow_out()
        # return tips
        pipette_left.return_tip()

    # disengage magnet
    magblock.disengage()

    # add ethanol
    pipette_left.transfer(300,
                          [wash_buffers[x] for x in ethanol_wells],
                          [transfer[x] for x in cols],
                          touch_tip=False,
                          trash=True,
                          new_tip='once')

    # mix
    for col in cols:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        pipette_left.mix(5, 200, mag_plate[col].bottom(z=4))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.return_tip()

    # engage magnet
    magblock.engage()
    protocol.delay(minutes=7)
    
    # remove supernatant
    for col in cols:
        # two transfers to remove supernatant:
        pipette_left.pick_up_tip(tiprack_wash.wells_by_name()[col])
        for i in range(0,2):
            pipette_left.aspirate(180, mag_plate[col], rate=1)
            pipette_left.air_gap(10)
            pipette_left.dispense(180, waste['A1'])
            pipette_left.blow_out()
        # we're done with these tips at this point
        pipette_left.drop_tip()

    # dry
    protocol.delay(minutes=5)

    # transfer elution buffer to mag plate

    magblock.disengage()

    # add elution buffer and mix
    for col in cols:
        pipette_left.pick_up_tip(tiprack_elution.wells_by_name()[col])
        pipette_left.aspirate(70, reagents['A2'], rate=1)
        pipette_left.dispense(70, mag_plate[col].bottom(z=1))
        pipette_left.mix(10, 60, mag_plate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.touch_tip()
        # we'll use these same tips for final transfer
        pipette_left.return_tip()

    # wait five minutes to elute further
    protocol.delay(minutes=2)

    magblock.engage()
    protocol.delay(minutes=7)

    for col in cols:
        pipette_left.pick_up_tip(tiprack_elution.wells_by_name()[col])
        pipette_left.aspirate(70, mag_plate[col], rate=1)
        pipette_left.dispense(70, eluate[col].bottom(z=1))
        pipette_left.blow_out(mag_plate[col].top())
        pipette_left.touch_tip()
        # we're done with these tips now
        pipette_left.drop_tip()
