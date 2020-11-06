#!./libs/bats/bin/bats

@test "Testing Hackflex full plate protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Library_Prep/Hackflex/hackflex.py \
       > test_Hackflex.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}

@test "Testing Hackflex 2 col protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Library_Prep/Hackflex/hackflex_test-2col.py \
       > test_Hackflex_test-2col.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}