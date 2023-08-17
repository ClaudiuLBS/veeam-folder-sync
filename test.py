import os
import shutil
from file_system_objects import FileSystemObject, Blob, Tree
LOG_FILE_NAME = 'log.out'

          
class FoldersSynchronization:
  def __init__(self, source_folder_path: str,  replica_folder_path: str) -> None:
    self.source_folder_path = source_folder_path
    self.replica_folder_path = replica_folder_path

  
  def walk_through_directory(self, path: str, relative_path: str = "") -> FileSystemObject:
    if os.path.isfile(path):
      b = Blob(path)
      b.relative_path = relative_path
      return b
    
    objects: list[FileSystemObject] = []
    content = os.listdir(path)
    for item in content:
      objects.append(self.walk_through_directory(os.path.join(path, item), os.path.join(relative_path, item)))
    
    tree = Tree(path)
    tree.objects = objects
    tree.calculate_hash()
    tree.relative_path = relative_path
    return tree

  def check_diff(self):
    source_tree: Tree = self.walk_through_directory(self.source_folder_path)
    source_tree.hash = '__root__'
    source_tree.name = '__root__'

    replica_tree: Tree = self.walk_through_directory(self.replica_folder_path)
    replica_tree.hash = '__root__'
    replica_tree.hash = '__root__'

    deleted: list[FileSystemObject] = []
    created: list[FileSystemObject] = []
    modified: dict[FileSystemObject, FileSystemObject] = {}

    replica_queue: list[Tree] = [replica_tree]
    source_queue: list[Tree] = [source_tree]
    while len(replica_queue) > 0 and len(source_queue) > 0:
      replica_objects = replica_queue.pop().objects
      source_objects = source_queue.pop().objects
      i = 0
      while i < len(replica_objects):
        for j in range(len(source_objects)):
          item_1 = replica_objects[i]
          item_2 = source_objects[j]
          if item_1.name == item_2.name:
            if item_1.hash != item_2.hash:
              if type(item_1) == Blob and type(item_2) == Blob:
                modified[item_1] = item_2
              else:
                replica_queue.append(item_1)
                source_queue.append(item_2)

            replica_objects.pop(i)
            source_objects.pop(j)
            i -= 1
            break
        i += 1
      created.extend(source_objects)
      deleted.extend(replica_objects)
    
    return created, deleted, modified
  
  def sync(self) -> None:
    created, deleted, modified = self.check_diff()
    for item in deleted:
      self._delete(item)
    
    for dest in modified:
      self._modify(modified[dest], dest)

    for item in created:
      self._create(item)
    
  def _delete(self, obj: FileSystemObject) -> None:
    if type(obj) == Blob:
      os.remove(obj.absolute_path)
      self._log(f"Deleted file {obj.relative_path}")
      return
    
    if len(obj.objects) == 0:
      os.rmdir(obj.absolute_path)
      self._log(f"Deleted empty directory {obj.relative_path}")
      return
    
    for item in obj.objects:
      self._delete(item)
    os.rmdir(obj.absolute_path)
    self._log(f"Deleted directory {obj.relative_path}")


  def _modify(self, source_obj: Blob, replica_obj: Blob):
    fin = open(source_obj.absolute_path, 'rb')
    fout = open(replica_obj.absolute_path, 'wb')
    fout.write(fin.read())
    fin.close()
    fout.close()
    self._log(f"Modified file {replica_obj.relative_path}")


  def _create(self, obj: FileSystemObject):
    src = os.path.join(self.source_folder_path, obj.relative_path)
    dest = os.path.join(self.replica_folder_path, obj.relative_path)
    if type(obj) == Tree:
      shutil.copytree(src, dest)
    else:
      shutil.copyfile(src, dest)

    self._log_createion(obj)

  def _log_createion(self, obj: FileSystemObject):
    if type(obj) == Blob:
      self._log(f"Created file {obj.relative_path}")
      return

    if len(obj.objects) == 0:
      self._log(f"Created empty directory {obj.relative_path}")
      return
    
    self._log(f"Created directory {obj.relative_path}")
    for item in obj.objects:
      self._log_createion(item)

  def _log(self, message: str):
    print(message)

if __name__ == '__main__':
  source_folder_path = 'source_folder'
  replica_folder_path = 'replica_folder'

  sync = FoldersSynchronization(source_folder_path, replica_folder_path)
  sync.sync()
