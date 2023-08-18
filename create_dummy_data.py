import os

def create_dummy_data(source_folder_path: str):
  os.makedirs(source_folder_path)
  
  os.makedirs(os.path.join(source_folder_path, 'dir01'))
  os.makedirs(os.path.join(source_folder_path, 'dir02'))
  os.makedirs(os.path.join(source_folder_path, 'dir03'))

  os.makedirs(os.path.join(source_folder_path, 'dir01', 'dir11'))
  os.makedirs(os.path.join(source_folder_path, 'dir01', 'dir12'))
  os.makedirs(os.path.join(source_folder_path, 'dir02', 'dir13'))
  os.makedirs(os.path.join(source_folder_path, 'dir02', 'dir14'))

  open(os.path.join(source_folder_path, 'file01'), 'x').close()
  open(os.path.join(source_folder_path, 'file02'), 'x').close()

  open(os.path.join(source_folder_path, 'dir01', 'file11'), 'x').close()
  open(os.path.join(source_folder_path, 'dir01', 'file12'), 'x').close()
  open(os.path.join(source_folder_path, 'dir01', 'file13'), 'x').close()

  open(os.path.join(source_folder_path, 'dir01', 'dir12', 'file21'), 'x').close()
  open(os.path.join(source_folder_path, 'dir01', 'dir12', 'file22'), 'x').close()
  open(os.path.join(source_folder_path, 'dir02', 'dir13', 'file22'), 'x').close()


if __name__ == '__main__':
  create_dummy_data('source_folder')
  create_dummy_data('replica_folder')