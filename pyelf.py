#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2019 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2019 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski

    $FileInfo: pyelf.py - Last Update: 3/18/2019 Ver. 1.0.0 RC 1 - Author: joshuatp $
'''

import os
import sys

__program_name__ = "PyELF"
__project__ = __program_name__
__project_url__ = "https://gist.github.com/KazukiPrzyborowski"
__version_info__ = (1, 0, 0, "RC 1", 1)
__version_date_info__ = (2019, 3, 18, "RC 1", 1)
__version_date__ = str(__version_date_info__[0]) + "." + str(__version_date_info__[
    1]).zfill(2) + "." + str(__version_date_info__[2]).zfill(2)
if (__version_info__[4] is not None):
    __version_date_plusrc__ = __version_date__ + \
        "-" + str(__version_date_info__[4])
if (__version_info__[4] is None):
    __version_date_plusrc__ = __version_date__
if (__version_info__[3] is not None):
    __version__ = str(__version_info__[0]) + "." + str(__version_info__[1]) + "." + str(
        __version_info__[2]) + " " + str(__version_info__[3])
if (__version_info__[3] is None):
    __version__ = str(__version_info__[
        0]) + "." + str(__version_info__[1]) + "." + str(__version_info__[2])


def get_elf_header(infile):
    if not os.path.exists(infile):
        return False
    if not os.path.isfile(infile):
        return False
    elf_file_pointer = open(infile, "rb")
    elf_file_pointer.seek(0, 0)
    elf_file_info = {}
    elf_file_info.update({'ei_magic': elf_file_pointer.read(4)})
    try:
        if (elf_file_info['ei_magic'] != b"\x7fELF"):
            return False
    except UnicodeDecodeError:
        return False
    elf_file_info.update({'ei_class': elf_file_pointer.read(1)})
    elf_file_info.update({'ei_data': elf_file_pointer.read(1)})
    elf_file_info.update({'ei_osendian': None})
    elf_file_info.update({'ei_significantbyte': None})
    if (elf_file_info['ei_data'] == b"\x01"):
        elf_file_info.update({'ei_osendian': "Little Endian"})
        elf_file_info.update({'ei_significantbyte': "LSB"})
    if (elf_file_info['ei_data'] == b"\x02"):
        elf_file_info.update({'ei_osendian': "Big Endian"})
        elf_file_info.update({'ei_significantbyte': "MSB"})
    elf_file_info.update({'ei_version': elf_file_pointer.read(1)})
    elf_file_info.update({'ei_osabi': elf_file_pointer.read(1)})
    elf_file_info.update({'ei_osname': None})
    if (elf_file_info['ei_osabi'] == b"\x00"):
        elf_file_info.update({'ei_osname': "System V"})
    if (elf_file_info['ei_osabi'] == b"\x01"):
        elf_file_info.update({'ei_osname': "HP-UX"})
    if (elf_file_info['ei_osabi'] == b"\x02"):
        elf_file_info.update({'ei_osname': "NetBSD"})
    if (elf_file_info['ei_osabi'] == b"\x03"):
        elf_file_info.update({'ei_osname': "Linux"})
    if (elf_file_info['ei_osabi'] == b"\x04"):
        elf_file_info.update({'ei_osname': "GNU Hurd"})
    if (elf_file_info['ei_osabi'] == b"\x06"):
        elf_file_info.update({'ei_osname': "Solaris"})
    if (elf_file_info['ei_osabi'] == b"\x07"):
        elf_file_info.update({'ei_osname': "AIX"})
    if (elf_file_info['ei_osabi'] == b"\x08"):
        elf_file_info.update({'ei_osname': "IRIX"})
    if (elf_file_info['ei_osabi'] == b"\x09"):
        elf_file_info.update({'ei_osname': "FreeBSD"})
    if (elf_file_info['ei_osabi'] == b"\x0a"):
        elf_file_info.update({'ei_osname': "Tru64"})
    if (elf_file_info['ei_osabi'] == b"\x0b"):
        elf_file_info.update({'ei_osname': "Novell Modesto"})
    if (elf_file_info['ei_osabi'] == b"\x0c"):
        elf_file_info.update({'ei_osname': "OpenBSD"})
    if (elf_file_info['ei_osabi'] == b"\x0d"):
        elf_file_info.update({'ei_osname': "OpenVMS"})
    if (elf_file_info['ei_osabi'] == b"\x0e"):
        elf_file_info.update({'ei_osname': "NonStop Kernel"})
    if (elf_file_info['ei_osabi'] == b"\x0f"):
        elf_file_info.update({'ei_osname': "AROS"})
    if (elf_file_info['ei_osabi'] == b"\x10"):
        elf_file_info.update({'ei_osname': "Fenix OS"})
    if (elf_file_info['ei_osabi'] == b"\x11"):
        elf_file_info.update({'ei_osname': "CloudABI"})
    elf_file_info.update({'ei_abiversion': elf_file_pointer.read(1)})
    elf_file_info.update({'ei_abiosname': None})
    if (elf_file_info['ei_abiversion'] == b"\x00"):
        elf_file_info.update({'ei_abiosname': "System V"})
    elf_file_info.update({'ei_pad': elf_file_pointer.read(7)})
    elf_file_info.update({'e_type': elf_file_pointer.read(2)})
    elf_file_info.update({'e_objecttype': None})
    elf_file_info.update({'e_objectmeaning': None})
    if (elf_file_info['e_type'] == b"\x00\x00"):
        elf_file_info.update({'e_objecttype': "ET_NONE"})
        elf_file_info.update({'e_objectmeaning': "No File Type"})
    if (elf_file_info['e_type'] == b"\x01\x00"):
        elf_file_info.update({'e_objecttype': "ET_REL"})
        elf_file_info.update({'e_objectmeaning': "Relocatable File"})
    if (elf_file_info['e_type'] == b"\x02\x00"):
        elf_file_info.update({'e_objecttype': "ET_EXEC"})
        elf_file_info.update({'e_objectmeaning': "Executable File"})
    if (elf_file_info['e_type'] == b"\x03\x00"):
        elf_file_info.update({'e_objecttype': "ET_DYN"})
        elf_file_info.update({'e_objectmeaning': "Shared Object File"})
    if (elf_file_info['e_type'] == b"\x04\x00"):
        elf_file_info.update({'e_objecttype': "ET_CORE"})
        elf_file_info.update({'e_objectmeaning': "Core File"})
    if (elf_file_info['e_type'] == b"\xfe00"):
        elf_file_info.update({'e_objecttype': "ET_LOOS"})
        elf_file_info.update({'e_objectmeaning': "Processor-Specific"})
    if (elf_file_info['e_type'] == b"\xfeff"):
        elf_file_info.update({'e_objecttype': "ET_HIOS"})
        elf_file_info.update({'e_objectmeaning': "Processor-Specific"})
    if (elf_file_info['e_type'] == b"\xff00"):
        elf_file_info.update({'e_objecttype': "ET_LOPROC"})
        elf_file_info.update({'e_objectmeaning': "Processor-Specific"})
    if (elf_file_info['e_type'] == b"\xffff"):
        elf_file_info.update({'e_objecttype': "ET_HIPROC"})
        elf_file_info.update({'e_objectmeaning': "Processor-Specific"})
    elf_file_info.update({'e_machine': elf_file_pointer.read(2)})
    elf_file_info.update({'e_architecture': None})
    if (elf_file_info['e_machine'] == b"\x00\x00"):
        elf_file_info.update({'e_architecture': "No Specific"})
    if (elf_file_info['e_machine'] == b"\x01\x00"):
        elf_file_info.update({'e_architecture': "AT&T WE 32100"})
    if (elf_file_info['e_machine'] == b"\x02\x00"):
        elf_file_info.update({'e_architecture': "SPARC"})
    if (elf_file_info['e_machine'] == b"\x03\x00"):
        elf_file_info.update({'e_architecture': "x86-32"})
    if (elf_file_info['e_machine'] == b"\x04\x00"):
        elf_file_info.update({'e_architecture': "Motorola 68000"})
    if (elf_file_info['e_machine'] == b"\x05\x00"):
        elf_file_info.update({'e_architecture': "Motorola 88000"})
    if (elf_file_info['e_machine'] == b"\x08\x00"):
        elf_file_info.update({'e_architecture': "MIPS"})
    if (elf_file_info['e_machine'] == b"\x14\x00"):
        elf_file_info.update({'e_architecture': "PowerPC"})
    if (elf_file_info['e_machine'] == b"\x16\x00"):
        elf_file_info.update({'e_architecture': "S390"})
    if (elf_file_info['e_machine'] == b"\x28\x00"):
        elf_file_info.update({'e_architecture': "ARM"})
    if (elf_file_info['e_machine'] == b"\x2a\x00"):
        elf_file_info.update({'e_architecture': "SuperH"})
    if (elf_file_info['e_machine'] == b"\x32\x00"):
        elf_file_info.update({'e_architecture': "IA-64"})
    if (elf_file_info['e_machine'] == b"\x3e\x00"):
        elf_file_info.update({'e_architecture': "x86-64"})
    if (elf_file_info['e_machine'] == b"\xb7\x00"):
        elf_file_info.update({'e_architecture': "AArch64"})
    if (elf_file_info['e_machine'] == b"\xf3\x00"):
        elf_file_info.update({'e_architecture': "RISC-V"})
    elf_file_info.update({'e_version': elf_file_pointer.read(4)})
    elf_file_info.update({'ei_osbit': None})
    elf_file_info.update({'e_entry': None})
    elf_file_info.update({'e_phoff': None})
    elf_file_info.update({'e_bit': None})
    elf_file_info.update({'e_shoff': None})
    if (elf_file_info['ei_class'] == b"\x01"):
        elf_file_info.update({'ei_osbit': "32-Bit"})
        elf_file_info.update({'e_entry': elf_file_pointer.read(4)})
        elf_file_info.update({'e_phoff': elf_file_pointer.read(4)})
        if (elf_file_info['e_phoff'] == b"\x34\x00\x00\x00"):
            elf_file_info.update({'e_bit': "32-Bit"})
        if (elf_file_info['e_phoff'] == b"\x40\x00\x00\x00"):
            elf_file_info.update({'e_bit': "64-Bit"})
        elf_file_info.update({'e_shoff': elf_file_pointer.read(4)})
    if (elf_file_info['ei_class'] == b"\x02"):
        elf_file_info.update({'ei_osbit': "64-Bit"})
        elf_file_info.update({'e_entry': elf_file_pointer.read(8)})
        elf_file_info.update({'e_phoff': elf_file_pointer.read(8)})
        if (elf_file_info['e_phoff'] == b"\x34\x00\x00\x00\x00\x00\x00\x00"):
            elf_file_info.update({'e_bit': "32-Bit"})
        if (elf_file_info['e_phoff'] == b"\x40\x00\x00\x00\x00\x00\x00\x00"):
            elf_file_info.update({'e_bit': "64-Bit"})
        elf_file_info.update({'e_shoff': elf_file_pointer.read(8)})
    elf_file_info.update({'e_flags': elf_file_pointer.read(4)})
    elf_file_info.update({'e_ehsize': elf_file_pointer.read(2)})
    elf_file_info.update({'e_phentsize': elf_file_pointer.read(2)})
    elf_file_info.update({'e_phnum': elf_file_pointer.read(2)})
    elf_file_info.update({'e_shentsize': elf_file_pointer.read(2)})
    elf_file_info.update({'e_shnum': elf_file_pointer.read(2)})
    elf_file_info.update({'e_shstrndx': elf_file_pointer.read(2)})
    if (elf_file_info['ei_class'] == b"\x01"):
        elf_file_pointer.seek(52, 0)
    if (elf_file_info['ei_class'] == b"\x02"):
        elf_file_pointer.seek(64, 0)
    if (elf_file_info['e_phnum'][1] <= 0):
        numprohead = elf_file_info['e_phnum'][0]
    else:
        numprohead = int(
            str(elf_file_info['e_phnum'][0]) + str(elf_file_info['e_phnum'][1]))
    if (elf_file_info['e_phentsize'][1] <= 0):
        proheadersize = elf_file_info['e_phentsize'][0]
    else:
        proheadersize = int(
            str(elf_file_info['e_phentsize'][0]) + str(elf_file_info['e_phentsize'][1]))
    elf_file_info.update({'p_headers': []})
    cintnumprohead = 0
    while (cintnumprohead < numprohead):
        program_headers = {}
        phstart = elf_file_pointer.tell()
        program_headers.update({'p_type': elf_file_pointer.read(4)})
        program_headers.update({'p_offset': None})
        program_headers.update({'p_vaddr': None})
        program_headers.update({'p_paddr': None})
        program_headers.update({'p_filesz': None})
        program_headers.update({'p_memsz': None})
        program_headers.update({'p_flags': None})
        program_headers.update({'p_align': None})
        if (elf_file_info['ei_class'] == b"\x01"):
            program_headers.update({'p_offset': elf_file_pointer.read(4)})
            program_headers.update({'p_vaddr': elf_file_pointer.read(4)})
            program_headers.update({'p_paddr': elf_file_pointer.read(4)})
            program_headers.update({'p_filesz': elf_file_pointer.read(4)})
            program_headers.update({'p_memsz': elf_file_pointer.read(4)})
            program_headers.update({'p_flags': elf_file_pointer.read(4)})
            program_headers.update({'p_align': elf_file_pointer.read(4)})
        if (elf_file_info['ei_class'] == b"\x02"):
            program_headers.update({'p_flags': elf_file_pointer.read(4)})
            program_headers.update({'p_offset': elf_file_pointer.read(4)})
            program_headers.update({'p_vaddr': elf_file_pointer.read(8)})
            program_headers.update({'p_paddr': elf_file_pointer.read(8)})
            program_headers.update({'p_filesz': elf_file_pointer.read(8)})
            program_headers.update({'p_memsz': elf_file_pointer.read(8)})
            program_headers.update({'p_align': elf_file_pointer.read(8)})
        elf_file_info['p_headers'].append(program_headers)
        phend = elf_file_pointer.tell()
        phsum = phend - phstart
        cintnumprohead += 1
    elf_file_info.update({'e_file_info': infile + ": ELF " + elf_file_info['e_bit'] + " " + elf_file_info['ei_significantbyte'] + " " +
                         elf_file_info['e_objectmeaning'] + " " + elf_file_info['e_architecture'] + ", version 1 (" + elf_file_info['ei_osname'] + ")"})
    elf_file_pointer.close()
    return elf_file_info


if __name__ == '__main__' and len(sys.argv) > 1:
    elf_file_info = get_elf_header(sys.argv[1])
    if (elf_file_info is not False):
        print(elf_file_info['e_file_info'])
    if (elf_file_info is False):
        print(sys.argv[1] + ": Not a ELF File")
