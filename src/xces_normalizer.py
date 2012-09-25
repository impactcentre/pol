#!/usr/bin/python
# -*- coding: utf-8 -*-
# Tomasz Olejniczak 2011, 2012

import sys
from xml.sax import make_parser
from xml.sax.handler import feature_validation, feature_external_ges
from xml.sax.saxutils import XMLFilterBase, XMLGenerator
from normalize import readRules, processToken, readExceptions

class MyAttrs:

	def __init__(self, mydict):
		self.__dict = mydict

	def copy(self):
		return MyAttrs(self.__dict.copy())

	def get(self, key):
		return self.__dict.get(key)

	def has_key(self, key):
		return self.__dict.has_key(key)

	def items(self):
		return self.__dict.items()

	def keys(self):
		return self.__dict.keys()
	
	def values(self):
		return self.__dict.values()
	
	def getLength(self):
		return len(self.__dict.keys())
	
	def getNames(self):
		return self.__dict.keys()
	
	def getType(self, key):
		return type(self.__dict.get(key))
	
	def getValue(self, key):
		return self.__dict[key]

class MyFilter(XMLFilterBase):

	def __init__(self, upstream, downstream):
		XMLFilterBase.__init__(self, upstream)
		self.__downstream = downstream
		self.__isOrth = False
		self.__isBase = False
		self.__orthText = u""

	def startElement(self, name, attrs):
		if name == u"orth":
			self.__isOrth = True
			self.__orthText = u""
		if name == u"base":
			self.__isBase = True
		self.__downstream.startElement(name, attrs)

	def endElement(self, name):
		if name == u"orth":
			self.__isOrth = False
			text = processToken(self.__orthText)
			self.__downstream.characters(text)
		if name == u"base":
			self.__isBase = False
		self.__downstream.endElement(name)

	def characters(self, content):
		if self.__isOrth:
			self.__orthText += content
		else:
			self.__downstream.characters(content)

def main(argv):
	if len(argv) != 4 and len(argv) != 5:
		print "Usage: xces_normalizer.py RULES_FILE [EXCEPTIONS_FILE] INPUT_FILE OUTPUT_FILE"
		exit()
	readRules(argv[1])
	i = 0
	if len(argv) == 5:
		readExceptions(argv[2])
		i = 1
	saxparser = make_parser()
	saxparser.setFeature(feature_validation, False)
	saxparser.setFeature(feature_external_ges, False)
	out = open(argv[3 + i], "w")
	out.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	out.write("<!DOCTYPE cesAna SYSTEM \"xcesAnaIPI.dtd\">\n")
	generator = XMLGenerator(out, "utf-8")
	filter = MyFilter(saxparser, generator)
	filter.parse(argv[2 + i])
	out.close()

if __name__ == '__main__': sys.exit(main(sys.argv))

# Copyright Formal Linguistics Department, University of Warsaw  2011,2012; klf@uw.edu.pl.
# Licence GNU General Public Lincense version 2 or later
