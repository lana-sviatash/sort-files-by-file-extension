import sys
import os
from pathlib import Path
import shutil


def normalize(name):
    translit_table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ie', 'ж': 'zh', 'з': 'z',
        'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
        'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ь': '', 'ю': 'iu', 'я': 'ia', 'ы': 'y', 'ъ': '', 'э': 'e', 'ё': 'io', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H',
        'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y', 'К': 'K',
        'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh',
        'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ь': '', 'Ю': 'Yu', 'Я': 'Ya', 'Ы': 'Y', 'Ъ': '', 'Э': 'E',
        'Ё': 'Io'
    }

    normalized_name = ''
    for char in name:
        if char in translit_table:
            normalized_name += translit_table[char]
        elif char.isalnum() and char.isascii() or char == '.':
            normalized_name += char
        else:
            normalized_name += '_'

    return normalized_name


def collect_files(directory):
    file_list = []
    directory_path = Path(directory)
    for path in directory_path.rglob('*'):
        if path.is_file():
            file_list.append(path)
    return file_list


def check_file_type(directory):
    known_types = {
        'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
        'videos': ['AVI', 'MP4', 'MOV', 'MKV'],
        'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
        'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
        'archives': ['ZIP', 'GZ', 'TAR']
    }

    file_types = set()
    unknown_types = set()

    files_by_type = {
        'images': [],
        'videos': [],
        'documents': [],
        'audio': [],
        'archives': [],
        'other': []
    }

    for file_path in collect_files(directory):
        extension = str(file_path).split('.')[-1].upper()

        found = False
        for file_type, extensions in known_types.items():
            if extension in extensions:
                files_by_type[file_type].append(file_path)
                file_types.add(extension)
                found = True
                break
        
        if not found:
            files_by_type['other'].append(file_path)
            unknown_types.add(extension)
    
    return files_by_type, file_types, unknown_types


def extract_archive(archive_path):
    archive_folder_path = os.path.dirname(archive_path)
    archive_name = os.path.splitext(os.path.basename(archive_path))[0]
    destination_folder = os.path.join(archive_folder_path, archive_name)
    shutil.unpack_archive(str(archive_path), str(destination_folder))


def move_to_folder(directory):
    files_by_type, file_types, unknown_types = check_file_type(directory)

    for file_type, file_list in files_by_type.items():
        new_folders_path = os.path.join(directory, file_type)
        os.makedirs(new_folders_path, exist_ok=True)

        for file_path in file_list:
            normalized_file_name = normalize(os.path.basename(file_path))
            destination_path = os.path.join(new_folders_path, normalized_file_name)
            shutil.move(file_path, destination_path)

            if file_type == 'archives':
                extract_archive(destination_path)
    
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)


def print_results(files_by_type, file_types, unknown_types):
    print("{:<10} | {}".format("File Type", "File Name"))
    print("-" * 50)
    
    for file_type, file_list in files_by_type.items():
        file_names = set(normalize(os.path.basename(name)) for name in file_list)
        if len(file_list) > 0: 
            print("{:<10} | {}".format(file_type, (", ".join(sorted(name for name in file_names)))))
    
    print("\nKnown Extensions: {}".format(", ".join(sorted(file_types))))
    
    if len(unknown_types) > 0:
        print("Unknown Extensions: {}".format(", ".join(sorted(unknown_types))))
    else:
        print("Unknown Extensions: None\n")
    

def main():
    try:
        folder_path = sys.argv[1]
    except IndexError:
        return 'Usage: python sort.py <folder_path>'

    if not Path(folder_path).exists():
        return f'Folder with path {folder_path} does not exist'

    files_by_type, file_types, unknown_types = check_file_type(folder_path)
    print_results(files_by_type, file_types, unknown_types)
    move_to_folder(folder_path)


if __name__ == '__main__':
    main()