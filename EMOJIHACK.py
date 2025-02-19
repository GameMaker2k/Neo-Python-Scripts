import sys

def byte_to_variation_selector(byte):
    if byte < 16:
        return unichr(0xFE00 + byte) if sys.version_info[0] == 2 else chr(0xFE00 + byte)
    else:
        return unichr(0xE0100 + (byte - 16)) if sys.version_info[0] == 2 else chr(0xE0100 + (byte - 16))

def encode(base, bytes_list):
    result = base + ''.join(byte_to_variation_selector(byte) for byte in bytes_list)
    return result

def test():
    print(encode(u'😊', [0x68, 0x65, 0x6c, 0x6f]))

if __name__ == "__main__":
    test()
