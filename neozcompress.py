import struct
from typing import List

def lzw_compress(uncompressed: str, max_table_size: int = 4096) -> List[int]:
    """
    Compress a string to a list of output symbols using the LZW algorithm.

    :param uncompressed: The input string to compress.
    :param max_table_size: Maximum size for the dictionary.
    :return: A list of integer codes representing the compressed data.
    """
    if not uncompressed:
        return []
    
    # Initialize the dictionary with single-character mappings.
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}
    
    w = ""
    result = []
    for c in uncompressed:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            # Output the code for w.
            result.append(dictionary[w])
            # Only add new sequences if we haven't reached the maximum table size.
            if dict_size < max_table_size:
                dictionary[wc] = dict_size
                dict_size += 1
            w = c

    # Output the code for w if it's not empty.
    if w:
        result.append(dictionary[w])
    
    return result


def lzw_decompress(compressed: List[int], max_table_size: int = 4096) -> str:
    """
    Decompress a list of output symbols to a string using the LZW algorithm.

    :param compressed: The list of integer codes to decompress.
    :param max_table_size: Maximum size for the dictionary.
    :return: The original uncompressed string.
    """
    if not compressed:
        return ""
    
    # Initialize the dictionary with single-character mappings.
    dict_size = 256
    dictionary = [chr(i) for i in range(dict_size)]
    
    # Start with the first code.
    result = []
    w = dictionary[compressed[0]]
    result.append(w)
    
    # Process the rest of the codes.
    for k in compressed[1:]:
        if k < len(dictionary):
            entry = dictionary[k]
        elif k == dict_size:
            # Special case: entry = w + w[0]
            entry = w + w[0]
        else:
            raise ValueError(f"Bad compressed code: {k}")
        
        result.append(entry)
        # Add new entry to the dictionary if the maximum size hasn't been reached.
        if dict_size < max_table_size:
            dictionary.append(w + entry[0])
            dict_size += 1
        w = entry

    return "".join(result)


def lzw_compress_bytes(uncompressed: str, max_table_size: int = 4096) -> bytes:
    """
    Compress a string and return a bytes object.
    
    This function wraps lzw_compress() by converting its list-of-int output into a bytes
    object, where each code is stored as an unsigned 16-bit integer.
    
    :param uncompressed: The input string to compress.
    :param max_table_size: Maximum size for the dictionary.
    :return: A bytes object containing the packed compressed data.
    """
    # Get the list of integer codes from the standard LZW compression.
    codes = lzw_compress(uncompressed, max_table_size)
    
    # Pack each integer as an unsigned short (16 bits) in big-endian order.
    # Note: With max_table_size=4096 the codes fit in 12 bits and are safe to pack in 16 bits.
    return struct.pack('>' + 'H' * len(codes), *codes)


def lzw_decompress_bytes(compressed_bytes: bytes, max_table_size: int = 4096) -> str:
    """
    Decompress a bytes object (produced by lzw_compress_bytes) back to a string.
    
    This function unpacks the bytes object into a list of integers (codes) and then uses
    lzw_decompress() to reconstruct the original string.
    
    :param compressed_bytes: The bytes object containing the packed compressed data.
    :param max_table_size: Maximum size for the dictionary.
    :return: The original uncompressed string.
    """
    # Each code is stored as 2 bytes. Compute the number of codes.
    num_codes = len(compressed_bytes) // 2
    
    # Unpack the bytes object to a tuple of integers.
    codes = list(struct.unpack('>' + 'H' * num_codes, compressed_bytes))
    
    # Decompress using the standard LZW decompression.
    return lzw_decompress(codes, max_table_size)


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
