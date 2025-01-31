import struct
from typing import List

# Define the magic header (two bytes: 0x1f, 0x9d)
MAGIC_BYTES = b'\x1f\x9d'


# ====================================================
# Core LZW functions that work directly on bytes data
# ====================================================

def lzw_compress_bytes_core(data: bytes, max_table_size: int = 4096) -> List[int]:
    """
    Compress a bytes object into a list of integer codes using LZW.
    This version works on bytes (each value is in the range 0-255).
    
    :param data: The input bytes to compress.
    :param max_table_size: Maximum allowed size of the dictionary.
    :return: A list of integer codes.
    """
    if not data:
        return []
    
    # Initialize the dictionary with all possible single-byte values.
    dict_size = 256
    # Dictionary keys are bytes objects of length 1.
    dictionary = {bytes([i]): i for i in range(dict_size)}
    
    w = b""
    result = []
    for byte in data:
        c = bytes([byte])
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            # Only add new sequences if we haven't reached the maximum table size.
            if dict_size < max_table_size:
                dictionary[wc] = dict_size
                dict_size += 1
            w = c
    if w:
        result.append(dictionary[w])
    
    return result


def lzw_decompress_bytes_core(codes: List[int], max_table_size: int = 4096) -> bytes:
    """
    Decompress a list of integer codes (produced by lzw_compress_bytes_core) back into bytes.
    
    :param codes: List of integer codes.
    :param max_table_size: Maximum allowed size of the dictionary.
    :return: The decompressed bytes.
    """
    if not codes:
        return b""
    
    dict_size = 256
    # Initialize dictionary: index -> single-byte value.
    dictionary = [bytes([i]) for i in range(dict_size)]
    
    result = []
    w = dictionary[codes[0]]
    result.append(w)
    
    for k in codes[1:]:
        if k < len(dictionary):
            entry = dictionary[k]
        elif k == dict_size:
            # Special case: current code is exactly the next code to be assigned.
            entry = w + w[:1]
        else:
            raise ValueError(f"Bad compressed code: {k}")
        
        result.append(entry)
        
        if dict_size < max_table_size:
            dictionary.append(w + entry[:1])
            dict_size += 1
        
        w = entry
    
    return b"".join(result)


def lzw_compress_bytes(data: bytes, max_table_size: int = 4096) -> bytes:
    """
    Compress a bytes object using LZW and pack the resulting integer codes into a bytes object.
    
    Each code is stored as an unsigned 16-bit (2 bytes) integer in big-endian order.
    
    :param data: Input bytes to compress.
    :param max_table_size: Maximum allowed size of the dictionary.
    :return: A bytes object containing the packed compressed codes.
    """
    codes = lzw_compress_bytes_core(data, max_table_size)
    # 'H' is the format for an unsigned short (16 bits).
    return struct.pack('>' + 'H' * len(codes), *codes)


def lzw_decompress_bytes(data: bytes, max_table_size: int = 4096) -> bytes:
    """
    Unpack a bytes object (produced by lzw_compress_bytes) into integer codes
    and decompress them using LZW.
    
    :param data: The bytes object containing the packed compressed codes.
    :param max_table_size: Maximum allowed size of the dictionary.
    :return: The decompressed bytes.
    """
    if not data:
        return b""
    
    # Each code is 2 bytes long.
    num_codes = len(data) // 2
    codes = list(struct.unpack('>' + 'H' * num_codes, data))
    return lzw_decompress_bytes_core(codes, max_table_size)


# ====================================================
# Wrapper functions for Unicode strings (with magic header)
# ====================================================

def compress_str_to_bytes(uncompressed: str, max_table_size: int = 4096) -> bytes:
    """
    Compress a Unicode string using LZW.
    
    The function:
      1. Encodes the string to UTF-8.
      2. Compresses the resulting bytes.
      3. Prepends the magic header (0x1f9d) to the compressed data.
    
    :param uncompressed: The input Unicode string.
    :param max_table_size: Maximum allowed size of the dictionary.
    :return: A bytes object containing the magic header followed by the compressed data.
    """
    # Convert string to UTF-8 encoded bytes.
    data = uncompressed.encode('utf-8')
    # Compress the data.
    compressed_data = lzw_compress_bytes(data, max_table_size)
    # Prepend the magic header.
    return MAGIC_BYTES + compressed_data


def decompress_bytes_to_bytes(compressed: bytes, max_table_size: int = 4096) -> bytes:
    """
    Decompress a bytes object (that includes the magic header) produced by compress_str_to_bytes.
    
    The function:
      1. Checks that the input starts with the magic header (0x1f9d) and removes it.
      2. Decompresses the remaining bytes using LZW.
    
    :param compressed: The bytes object with the magic header and compressed data.
    :param max_table_size: Maximum allowed size of the dictionary.
    :return: The decompressed bytes.
    :raises ValueError: If the magic header is missing.
    """
    if not compressed.startswith(MAGIC_BYTES):
        raise ValueError("Compressed data is missing the magic header 0x1f9d")
    
    # Remove the magic header.
    data_without_magic = compressed[len(MAGIC_BYTES):]
    return lzw_decompress_bytes(data_without_magic, max_table_size)


def decompress_bytes_to_str(compressed: bytes, max_table_size: int = 4096) -> str:
    """
    Decompress a bytes object (that includes the magic header) into a Unicode string.
    
    :param compressed: The bytes object with the magic header and compressed data.
    :param max_table_size: Maximum allowed size of the dictionary.
    :return: The decompressed Unicode string.
    """
    decompressed_bytes = decompress_bytes_to_bytes(compressed, max_table_size)
    return decompressed_bytes.decode('utf-8')


# ====================================================
# Example usage
# ====================================================

if __name__ == "__main__":
    # Sample text with Unicode characters.
    test_str = (
        "\nA wiki (/ˈwɪki/ ⓘ WICK-ee) is a form of hypertext publication on the internet "
        "which is collaboratively edited and managed by its audience directly through a web browser. "
        "A typical wiki contains multiple pages that can either be edited by the public or limited to "
        "use within an organization for maintaining its internal knowledge base.\n"
        "Wikis are powered by wiki software, also known as wiki engines. Being a form of content management "
        "system, these differ from other web-based systems such as blog software or static site generators in "
        "that the content is created without any defined owner or leader. Wikis have little inherent structure, "
        "allowing one to emerge according to the needs of the users.[1]\n"
    )
    
    print("Original string length:", len(test_str))
    
    # Compress the string to bytes (this adds the magic header automatically).
    compressed = compress_str_to_bytes(test_str)
    print("Compressed bytes length:", len(compressed))
    print("Compressed bytes (in hex):", compressed.hex())
    
    # Decompress the bytes back to raw bytes.
    decompressed_bytes = decompress_bytes_to_bytes(compressed)
    print("Decompressed bytes length:", len(decompressed_bytes))
    
    # Optionally, decode to Unicode string.
    decompressed_str = decompress_bytes_to_str(compressed)
    print("Decompressed string length:", len(decompressed_str))
    
    # Verify that the decompressed string matches the original.
    if test_str == decompressed_str:
        print("Success: The original and decompressed strings match.")
    else:
        print("Error: The strings do not match!")
