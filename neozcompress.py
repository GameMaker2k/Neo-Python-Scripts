import struct
from typing import List

# =========================
# Bytes-based LZW functions
# =========================

def lzw_compress_bytes_core(data: bytes, max_table_size: int = 4096) -> List[int]:
    """
    Compress a bytes object into a list of integer codes using LZW.
    This function works directly on bytes.
    
    :param data: The input bytes to compress.
    :param max_table_size: Maximum size for the dictionary.
    :return: A list of integer codes.
    """
    if not data:
        return []
    
    # Initialize the dictionary with single-byte entries.
    dict_size = 256
    # The keys are bytes objects of length 1.
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
            if dict_size < max_table_size:
                dictionary[wc] = dict_size
                dict_size += 1
            w = c
    if w:
        result.append(dictionary[w])
    return result

def lzw_decompress_bytes_core(codes: List[int], max_table_size: int = 4096) -> bytes:
    """
    Decompress a list of integer codes into a bytes object using LZW.
    
    :param codes: The list of integer codes.
    :param max_table_size: Maximum size for the dictionary.
    :return: The decompressed bytes.
    """
    if not codes:
        return b""
    
    dict_size = 256
    dictionary = [bytes([i]) for i in range(dict_size)]
    
    result = []
    # First code.
    w = dictionary[codes[0]]
    result.append(w)
    
    for k in codes[1:]:
        if k < len(dictionary):
            entry = dictionary[k]
        elif k == dict_size:
            # Special case: when the current code is exactly the next code to be assigned.
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
    Compress a bytes object using LZW and return a bytes object containing the packed codes.
    
    Each integer code is stored as an unsigned 16-bit (2 bytes) big-endian value.
    
    :param data: The input bytes to compress.
    :param max_table_size: Maximum size for the dictionary.
    :return: A bytes object with the packed compressed data.
    """
    codes = lzw_compress_bytes_core(data, max_table_size)
    # Pack all codes into a bytes object. (2 bytes per code)
    return struct.pack('>' + 'H' * len(codes), *codes)

def lzw_decompress_bytes(compressed: bytes, max_table_size: int = 4096) -> bytes:
    """
    Decompress a bytes object (packed codes) back into the original bytes.
    
    The input should be in the format produced by lzw_compress_bytes.
    
    :param compressed: A bytes object with packed compressed codes.
    :param max_table_size: Maximum size for the dictionary.
    :return: The decompressed bytes.
    """
    if not compressed:
        return b""
    
    # Each code is stored as 2 bytes.
    num_codes = len(compressed) // 2
    codes = list(struct.unpack('>' + 'H' * num_codes, compressed))
    return lzw_decompress_bytes_core(codes, max_table_size)

# ================================
# Wrapper functions for Unicode
# ================================

def compress_str_to_bytes(uncompressed: str, max_table_size: int = 4096) -> bytes:
    """
    Compress a Unicode string using LZW.
    
    The string is first encoded into UTF-8 bytes, then compressed.
    
    :param uncompressed: The input Unicode string.
    :param max_table_size: Maximum size for the dictionary.
    :return: A bytes object containing the compressed data.
    """
    data = uncompressed.encode('utf-8')
    return lzw_compress_bytes(data, max_table_size)

def decompress_bytes_to_str(compressed: bytes, max_table_size: int = 4096) -> str:
    """
    Decompress a bytes object (produced by compress_str_to_bytes) back to a Unicode string.
    
    The output bytes are decoded from UTF-8.
    
    :param compressed: A bytes object containing the compressed data.
    :param max_table_size: Maximum size for the dictionary.
    :return: The decompressed Unicode string.
    """
    data = lzw_decompress_bytes(compressed, max_table_size)
    return data.decode('utf-8')


# ================================
# Example usage
# ================================


# Example usage:
if __name__ == "__main__":
    sample_text = "TOBEORNOTTOBEORTOBEORNOT"
    print("Original Text:   ", sample_text)
    
    # Compress to a list of integer codes.
    codes = lzw_compress(sample_text)
    print("Compressed Codes:", codes)
    
    # Compress to bytes.
    compressed_bytes = lzw_compress_bytes(sample_text)
    print("Compressed Bytes:", compressed_bytes)
    
    # Decompress from list of integer codes.
    decompressed_text = lzw_decompress(codes)
    print("Decompressed Text (from codes):", decompressed_text)
    
    # Decompress from bytes.
    decompressed_text_bytes = lzw_decompress_bytes(compressed_bytes)
    print("Decompressed Text (from bytes):", decompressed_text_bytes)
