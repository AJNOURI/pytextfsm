#!/usr/bin/python

import sys
import os
import textfsm
import re


# Open the template file, and initialise a new TextFSM object with it.
template_file = 'route.temp'
fsm = textfsm.TextFSM(open(template_file))


# Read input file and pass it to the FSM for parsing.
input_file = 'route.txt'
#with open(input_file) as inputf:
#    print inputf.read()

with open(input_file, "r") as inf:
  inputf = inf.read()
  fsm_results = fsm.ParseText(inputf)

print 'Header:'
print fsm.header

print '-------------------------------'

for row in fsm_results:
  print row[0],' ',row[1],' ', row[2],' ', row[3],' ',row[4],' ',row[5],' ',row[6]