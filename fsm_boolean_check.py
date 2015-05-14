#!/usr/bin/python

import sys
import os
import textfsm
import re

def textFSMParser(inputf, templatef):

    # Open the template file, and initialise a new TextFSM object with it.
    fsm = textfsm.TextFSM(open(templatef))

    with open(inputf, "r") as inf:
      inputf = inf.read()
      fsm_results = fsm.ParseText(inputf)
      return fsm_results

#print 'Header:'
#print fsm.header


def fsmResultHandler(fsmresult):
    """
    Match a specific next-hop for a given route from the routing table
    :param fsmresult:
    :return:
    """
    #print fsmresult
    isResult = False
    for row in fsmresult:

        if row[2] == '192.0.2.76/30':
            #print row[2]
            #print row[3]
            for nh in row[3]:
                if nh == '203.0.113.183':
                    #print nh
                    isResult = True
    return isResult


result = textFSMParser('route.txt', 'route.temp')

print fsmResultHandler(result)
