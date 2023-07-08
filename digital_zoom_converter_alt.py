#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2016 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2016 Joshua Przyborowski - https://github.com/JoshuaPrzyborowski

    $FileInfo: digi_zoom_convert.py - Last Update: 08/15/2017 Ver. 0.0.1 RC 2 - Author: joshuatp $
'''

import argparse

def convert_to_full_frame_focal_length(sensor_focal_length, sensor_type="apsc", is_canon=False):
    """Convert sensor focal length to full frame equivalent."""
    if sensor_type == "apsc":
        full_frame_focal_length = sensor_focal_length * (1.6 if is_canon else 1.5)
    elif sensor_type == "apsh":
        full_frame_focal_length = sensor_focal_length * (1.3 if is_canon else 1.35)
    elif sensor_type == "mft":
        full_frame_focal_length = sensor_focal_length * 2.0
    elif sensor_type == "cxf":
        full_frame_focal_length = sensor_focal_length * 2.7
    elif sensor_type == "q7f":
        full_frame_focal_length = sensor_focal_length * 4.55
    else:
        full_frame_focal_length = sensor_focal_length
    return full_frame_focal_length

def convert_from_full_frame_focal_length(full_frame_focal_length, sensor_type="apsc", is_canon=False):
    """Convert full frame focal length to sensor equivalent."""
    if sensor_type == "apsc":
        sensor_focal_length = full_frame_focal_length / (1.6 if is_canon else 1.5)
    elif sensor_type == "apsh":
        sensor_focal_length = full_frame_focal_length / (1.3 if is_canon else 1.35)
    elif sensor_type == "mft":
        sensor_focal_length = full_frame_focal_length / 2.0
    elif sensor_type == "cxf":
        sensor_focal_length = full_frame_focal_length / 2.7
    elif sensor_type == "q7f":
        sensor_focal_length = full_frame_focal_length / 4.55
    else:
        sensor_focal_length = full_frame_focal_length
    return sensor_focal_length

def get_optical_zoom(maximum_focal_length, minimum_focal_length):
    """Calculate optical zoom."""
    return maximum_focal_length / minimum_focal_length

def get_minimum_focal_length(maximum_focal_length, optical_zoom):
    """Calculate minimum focal length given maximum focal length and optical zoom."""
    return maximum_focal_length / optical_zoom

def get_maximum_focal_length(minimum_focal_length, optical_zoom):
    """Calculate maximum focal length given minimum focal length and optical zoom."""
    return minimum_focal_length * optical_zoom

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--maximum", type=float, required=True, help="Maximum focal length")
    parser.add_argument("-n", "--minimum", type=float, required=True, help="Minimum focal length")
    args = parser.parse_args()

    print(get_optical_zoom(args.maximum, args.minimum))
