#!./libs/bats/bin/bats

@test "Testing isolate DNA extraction" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Extraction/isolate_DNA_extraction/isolate_DNA_extraction.py \
       > test_isolate_DNA_extraction.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}

@test "Testing Zymo fecal/soil magbead extraction, Part A" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Extraction/Zymo_fecal-soil_magbead/Zymo_fecal-soil_magbead_A-tube-to-plate.py \
       > Zymo_fecal-soil_magbead_A-tube-to-plate.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}

@test "Testing Zymo fecal/soil magbead extraction, Part B" {
  run opentrons_simulate \
       -L ../Labware/custom_labware \
       ../Extraction/Zymo_fecal-soil_magbead/Zymo_fecal-soil_magbead_B-extraction.py \
       > Zymo_fecal-soil_magbead_B-extraction.out
  echo "status = ${status}"
  echo "output = ${output}"
  [ "$status" -eq 0 ]
}
