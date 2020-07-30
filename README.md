# Moeller Lab OpenTrons Protocol Library	
This is an ongoing collection of OpenTrons protocols from our lab, focused on automating inexpensive and high-throughput DNA extractions and library preps for bacterial genomes and metagenomes. 

These protocols are all written in Python using the OpenTrons ProtocolAPI. Additionally, they depend on [this functions library](https://github.com/tanaes/opentrons_functions) for scripting certain convenience functions. 


## Installation

The only installation necessary is to install the [opentrons_functions](https://github.com/tanaes/opentrons_functions) library on the OT-2 robot.

## Modification and Testing

All of the protocols in the main branch of this repository are tested for execution using the OpenTrons simulation functionality. You may need to edit certain parameters for your own use, in which case you may want to execute the tests on your own computer, as well.

To do that, first clone the repository:

```{bash}
git clone https://github.com/tanaes/Moeller_Opentrons_protocol_library.git
```

Then create a new Conda environment, and install the OpenTrons API and the opentrons_function library in the new environment:

```{bash}
conda create -n opentrons python=3
```

```{bash}
pip install opentrons
pip install git+https://github.com/tanaes/opentrons_functions.git 
```

Now, you can execute the tests using the [Bats shell test package](https://github.com/sstephenson/bats) (this is cloned automatically into the Tests folder). Each collection of protocols has its own test script.

```{bash}
cd Tests
.libs/bats/bin/bats test_Quantification.bats
.libs/bats/bin/bats test_Extraction.bats
.libs/bats/bin/bats test_Library_Prep.bats
```
If the tests exit successfully, the scripts should be interpretable by the OT-2. 