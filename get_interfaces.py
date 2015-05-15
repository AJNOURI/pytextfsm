#!/usr/bin/python

import sys
import os
import textfsm
import re

def textFSMParser(inputf, templatef):
    """
    Open the template file, and initialise a new TextFSM object with it.
    :param inputf:
    :param templatef:
    :return:
    """
    fsm = textfsm.TextFSM(open(templatef))

    with open(inputf, "r") as inf:
      inputf = inf.read()
      fsm_results = fsm.ParseText(inputf)
      return fsm_results


def prefixToNH(fsmresult, prefix, ip):
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

def interfaceUP(fsmresult, interface):
    """
    IOS: show ip int brief: Is an interface UP?
    :param fsmresult:
    :param interface:
    :return:
    """
    isResult = False
    for row in fsmresult:
        #print row
        if row[0] == interface and row[4] == 'up' and row[5] == 'up':
            isResult = True
    return isResult


def interfaceIP(fsmresult, interface, ip):
    """
    IOS: show ip int brief: Is the interface configured with this IP
    :param fsmresult:
    :param interface:
    :param ip:
    :return:
    """
    isResult = False
    for row in fsmresult:
        #print row
        if row[0] == interface and row[1] == ip:
            isResult = True
    return isResult


result = textFSMParser('route.txt', 'route.temp')
print prefixToNH(result, '192.0.2.76/30', '203.0.113.183')


result = textFSMParser('get_interfaces.input', 'get_interfaces.temp')
print interfaceUP(result, 'Ethernet0/0')


print interfaceIP(result, 'Ethernet0/0', '192.168.17.7')