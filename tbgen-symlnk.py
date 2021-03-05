#!/usr/bin/python

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2015 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2015 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski

    $FileInfo: tbgen-symlnk.py - Last Update: 2/20/2015 Ver. 1.0.5 RC 2 - Author: cooldude2k $
'''

from __future__ import absolute_import, division, print_function, unicode_literals;
import os, sys, re, subprocess;

bbexecname = "toybox";
prependfilename = False;
prependexecname = bbexecname+"-";
appendfilename = False;
appendexecname = "-"+bbexecname;
if(len(sys.argv)==1):
 cmdargpath = os.path.realpath(os.getcwd());
if(len(sys.argv)>1):
 cmdargpath = sys.argv[1];
 if(not os.path.exists(cmdargpath)):
  cmdargpath = os.path.realpath(os.getcwd());
 cmdargpath = os.path.realpath(cmdargpath);
 if(not os.path.isdir(cmdargpath)):
  cmdargpath = os.path.dirname(os.path.realpath(cmdargpath));
 if(not os.path.exists(cmdargpath)):
  cmdargpath = os.path.realpath(os.getcwd());
bbllocatp = subprocess.Popen(['which', bbexecname], stdout=subprocess.PIPE, stderr=subprocess.PIPE);
bbllocatout, bbllocaterr = bbllocatp.communicate();
bbllocatout = re.sub('\s+',' ',bbllocatout).strip();
bblistp = subprocess.Popen([bbexecname], stdout=subprocess.PIPE, stderr=subprocess.PIPE);
cmdout, cmderr = bblistp.communicate();
bblist = cmdout.replace('\n', ' ').strip();
bblist = [x.strip() for x in bblist.split(' ')];
bblisti = 0;
bblistil = len(bblist);
while(bblisti < bblistil):
 if(prependfilename==True):
  bblist[bblisti] = prependexecname+bblist[bblisti];
 if(appendfilename==True):
  bblist[bblisti] = bblist[bblisti]+appendexecname;
 bbfilename = os.path.join(cmdargpath, bblist[bblisti]);
 if(os.path.exists(bbfilename)):
  print("removed '"+bbfilename+"'");
  os.remove(bbfilename);
 print("'"+bbfilename+"' -> '"+bbllocatout+"'");
 os.symlink(bbllocatout, bbfilename);
 bblisti = bblisti + 1;
