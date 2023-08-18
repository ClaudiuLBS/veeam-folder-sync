import hashlib
import os

class FileSystemObject:
  name: str
  hash: str
  absolute_path: str # not necessarily an absolute path
  relative_path: str # relative to the source or the replica folder

  def __init__(self, input_path: str = None) -> None:
    if input_path != None:
      self.absolute_path = input_path
      _, self.name = os.path.split(input_path)

  def __str__(self) -> str:
    return f'{self.name} {self.hash}'
  
  def __repr__(self) -> str:
    return self.__str__()

  def calculate_hash(self, content: str = None) -> None:
    content_hash = hashlib.md5(content).hexdigest()
    name_hash = hashlib.md5(self.name.encode()).hexdigest()
    self.hash = hashlib.md5((content_hash + name_hash).encode()).hexdigest()


class Blob(FileSystemObject):
  def __init__(self, input_path: str = None) -> None:
    if input_path == None: return
    super().__init__(input_path)
    
    with open(input_path, 'rb') as f:
      self.calculate_hash(f.read())
  

class Tree(FileSystemObject):
  objects: list[FileSystemObject] = []

  def calculate_hash(self, content: str = None) -> None:
    content_hashes = ''.join([x.hash for x in self.objects])
    content_hash = hashlib.md5(content_hashes.encode()).hexdigest()
    name_hash = hashlib.md5(self.name.encode()).hexdigest()
    self.hash = hashlib.md5((content_hash + name_hash).encode()).hexdigest()