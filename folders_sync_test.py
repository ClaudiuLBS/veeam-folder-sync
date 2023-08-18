import os
import unittest
import shutil
from folders_sync import FoldersSynchronization


class FoldersSyncTest(unittest.TestCase):
  def setUp(self) -> None:
    self.source_folder_path = 'source_folder'
    self.replica_folder_path = 'replica_folder'
    self.log_file_path = 'log_file'

    os.makedirs(self.source_folder_path)
    os.makedirs(self.replica_folder_path)
    open('log_file', 'x').close()
    
    os.makedirs(os.path.join(self.source_folder_path, 'dir01'))
    os.makedirs(os.path.join(self.source_folder_path, 'dir02'))
    os.makedirs(os.path.join(self.source_folder_path, 'dir03'))

    os.makedirs(os.path.join(self.source_folder_path, 'dir01', 'dir11'))
    os.makedirs(os.path.join(self.source_folder_path, 'dir01', 'dir12'))
    os.makedirs(os.path.join(self.source_folder_path, 'dir02', 'dir13'))
    os.makedirs(os.path.join(self.source_folder_path, 'dir02', 'dir14'))

    open(os.path.join(self.source_folder_path, 'file01'), 'x').close()
    open(os.path.join(self.source_folder_path, 'file02'), 'x').close()

    open(os.path.join(self.source_folder_path, 'dir01', 'file11'), 'x').close()
    open(os.path.join(self.source_folder_path, 'dir01', 'file12'), 'x').close()
    open(os.path.join(self.source_folder_path, 'dir01', 'file13'), 'x').close()

    open(os.path.join(self.source_folder_path, 'dir01', 'dir12', 'file21'), 'x').close()
    open(os.path.join(self.source_folder_path, 'dir01', 'dir12', 'file22'), 'x').close()
    open(os.path.join(self.source_folder_path, 'dir02', 'dir13', 'file22'), 'x').close()

    self.syncFolders = FoldersSynchronization(self.source_folder_path, self.replica_folder_path, self.log_file_path)


  def tearDown(self) -> None:
    shutil.rmtree(self.source_folder_path)
    shutil.rmtree(self.replica_folder_path)
    os.remove(self.log_file_path)
    

  def test_before_and_after_sync(self):
    # test if the folders are different
    source_tree = self.syncFolders.walk_through_directory(self.source_folder_path)
    replica_tree = self.syncFolders.walk_through_directory(self.replica_folder_path)
    self.assertNotEqual(source_tree.hash, replica_tree.hash)

    # test if the folders are the same after the sync
    self.syncFolders.sync()
    source_tree = self.syncFolders.walk_through_directory(self.source_folder_path)
    replica_tree = self.syncFolders.walk_through_directory(self.replica_folder_path)
    self.assertEqual(source_tree.hash, replica_tree.hash)
  

  def test_create_files(self):
    self.syncFolders.sync()
    open(os.path.join(self.source_folder_path, 'dir01', 'dir12', 'file23'), 'x').close()
    open(os.path.join(self.source_folder_path, 'dir02', 'file14'), 'x').close()
    open(os.path.join(self.source_folder_path, 'dir02', 'dir13', 'file24'), 'x').close()

    print("\n\nTEST CREATE FILES")
    self.test_before_and_after_sync()


  def test_create_empty_folders(self):
    self.syncFolders.sync()
    os.makedirs(os.path.join(self.source_folder_path, 'dir04'))
    os.makedirs(os.path.join(self.source_folder_path, 'dir02', 'dir15'))

    print("\n\nTEST CREATE EMPTY FOLDERS")
    self.test_before_and_after_sync()

  
  def test_subtree_creation(self):
    self.syncFolders.sync()
    os.makedirs(os.path.join(self.source_folder_path, 'dir02', 'dir15'))
    open(os.path.join(self.source_folder_path, 'dir02', 'dir15', 'file23'), 'x').close()
    open(os.path.join(self.source_folder_path, 'dir02', 'dir15', 'file24'), 'x').close()

    print("\n\nTEST CREATE SUBTREE")
    self.test_before_and_after_sync()
    

  def test_modify_files(self):
    self.syncFolders.sync()
    f = open(os.path.join(self.source_folder_path, 'file02'), 'w')
    f.write('test1')
    f.close()

    f = open(os.path.join(self.source_folder_path, 'dir01', 'file13'), 'w')
    f.write('test2')
    f.close()

    f = open(os.path.join(self.source_folder_path, 'dir01', 'dir12', 'file21'), 'w')
    f.write('test3')
    f.close()
    
    print("\n\nTEST MODIFY FILES")
    self.test_before_and_after_sync()
    

  def test_delete_files(self):
    self.syncFolders.sync()
    os.remove(os.path.join(self.source_folder_path, 'file01'))
    os.remove(os.path.join(self.source_folder_path, 'dir01', 'file11'))
    os.remove(os.path.join(self.source_folder_path, 'dir01', 'dir12', 'file21'))

    print("\n\nTEST DELETE FILES")
    self.test_before_and_after_sync()


  def test_delete_subtree(self):
    self.syncFolders.sync()
    shutil.rmtree(os.path.join(self.source_folder_path, 'dir01'))
    shutil.rmtree(os.path.join(self.source_folder_path, 'dir02'))
    
    print("\n\nTEST DELETE SUBTREE")
    self.test_before_and_after_sync()


  def test_delete_empty_folders(self):
    self.syncFolders.sync()
    os.rmdir(os.path.join(self.source_folder_path, 'dir03'))
    os.rmdir(os.path.join(self.source_folder_path, 'dir02', 'dir14'))

    print("\n\nTEST DELETE EMPTY FOLDERS")
    self.test_before_and_after_sync()



if __name__ == '__main__':
  unittest.main()