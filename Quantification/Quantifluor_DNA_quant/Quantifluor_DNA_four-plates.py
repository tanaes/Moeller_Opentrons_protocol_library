from opentrons import protocol_api
from opentrons.protocols.types import APIVersion
from opentrons_functions.transfer import add_buffer, get_96_from_384_wells

metadata = {
    'apiLevel': '2.5',
    'author': 'Jon Sanders'}


api_version = APIVersion(2, 5)

cols = ['{0}{1}'.format(row, col) for col in range(1, 25)
        for row in ['A', 'B']]

trash_tips = True

def run(protocol: protocol_api.ProtocolContext(api_version=api_version)):

    # define deck positions and labware

    # tips
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 6)

    tipracks_10f = [protocol.load_labware('opentrons_96_filtertiprack_10ul', x)
                    for x in [1, 4, 7, 10]]

    # plates
    reagents = protocol.load_labware('usascientific_12_reservoir_22ml',
                                     3, 'reagents')
    assay = protocol.load_labware('corning_384_wellplate_112ul_flat',
                                  9, 'assay')

    samples = [protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                     x, 'samples')
               for x in [2, 5, 8, 11]]

    # initialize pipettes
    pipette_left = protocol.load_instrument('p300_multi',
                                            'left',
                                            tip_racks=[tiprack_300])

    pipette_right = protocol.load_instrument('p10_multi',
                                             'right',
                                             tip_racks=tipracks_10f)

    # distribute 38 µL of quantification reagent into each well of the assay
    # plate. Use the same tip for the entirety of these transfers, then
    # replace it in the rack.

    add_buffer(pipette_left,
               [reagents[x] for x in ['A1', 'A2']],
               assay,
               cols,
               38,
               13000/8,
               tip=None,
               tip_vol=300,
               remaining=None,
               drop_tip=trash_tips)

    # add 2 µL of each sample to each of the wells. Mix after dispensing.
    # Dispose of these tips.
    for i, plate in enumerate(samples):
        start = i + 1
        assay_wells = get_96_from_384_wells(method='interleaved', start=start)
        pipette_right.transfer(2,
                               plate.wells(),
                               [assay[x] for x in assay_wells],
                               mix_after=(1, 10),
                               touch_tip=True,
                               trash=trash_tips,
                               new_tip='always')
