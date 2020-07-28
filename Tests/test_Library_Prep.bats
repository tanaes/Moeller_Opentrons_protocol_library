#!./libs/bats/bin/bats

@test "Testing Hackflex library prep" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Library_Prep/Hackflex/hackflex.py \
       > test_hackflex.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}
