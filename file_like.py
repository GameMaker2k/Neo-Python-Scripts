class FileLikeObject:
    def __init__(self):
        self.content = ""
        self.position = 0

    def write(self, data):
        self.content += data

    def read(self, size=-1):
        if size == -1:
            size = len(self.content) - self.position
        data = self.content[self.position:self.position + size]
        self.position += size
        return data

    def seek(self, position, whence=0):
        if whence == 0:
            self.position = position
        elif whence == 1:
            self.position += position
        elif whence == 2:
            self.position = len(self.content) + position

    def tell(self):
        return self.position

    def close(self):
        pass  # Add any cleanup code here, if necessary


class FileLikeDict:
    def __init__(self, infile=None):
        # Initialize with an empty dict if no infile is provided
        self.files = infile if infile else {}
        self.current_file = None
        self.mode = None
        self.closed = True

    def open(self, file_key, mode):
        if file_key not in self.files and 'x' not in mode:
            raise FileNotFoundError(f"File '{file_key}' not found")
        if 'x' in mode and file_key in self.files:
            raise FileExistsError(f"File '{file_key}' already exists")
        self.current_file = file_key
        self.mode = mode
        self.closed = False
        if 'w' in mode:
            # Clear the data for the current file if it's a write operation
            self.files[self.current_file] = ''

    def read(self):
        if self.closed:
            raise IOError("File not open")
        if 'r' not in self.mode:
            raise IOError("File not opened in read mode")
        return self.files[self.current_file]

    def write(self, data):
        if self.closed:
            raise IOError("File not open")
        if 'w' not in self.mode and 'a' not in self.mode:
            raise IOError("File not opened in write or append mode")
        if 'b' in self.mode and not isinstance(data, bytes):
            raise ValueError("Binary mode requires bytes-like object")
        if 't' in self.mode and not isinstance(data, str):
            raise ValueError("Text mode requires str object")
        if self.mode == 'w':
            self.files[self.current_file] = data
        elif self.mode == 'a':
            self.files[self.current_file] += data  # Append the data

    def close(self):
        self.current_file = None
        self.mode = None
        self.closed = True
