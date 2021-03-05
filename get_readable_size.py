#!/usr/bin/python

import os, re, sys, hashlib;

# get_readable_size by Lipis
# http://stackoverflow.com/posts/14998888/revisions
def get_readable_size(bytes, precision=1, unit="IEC"):
 unit = unit.upper();
 if(unit!="IEC" and unit!="SI"):
  unit = "IEC";
 if(unit=="IEC"):
  units = [" B"," KiB"," MiB"," GiB"," TiB"," PiB"," EiB"," ZiB"];
  unitswos = ["B","KiB","MiB","GiB","TiB","PiB","EiB","ZiB"];
  unitsize = 1024.0;
 if(unit=="SI"):
  units = [" B"," kB"," MB"," GB"," TB"," PB"," EB"," ZB"];
  unitswos = ["B","kB","MB","GB","TB","PB","EB","ZB"];
  unitsize = 1000.0;
 return_val = {};
 orgbytes = bytes;
 for unit in units:
  if abs(bytes) < unitsize:
   strformat = "%3."+str(precision)+"f%s";
   pre_return_val = (strformat % (bytes, unit));
   pre_return_val = re.sub(r"([0]+) ([A-Za-z]+)", r" \2", pre_return_val);
   pre_return_val = re.sub(r"\. ([A-Za-z]+)", r" \1", pre_return_val);
   alt_return_val = pre_return_val.split();
   return_val = {'Bytes': orgbytes, 'ReadableWithSuffix': pre_return_val, 'ReadableWithoutSuffix': alt_return_val[0], 'ReadableSuffix': alt_return_val[1]}
   return return_val;
  bytes /= unitsize;
 strformat = "%."+str(precision)+"f%s";
 pre_return_val = (strformat % (bytes, "YiB"));
 pre_return_val = re.sub(r"([0]+) ([A-Za-z]+)", r" \2", pre_return_val);
 pre_return_val = re.sub(r"\. ([A-Za-z]+)", r" \1", pre_return_val);
 alt_return_val = pre_return_val.split();
 return_val = {'Bytes': orgbytes, 'ReadableWithSuffix': pre_return_val, 'ReadableWithoutSuffix': alt_return_val[0], 'ReadableSuffix': alt_return_val[1]}
 return return_val;

def get_readable_size_from_file(infile, precision=1, unit="IEC", usehashes=False, usehashtypes="md5,sha1"):
 unit = unit.upper();
 usehashtypes = usehashtypes.lower();
 getfilesize = os.path.getsize(infile);
 return_val = get_readable_size(getfilesize, precision, unit);
 if(usehashes==True):
  hashtypelist = usehashtypes.split(",");
  openfile = open(infile, "rb");
  filecontents = openfile.read();
  openfile.close();
  listnumcount = 0;
  listnumend = len(hashtypelist);
  while(listnumcount < listnumend):
   hashtypelistlow = hashtypelist[listnumcount].strip();
   hashtypelistup = hashtypelistlow.upper();
   filehash = hashlib.new(hashtypelistup);
   filehash.update(filecontents);
   filegethash = filehash.hexdigest();
   return_val.update({hashtypelistup: filegethash});
   listnumcount += 1;
 return return_val;

def get_readable_size_from_string(instring, precision=1, unit="IEC", usehashes=False, usehashtypes="md5,sha1"):
 unit = unit.upper();
 usehashtypes = usehashtypes.lower();
 getfilesize = len(instring);
 return_val = get_readable_size(getfilesize, precision, unit);
 if(usehashes==True):
  hashtypelist = usehashtypes.split(",");
  listnumcount = 0;
  listnumend = len(hashtypelist);
  while(listnumcount < listnumend):
   hashtypelistlow = hashtypelist[listnumcount].strip();
   hashtypelistup = hashtypelistlow.upper();
   filehash = hashlib.new(hashtypelistup);
   if(sys.version[0]=="2"):
    filehash.update(instring);
   if(sys.version[0]>="3"):
    filehash.update(instring.encode('utf-8'));
   filegethash = filehash.hexdigest();
   return_val.update({hashtypelistup: filegethash});
   listnumcount += 1;
 return return_val;

testfile = "/bin/sh";
print(get_readable_size_from_file(testfile, 1, "IEC", True));
print(get_readable_size_from_file(testfile, 1, "SI", True));
