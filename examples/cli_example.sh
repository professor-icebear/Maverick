#!/bin/bash

# Example 1: Preflop analysis of AK suited
echo "Example 1: Preflop AKs"
python -m maverick.cli "As Ks" -o 3

# Example 2: Flop analysis with a flush draw
echo -e "\nExample 2: Flop with flush draw"
python -m maverick.cli "Ah Kh" -c "2h 7h Td" -o 2 -p 150 -b 50

# Example 3: Turn analysis with straight draw
echo -e "\nExample 3: Turn with straight draw"
python -m maverick.cli "Jc Tc" -c "9h 8d 2c Qh" -o 1 -p 300 -b 100 -s 800

# Example 4: River analysis
echo -e "\nExample 4: River decision"
python -m maverick.cli "Ac Ad" -c "Kc Kh Kd 2c 2h" -o 2 -p 500 -b 200 -s 1200 --position late 