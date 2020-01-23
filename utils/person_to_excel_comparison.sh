#!/bin/bash

name=$1
file=$2

grep -i $name $file
echo ""

echo "# Event"
grep -i $name $file | grep "Anmälan för" | sed 's/Anmälan för .* i //' | sed 's/ - /\#/' | cut -d'#' -f1
echo ""
#grep -i $name $file | grep "Anmälan för" | sed 's/Anmälan för .* i //' | sed 's/.*\.Amount//'

echo "# Amount"
grep -i $name $file | grep "Anmälan för" | sed 's/Anmälan för .* i //' | sed 's/ - /\#/' | cut -d'#' -f2 | sed 's/.* Amount: //' | sed 's/, fee:.*//'
echo ""

echo "# Fee"
grep -i $name $file | grep "Anmälan för" | sed 's/Anmälan för .* i //' | sed 's/ - /\#/' | cut -d'#' -f2 | sed 's/.*, fee: //' | sed 's/, lateFee:.*//'
echo ""

echo "# Late fee"
grep -i $name $file | grep "Anmälan för" | sed 's/Anmälan för .* i //' | sed 's/ - /\#/' | cut -d'#' -f2 | sed 's/.*, lateFee: //' | sed 's/^, status:/0, status:/' | sed 's/, status:.*//'
echo ""