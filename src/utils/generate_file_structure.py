import os
import time

def generate_file_structure(root_dir, output_file='file_structure.txt', skip_dirs=None):
    if skip_dirs is None:
        skip_dirs = ['bin', 'lib', 'include', 'your_lib_folder', 'archive', '.git', '__pycache__']  # Add any folders you want to skip
    with open(output_file, 'w') as file_out:
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            level = root.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            file_out.write('{}{}/\n'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                file_out.write('{}{}\n'.format(subindent, f))

if __name__ == '__main__':
    root_directory = '/Users/ctavolazzi/Code/WinfoNova/Nova_System_Git/NovaSystem'
    output_filename = f'NovaSystem_file_structure.txt{time.time()}'
    generate_file_structure(root_directory, output_filename)
