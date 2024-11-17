import gzip

try:
    # For Python 3
    from io import BytesIO
except ImportError:
    # For Python 2
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO

class GzipBytesIO(object):
    def __init__(self, initial_bytes=None, mode='wb'):
        """
        Initialize the GzipBytesIO object.

        :param initial_bytes: Optional initial bytes to load into the buffer.
        :param mode: Mode of operation, 'wb' for writing or 'rb' for reading.
        """
        self.buffer = BytesIO()
        self.mode = mode
        if 'w' in mode:
            self.gzip_file = gzip.GzipFile(fileobj=self.buffer, mode='wb')
        elif 'r' in mode:
            if initial_bytes:
                self.buffer.write(initial_bytes)
                self.buffer.seek(0)
            self.gzip_file = gzip.GzipFile(fileobj=self.buffer, mode='rb')
        else:
            raise ValueError("Mode must be 'rb' or 'wb'")
        self.closed = False

    def write(self, data):
        """
        Write data to the GzipBytesIO buffer.

        :param data: Data to write.
        """
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        if 'w' not in self.mode:
            raise IOError("File not open for writing")
        self.gzip_file.write(data)

    def read(self, size=-1):
        """
        Read data from the GzipBytesIO buffer.

        :param size: Number of bytes to read.
        :return: Decompressed data.
        """
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        if 'r' not in self.mode:
            raise IOError("File not open for reading")
        return self.gzip_file.read(size)

    def seek(self, offset, whence=0):
        """
        Seek to a position in the GzipBytesIO buffer.

        :param offset: Offset to seek to.
        :param whence: Reference point for offset.
        """
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        return self.gzip_file.seek(offset, whence)

    def tell(self):
        """
        Tell the current position in the GzipBytesIO buffer.

        :return: Current position.
        """
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        return self.gzip_file.tell()

    def flush(self):
        """
        Flush the GzipBytesIO buffer.
        """
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        self.gzip_file.flush()

    def close(self):
        """
        Close the GzipBytesIO buffer.
        """
        if not self.closed:
            self.gzip_file.close()
            self.buffer.close()
            self.closed = True

    def getvalue(self):
        """
        Get the compressed data from the buffer.

        :return: Compressed data.
        """
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        if 'w' in self.mode:
            self.gzip_file.flush()
        return self.buffer.getvalue()
