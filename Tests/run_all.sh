#!/bin/bash

for test in test*.sh
do
	echo "Running test $test"
	bash $test
	# break
done