#!./libs/bats/bin/bats

@test "Testing Hackflex full plate protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Library_Prep/Hackflex/hackflex.py \
       > test_Hackflex.out 2>&1
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}

@test "Testing Hackflex 2 col protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Library_Prep/Hackflex/hackflex_test-2col.py \
       > test_Hackflex_test-2col.out 2>&1
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}

@test "Testing Hackflex 3 col protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Library_Prep/Hackflex/hackflex_test-3col.py \
       > test_Hackflex_test-3col.out 2>&1
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}
@test "Testing Hackflex 6 col protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Library_Prep/Hackflex/hackflex_test-6col.py \
       > test_Hackflex_test-6col.out 2>&1
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}


@test "Testing Hackflex size select protocol" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Library_Prep/Hackflex/hackflex-only_size_select.py \
       > test_hackflex-only_size_select.out 2>&1
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}