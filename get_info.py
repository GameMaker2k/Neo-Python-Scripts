#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from __future__ import print_function;

def get_info(invar):
 inname = invar.__name__;
 intype = type(invar).__name__;
 indec = id(invar);
 inhex = hex(indec);
 try:
  inprempath = invar.__package__;
 except AttributeError:
  inprempath = invar.__module__;
 inprempath = globals()[inprempath]
 inmpath = getattr(inprempath, "__file__");
 outstr = "<"+intype+" '"+inname+"' from '"+inmpath+"'>";
 return outstr;
