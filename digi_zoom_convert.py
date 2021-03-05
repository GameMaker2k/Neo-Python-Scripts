#!/usr/bin/python

from __future__ import division, print_function;

def convert_to_full_frame_focal_length(sensor_focal_length, sensor_type="apsc", is_canon=False):
 if(sensor_type=="apsc"):
  if(is_canon):
   full_frame_focal_length = sensor_focal_length * 1.6;
  else:
   full_frame_focal_length = sensor_focal_length * 1.5;
 elif(sensor_type=="apsh"):
  if(is_canon):
   full_frame_focal_length = sensor_focal_length * 1.3;
  else:
   full_frame_focal_length = sensor_focal_length * 1.35;
 elif(sensor_type=="mft"):
  full_frame_focal_length = sensor_focal_length * 2.0;
 elif(sensor_type=="cxf"):
  full_frame_focal_length = sensor_focal_length * 2.7;
 elif(sensor_type=="q7f"):
  full_frame_focal_length = sensor_focal_length * 4.55;
 else:
  full_frame_focal_length = sensor_focal_length * 1.0;
 full_frame_focal_length = '{0:g}'.format(full_frame_focal_length);
 if isinstance(full_frame_focal_length, int):
  full_frame_focal_length = int(full_frame_focal_length);
 elif isinstance(full_frame_focal_length, float):
  full_frame_focal_length = float(full_frame_focal_length);
 else:
  full_frame_focal_length = str(full_frame_focal_length);
 return full_frame_focal_length;

def convert_from_full_frame_focal_length(full_frame_focal_length, sensor_type="apsc", is_canon=False):
 if(sensor_type=="apsc"):
  if(is_canon):
   sensor_focal_length = full_frame_focal_length / 1.6;
  else:
   sensor_focal_length = full_frame_focal_length / 1.5;
 elif(sensor_type=="apsh"):
  if(is_canon):
   sensor_focal_length = full_frame_focal_length / 1.3;
  else:
   sensor_focal_length = full_frame_focal_length / 1.35;
 elif(sensor_type=="mft"):
  sensor_focal_length = full_frame_focal_length / 2.0;
 elif(sensor_type=="cxf"):
  sensor_focal_length = full_frame_focal_length / 2.7;
 elif(sensor_type=="q7f"):
  sensor_focal_length = full_frame_focal_length / 4.55;
 else:
  sensor_focal_length = full_frame_focal_length / 1.0;
 sensor_focal_length = '{0:g}'.format(sensor_focal_length);
 if isinstance(sensor_focal_length, int):
  sensor_focal_length = int(sensor_focal_length);
 elif isinstance(sensor_focal_length, float):
  sensor_focal_length = float(sensor_focal_length);
 else:
  sensor_focal_length = str(sensor_focal_length);
 return sensor_focal_length;

def get_optical_zoom(maximum_focal_length, minimum_focal_length):
 optical_zoom = maximum_focal_length / minimum_focal_length;
 optical_zoom = '{0:g}'.format(optical_zoom);
 if isinstance(optical_zoom, int):
  optical_zoom = int(optical_zoom);
 elif isinstance(optical_zoom, float):
  optical_zoom = float(optical_zoom);
 else:
  optical_zoom = str(optical_zoom);
 return optical_zoom;

print(str(get_optical_zoom(247, 3.8)));

def get_minimum_focal_length(maximum_focal_length, optical_zoom):
 minimum_focal_length = maximum_focal_length / optical_zoom;
 minimum_focal_length = '{0:g}'.format(minimum_focal_length);
 if isinstance(minimum_focal_length, int):
  minimum_focal_length = int(minimum_focal_length);
 elif isinstance(minimum_focal_length, float):
  minimum_focal_length = float(minimum_focal_length);
 else:
  minimum_focal_length = str(minimum_focal_length);
 return minimum_focal_length;

print(str(get_minimum_focal_length(247, 65)));

def get_maximum_focal_length(minimum_focal_length, optical_zoom):
 maximum_focal_length = minimum_focal_length * optical_zoom;
 maximum_focal_length = '{0:g}'.format(maximum_focal_length);
 if isinstance(maximum_focal_length, int):
  maximum_focal_length = int(maximum_focal_length);
 elif isinstance(maximum_focal_length, float):
  maximum_focal_length = float(maximum_focal_length);
 else:
  maximum_focal_length = str(maximum_focal_length);
 return maximum_focal_length;

print(str(get_maximum_focal_length(3.8, 65)));
