import os
import sys
import shutil
from datetime import datetime
from file_system_objects import FileSystemObject, Blob, Tree
          
class FoldersSynchronization:
  def __init__(self, source_folder_path: str,  replica_folder_path: str, log_file_path: str) -> None:
    self.source_folder_path = source_folder_path
    self.replica_folder_path = replica_folder_path
    self.log_file_path = log_file_path

  
  def sync(self) -> None:
    created, deleted, modified = self.check_diff()
    if len(created) == 0 and len(deleted) == 0 and len(modified.keys()) == 0:
      return
    
    self.log_file = open(self.log_file_path, 'a')
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    self._log(f"\nSync {now}")

    for item in deleted:
      self._delete(item)
    
    for dest in modified:
      self._modify(modified[dest], dest)

    for item in created:
      self._create(item)

    self.log_file.close()

  
  def walk_through_directory(self, absolute_path: str, relative_path: str = "") -> FileSystemObject:
    # If it is a file, return it
    if os.path.isfile(absolute_path):
      b = Blob(absolute_path)
      b.relative_path = relative_path
      return b
    
    # If it is a folder, add all its content to the objects list
    folder_content = os.listdir(absolute_path)
    objects: list[FileSystemObject] = []

    for item in folder_content:
      next_absolute_path = os.path.join(absolute_path, item)
      next_relative_path = os.path.join(relative_path, item)
      next_object = self.walk_through_directory(next_absolute_path, next_relative_path)
      objects.append(next_object)
    
    # Then create and return the tree
    tree = Tree(absolute_path)
    tree.objects = objects
    tree.calculate_hash()
    tree.relative_path = relative_path
    return tree
  

  def check_diff(self):
    # Both source and replica tree should have the same name and hash
    source_tree: Tree = self.walk_through_directory(self.source_folder_path)
    source_tree.hash = '__root__'
    source_tree.name = '__root__'

    replica_tree: Tree = self.walk_through_directory(self.replica_folder_path)
    replica_tree.hash = '__root__'
    replica_tree.hash = '__root__'

    # list of objects to be deleted from replica folder
    deleted: list[FileSystemObject] = []
    # list o objects to be copied from source to replica
    created: list[FileSystemObject] = []
    # dictionary of modified files - {replica_file: source_file}
    modified: dict[Blob, Blob] = {}

    # Two Queues. They start from the root, and add only Tree objects that have been modified (have the same name and different hash)
    replica_queue: list[Tree] = [replica_tree]
    source_queue: list[Tree] = [source_tree]

    while len(replica_queue) > 0 and len(source_queue) > 0:
      # Get the children of the folders
      replica_objects = replica_queue.pop().objects
      source_objects = source_queue.pop().objects

      # For every child of replica, try to find the corresponding child in the source 
      i = 0
      while i < len(replica_objects):
        for j in range(len(source_objects)):
          # cache the items
          item_1 = replica_objects[i]
          item_2 = source_objects[j]

          if item_1.name == item_2.name:
            if item_1.hash != item_2.hash:
              # Same name, different hash, and they are files => we add them to the modified files dictionary
              if type(item_1) == Blob and type(item_2) == Blob:
                modified[item_1] = item_2
              # Same name, different hash, and they are folders => we add them to queue
              else:
                replica_queue.append(item_1)
                source_queue.append(item_2)
            # Remove every match from the list
            replica_objects.pop(i)
            source_objects.pop(j)
            i -= 1
            break
        i += 1

      # The remaining objects in 'source_objects' does not appear in the replica, so we must create them  
      created.extend(source_objects)
      # The remaining objects in 'replica_objects' does not appear in the source, so we must delete them
      deleted.extend(replica_objects)
    
    return created, deleted, modified
  
    
  def _delete(self, obj: FileSystemObject) -> None:
    # File removing
    if type(obj) == Blob:
      os.remove(obj.absolute_path)
      self._log(f"Deleted file '{obj.relative_path}'")
      return

    # Empty directory removing
    if len(obj.objects) == 0:
      os.rmdir(obj.absolute_path)
      self._log(f"Deleted empty directory '{obj.relative_path}'")
      return
    
    # Non-Empty directory Removing
    for item in obj.objects:
      self._delete(item)

    os.rmdir(obj.absolute_path)
    self._log(f"Deleted directory '{obj.relative_path}'")


  def _modify(self, source_obj: Blob, replica_obj: Blob):
    # Copy the content from the source to replica file
    fin = open(source_obj.absolute_path, 'rb')
    fout = open(replica_obj.absolute_path, 'wb')
    
    fout.write(fin.read())
    self._log(f"Modified file '{replica_obj.relative_path}'")

    fin.close()
    fout.close()


  def _create(self, obj: FileSystemObject) -> None:
    source_path = os.path.join(self.source_folder_path, obj.relative_path)
    replica_path = os.path.join(self.replica_folder_path, obj.relative_path)
    
    # Copy the whole tree or the file from source to replica
    if type(obj) == Tree:
      shutil.copytree(source_path, replica_path)
    else:
      shutil.copyfile(source_path, replica_path)

    self._log_creation(obj)


  def _log_creation(self, obj: FileSystemObject) -> None:
    # Recursively log every file and folder that has been created
    if type(obj) == Blob:
      self._log(f"Created file '{obj.relative_path}'")
      return

    if len(obj.objects) == 0:
      self._log(f"Created empty directory '{obj.relative_path}'")
      return
    
    self._log(f"Created directory '{obj.relative_path}'")
    for item in obj.objects:
      self._log_creation(item)


  def _log(self, message: str) -> None:
    message += '\n'
    print(message, end='')
    self.log_file.write(message)


if __name__ == '__main__':
  source_folder_path = 'source_folder'
  replica_folder_path = 'replica_folder'
  
  sync = FoldersSynchronization(source_folder_path, replica_folder_path, 'log_file')
  sync.sync()
