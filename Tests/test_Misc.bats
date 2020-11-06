#!./libs/bats/bin/bats

@test "Testing Misc copy plate protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Misc/copy_plate.py \
       > test_Misc_copy_plate.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}