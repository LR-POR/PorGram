#! /bin/bash
# Author: Leonel Figueiredo de Alencar
# leonel.de.alencar@ufc.br
# March 15, 2021

echo "True negatives"
grep -E "\*" $1 | grep -E " 0 [0-9]+"

echo "True positives"
grep -Ev "\*" $1 | grep -E " [1-9]+ [0-9]+"

echo "False positives"
grep -E "\*" $1 | grep -E " [1-9]+ [0-9]+"
echo "False negatives"
grep -Ev "\*" $1 | grep -E " 0 [0-9]+"
