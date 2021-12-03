#!./libs/bats/bin/bats

@test "Testing single plate Quantifluor protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Quantification/Quantifluor_DNA_quant/Quantifluor_DNA_one-plate.py \
       > test_Quantifluor_DNA_one-plate.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}

@test "Testing four plate Quantifluor protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Quantification/Quantifluor_DNA_quant/Quantifluor_DNA_four-plates.py \
       > test_Quantifluor_DNA_four-plates.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}


@test "Testing 384well plate standard curve protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Quantification/Quantifluor_DNA_quant/Quantifluor_DNA_384_stdcurve.py \
       > test_Quantifluor_DNA_384_stdcurve.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}
