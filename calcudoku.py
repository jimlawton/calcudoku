#!/usr/bin/env python

import sys
import itertools
import pprint
import operator
import csv

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

def calculate(op, combs):
  results = {}
  for subset in combs:
    if op == operator.div:
      sublist = list(subset)
      sublist.reverse()
      remainder = reduce(operator.mod, sublist)
      if remainder != 0:
        continue
      subset = sublist
    subresult = reduce(op, subset)
    if op == operator.sub:
      if subresult < 0:
        subresult = -subresult
    if subresult in results:
      results[subresult].append(subset)
    else:
      results[subresult] = [subset]
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
  if len(vals) > 2:
    vals.sort()
    print "n=%d%s" % (n, op),
    for result in vals:
      print "%d:%s" % (result, getPacked(values[result])),
      if always and always[result]:
        print "y=%s" % getPacked(always[result]),
      if never and never[result]:
        print "n=%s" % getPacked(never[result]),
    print

def generateOutput(n, values):
  output = {}
  vals = values.keys()
  if len(vals) > 2:
    vals.sort()
    for result in vals:
      output[result] = {}
      output[result]["Values"] = getPacked(values[result])
      always = getAlways(values[result])
      output[result]["Always"] = getPacked(always)
      never = getNever(n, values[result])
      output[result]["Never"] = getPacked(never)
  return output
  
# Main starts here.

NMIN = 6
NMAX = 9

for n in range(NMIN, NMAX+1):
  print "Calculating, n=%d" % n
  numberset = set(i for i in range(1, n+1))
  output = {}
  for i in range(2, n+1):
    #print " cage size:", i
    linearcombs = list(itertools.combinations(numberset, i))
    lcombs = list(combinations_with_replacement(numberset, 3))
    lcombs2 = []
    for subset in lcombs:
      if subset[0] == subset[1] and subset[1] == subset[2]:
        continue
      lcombs2.append(subset)
    lcombs = lcombs2
  
    output[i] = {}
    
    #print "  linear sums..."
    sums = calculate(operator.add, linearcombs)
    output[i]["+"] = generateOutput(n, sums)
  
    if i == 3:
      #print "  L-shaped sums..."
      # L-shaped cages...
      lsums = calculate(operator.add, lcombs)
      output[i]["+L"] = generateOutput(n, lsums)
    
    if i == 2:
      #print "  linear differences..."
      diffs = calculate(operator.sub, linearcombs)
      output[i]["-"] = generateOutput(n, diffs)
    
    #print "  linear products..."
    prods = calculate(operator.mul, linearcombs)
    output[i]["x"] = generateOutput(n, prods)
      
    if i == 3:
      #print "  L-shaped products..."
      # L-shaped cages...
      lprods = calculate(operator.mul, lcombs)
      output[i]["xL"] = generateOutput(n, lprods)
  
    if i == 2:
      #print "  linear divisions..."
      divs = calculate(operator.div, linearcombs)
      output[i][":"] = generateOutput(n, divs)
    
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
      results = output[i][rowtype].keys()
      results.sort()
      for result in results:
        row = [i, "%d%s" % (result, rowtype)]
        row.append(output[i][rowtype][result]["Values"])
        row.append(output[i][rowtype][result]["Always"])
        row.append(output[i][rowtype][result]["Never"])
        csvout.writerow(row)

print "Done!"
