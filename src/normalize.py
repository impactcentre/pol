# -*- coding: utf-8 -*-
# Tomasz Olejniczak 2011, 2012
import re
import sys
import os
from optparse import OptionParser

rules = []
symbols = []
exceptions = {}
verbose = False
SEPARATOR = u";"

def readSymbol(els):
	global symbols
	res = u"["
	chars = els[2].split(u",")
	for c in chars:
		res += c.strip()
	res += u"]"
	symbols.append((els[0], res))

def readExceptions(path):
	global exceptions
	f = open(path)
	for line in f:
		line = unicode(line, "utf-8")
		if line == "u\n":
			continue
		line = line[:-1]
		els = line.split(SEPARATOR)
		exceptions.setdefault(els[0], els[1:])
	f.close()

def readRules(path):
	global rules, symbols
	f = open(path)
	for line in f:
		line = unicode(line, "utf-8")
		if line[0] == u"#":
			continue
		if line == u"\n":
			continue
		line = line[:-1]
		els = line.split(SEPARATOR)
		if len(els) < 5:
			if els[0] != u"0":
				readSymbol(els[1:5])
		else:
			if els[1] != u"0":
				for i in range(3, 7):
					if els[i] == u"":
						els[i] = u".*"
				rules.append(els[3:7] + els[0:1])
	f.close()
	for i in range(0, len(rules)):
		for j in range(0, 4):
			rules[i][j] = rules[i][j].strip()
		for (s, d) in symbols:
			rules[i][0] = rules[i][0].replace(s, d)
			rules[i][2] = rules[i][2].replace(s, d)

def contextFind(rex, leftContext, rightContext, string):
	for m in re.finditer(rex, string, re.IGNORECASE):
		if m.start() == 0:
			before = u""
		else:
			before = string[:m.start()]
		after = string[m.end():]
		#print "woyſka"
		#if string == u"woyſka":
		#	print u".*" + leftContext + u"$", before, rightContext, after
		#	print re.match(u".*" + leftContext + u"$", before, re.IGNORECASE), re.match(rightContext, after, re.IGNORECASE)
		if re.match(u".*" + leftContext + u"$", before, re.IGNORECASE) != None and re.match(rightContext, after, re.IGNORECASE) != None:
			return (before, string[m.start():m.end()], after)
	return (None, None, None)

def processToken(token, eol=False):
	global rules, verbose, exceptions
	for (left, rex, right, text, idd) in rules:
		excepts = exceptions.get(idd)
		if excepts != None:
			for ex in excepts:
				m = re.match(ex + (u"\n" if eol else u""), token)
				if m != None and len(token) == m.end():
					if verbose and contextFind(rex, left, right, token)[0] != None:
						print token, u"    #", idd, u"ignored due to", ex.encode("utf-8")
					continue
		(a, b, c) = contextFind(rex, left, right, token)
		while a != None:
			oldToken = token
			if b[0].isupper():
				token = a + text[0].upper() + text[1:] + c
			else:
				token = a + text + c
			if verbose:
				print oldToken.encode("utf-8"), token.encode("utf-8"), u"   #", (idd + u":").encode("utf-8"), left.encode("utf-8"), rex.encode("utf-8"), right.encode("utf-8")
			(a, b, c) = contextFind(rex, left, right, token)
	return token

def main(argv):
	global verbose, SEPARATOR
	usage = "%prog [OPTIONS] RULES_FILE INPUT_FILE OUTPUT_FILE"
	parser = OptionParser(usage = usage, version = "normalize.py 0.1")
	parser.add_option("-f", "--frequency-list", help="input file is frequency list", action="store_true", dest="freqlist", default=False)
	parser.add_option("-v", "--verbose", help="print information about normalized words", action="store_true", dest="verbose", default=False)
	parser.add_option("-e", "--exceptions", help="exception file", dest="exceptions", default=None)
	parser.add_option("-s", "--separator", help="CSV separator", dest="separator", default=";")
	(options, args) = parser.parse_args(argv)
	#print args
	if len(args) != 4:
		parser.print_help()
		exit()
	if options.verbose:
		verbose = True
	if options.exceptions:
		readExceptions(options.exceptions)
	SEPARATOR = unicode(options.separator, "utf-8")
	if SEPARATOR == u"\\t":
		SEPARATOR = u"\t"
	readRules(args[1])
	f = open(args[2])
	reses = []
	for line in f:
		line = unicode(line, "utf-8")
		if line == u"\n":
			continue
		if options.freqlist:
			els = line.split(u" ")
			i = 0
			for j in range(0, len(els)):
				if els[j] != u"":
					i = j
					break
			token = u""
			for j in range(i + 1, len(els)):
				token += els[j] + u" "
			token = token.strip()
			res = u" " * (7 - len(els[i])) + els[i] + u" " + processToken(token) + u"\n"
		else:
			token = line.strip()
			res = processToken(token + u"\n", eol=True)
		reses.append(res)
	f.close()
	f = open(args[3], "w")
	for res in reses:
		f.write(res.encode("utf-8"))
	f.close()
	
if __name__ == '__main__': sys.exit(main(sys.argv))

# Copyright Formal Linguistics Department, University of Warsaw  2011,2012; klf@uw.edu.pl.
# Licence GNU General Public Lincense version 2 or later
