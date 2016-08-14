#!/usr/bin/env python

import sys
import itertools
import pprint
import operator
import csv
import argparse

def combinations_with_replacement(iterable, r):
  pool = tuple(iterable)
  n = len(pool) 
  for indices in itertools.product(range(n), repeat=r): 
    if sorted(indices) == list(indices):
      yield tuple(pool[i] for i in indices)

def unique(iterable): 
  result = set() 
  for element in itertools.ifilterfalse(result.__contains__, iterable): 
    result.add(element) 
  return result

class PackedDigits(object):
  def __init__(self, values):
    self._values = []
    for value in values:
      self._values.append(value)
  def __str__(self):
    self._values.sort()
    text = ""
    for value in self._values:
      text += "%d" % value
    return text
  @property
  def values(self):
      return self._values

def calculate(op, combs, debug=False):
  results = {}
  for subset in combs:
    if debug:
      print "subset:", subset
    if op == operator.div:
      sublist = list(subset)
      sublist.reverse()
      remainder = reduce(operator.mod, sublist)
      if remainder != 0:
        continue
      subset = sublist
    subresult = reduce(op, subset)
    if debug:
      print "subresult:", subresult
    if op == operator.sub:
      if subresult < 0:
        subresult = -subresult
    if subresult in results:
      results[subresult].append(subset)
    else:
      results[subresult] = [subset]
    if debug:
      print "results:", results
  return results

def getValueSet(values):
  vals = []
  for subset in values:
    vals.extend(subset)
  valueset = unique(vals)
  return valueset

def getSets(values):
  sets = []
  for subset in values:
    sets.append(subset)
  return sets

def getAlways(values):
  always = []
  valueset = getValueSet(values)
  intersection = valueset.intersection(*values)
  if intersection:
    always = [intersection]
  return always
  
def getNever(n, values):
  never = []
  valueset = set([i for i in range(1, n+1)])
  difference = valueset.difference(*values)
  if difference:
    never = [difference]
  return never

def getPacked(values):
  items = ""
  for item in values:
    items += "%s " % (PackedDigits(item))  
  items = ','.join(items.split())
  return items

def printValues(n, op, values, always=None, never=None):
  vals = values.keys()
  print "n=%d%s" % (n, op),
  for result in vals:
    print "%d:%s" % (result, getPacked(values[result])),
    if always and always[result]:
      print "y=%s" % getPacked(always[result]),
    if never and never[result]:
      print "n=%s" % getPacked(never[result]),
    print

def generateOutput(n, values, debug=False):
  output = {}
  if debug:
    print "  values:", values
  vals = values.keys()
  vals.sort()
  for result in vals:
    output[result] = {}
    output[result]["Values"] = getPacked(values[result])
    always = getAlways(values[result])
    output[result]["Always"] = getPacked(always)
    never = getNever(n, values[result])
    output[result]["Never"] = getPacked(never)
  return output

def calculateOutput(n, op=None, debug=False):
  if debug:
    print "Calculating, n=%d" % n
  numberset = set(i for i in range(1, n+1))
  output = {}
  for i in range(2, n+1):
    if debug:
      print " cage size:", i
    linearcombs = list(itertools.combinations(numberset, i))
    if debug:
      print " linearcombs:", linearcombs
    lcombs = list(combinations_with_replacement(numberset, 3))
    lcombs2 = []
    for subset in lcombs:
      if subset[0] == subset[1] and subset[1] == subset[2]:
        continue
      lcombs2.append(subset)
    lcombs = lcombs2
  
    output[i] = {}
    
    if op == None or op == '+':
      if debug:
        print "  linear sums..."
      sums = calculate(operator.add, linearcombs)
      if debug:
        print "  sums:", sums
      output[i]["+"] = generateOutput(n, sums)
  
      if i == 3:
        if debug:
          print "  L-shaped sums..."
        # L-shaped cages...
        lsums = calculate(operator.add, lcombs)
        if debug:
          print "  lsums:", lsums
        output[i]["+L"] = generateOutput(n, lsums)
    
    if op == None or op == '-':
      if i == 2:
        if debug:
          print "  linear differences..."
        diffs = calculate(operator.sub, linearcombs)
        if debug:
          print "  diffs:", diffs
        output[i]["-"] = generateOutput(n, diffs)
    
    if op == None or op == 'x':
      if debug:
        print "  linear products..."
      prods = calculate(operator.mul, linearcombs)
      if debug:
        print "  prods:", prods
      output[i]["x"] = generateOutput(n, prods)
      
      if i == 3:
        if debug:
          print "  L-shaped products..."
        # L-shaped cages...
        lprods = calculate(operator.mul, lcombs)
        if debug:
          print "  lprods:", lprods
        output[i]["xL"] = generateOutput(n, lprods)
  
    if op == None or op == ':':
      if i == 2:
        if debug:
          print "  linear divisions..."
        divs = calculate(operator.div, linearcombs)
        if debug:
          print "  divs:", divs
        output[i][":"] = generateOutput(n, divs)
  if debug:
    print "  output:", output
  return output

def saveOutput(n, output, onlyType=None, debug=False):
  if onlyType == "+":
    csvout = csv.writer(open('calcudoku_%d_sums.csv' % n, 'wb'))
  elif onlyType == "-":
    csvout = csv.writer(open('calcudoku_%d_diffs.csv' % n, 'wb'))
  elif onlyType == "x":
    csvout = csv.writer(open('calcudoku_%d_prods.csv' % n, 'wb'))
  elif onlyType == ":":
    csvout = csv.writer(open('calcudoku_%d_divs.csv' % n, 'wb'))
  else:
    csvout = csv.writer(open('calcudoku_%d.csv' % n, 'wb'))
  csvout.writerow(['Type', 'Result', 'Values', 'Always', 'Never'])
  for i in range(2, n+1):
    if i == 2:
      rowtypes = [ "+", "-", "x", ":" ]
    elif i == 3:
      rowtypes = [ "+", "+L", "x", "xL" ]
    else:
      rowtypes = [ "+", "x" ]
    for rowtype in rowtypes:
      if onlyType != None and rowtype != onlyType:
        continue
      results = output[i][rowtype].keys()
      results.sort()
      for result in results:
        row = [i, "%d%s" % (result, rowtype)]
        row.append(output[i][rowtype][result]["Values"])
        row.append(output[i][rowtype][result]["Always"])
        row.append(output[i][rowtype][result]["Never"])
        csvout.writerow(row)


# Main starts here.

parser = argparse.ArgumentParser(description='Sudoku calculator.')
parser.add_argument('-d', '--debug', dest="debug", action="store_true", default=False, help='Print debugging information.')
parser.add_argument('--all', dest="all", action="store_true", default=False, help='Calculate all tables.')
parser.add_argument('-s', '--size', dest="size", type=int, default=9, help='Specify the Sudoku size (max digit, default=9)')
parser.add_argument('cage', nargs='?', type=int, help='Specify the cage size')
parser.add_argument('op', nargs='?', default='+', help='Specify the operation (default is "+")')
parser.add_argument('value', nargs='?', type=int, default=0, help='Specify the value for the operation.')

args = parser.parse_args()

NMIN = 6
NMAX = 9

if args.all:
  for n in range(NMIN, NMAX+1):
    output = calculateOutput(n, debug=args.debug)
    saveOutput(n, output)
    if n == 9:
      saveOutput(n, output, "+", debug=args.debug)
else:
    output = calculateOutput(args.size, args.op, debug=args.debug)
    if args.value == 0:
      pprint.pprint(output[args.cage])
    else:
      cage = output[args.cage]
      for op in cage.keys():
        if args.value in cage[op].keys():
          print "%3s:" % op,
          print output[args.cage][op][args.value]['Values'],
          if output[args.cage][op][args.value]['Always'] != '':
              print "always:", output[args.cage][op][args.value]['Always'],
          if output[args.cage][op][args.value]['Never'] != '':
              print "never:", output[args.cage][op][args.value]['Never'],
          print
