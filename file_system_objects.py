import hashlib
import os

class FileSystemObject:
  name: str
  hash: str
  absolute_path: str
  relative_path: str

  def __init__(self, input_path: str = None) -> None:
    if input_path != None:
      self.absolute_path = input_path
      _, self.name = os.path.split(input_path)

  def calculate_hash(self, content: str = None):
    pass
  
  def __str__(self) -> str:
    return f'{self.name} {self.hash}'
  
  def __repr__(self) -> str:
    return self.__str__()


class Blob(FileSystemObject):
  def __init__(self, input_path: str = None) -> None:
    if input_path == None: return
    super().__init__(input_path)
    
    with open(input_path) as f:
      self.calculate_hash(f.read().encode())

  def calculate_hash(self, content: str = None):
    self.hash = hashlib.md5(content).hexdigest()
  

class Tree(FileSystemObject):
  objects: list[FileSystemObject] = []

  def calculate_hash(self, content: str = None):
    content_hashes = ''.join([x.hash for x in self.objects])
    self.hash = hashlib.md5(content_hashes.encode()).hexdigest()