import os
import re
import shutil


def check_and_create_folder(folder_path):
    os.makedirs(folder_path, exist_ok=True)

def rename_and_organize_files(structure, image_files, folder, prefix):
    renamed_files = []
    current_question = None
    page_counters = {}
    
    for i, page in enumerate(structure):
        if page['type'] in ["Multiple choice question", "Written answer question"]:
            number = re.sub(r'[^0-9]', '', str(page['question_number']))
            question_type = "mc" if "multiple choice" in page['type'].lower() else "wa"
            current_question = f"{question_type}_{number}"
            page_counters[current_question] = 1
            new_name = f"{prefix}_{current_question}_p1.jpg"
            renamed_files.append(rename_file(image_files[i], folder, new_name))
        elif page['type'] in ["Multiple choice solution", "Written answer solution"]:
            solution_numbers = page.get('solution_number', '').split(',')
            solution_numbers = [re.sub(r'[^0-9]', '', num.strip()) for num in solution_numbers if num.strip()]
            if solution_numbers:
                for num in solution_numbers:
                    solution_type = "mc" if "multiple choice" in page['type'].lower() else "wa"
                    solution_key = f"{solution_type}_{num}"
                    page_counters[solution_key] = 1
                    new_name = f"{prefix}_{solution_key}_p1.jpg"
                    renamed_files.append(copy_and_rename_file(image_files[i], folder, new_name))
            else:
                new_name = f"{prefix}_unknown_{i+1}.jpg"
                renamed_files.append(rename_file(image_files[i], folder, new_name))
        elif current_question and page['type'] != "Blank page":
            page_counters[current_question] += 1
            new_name = f"{prefix}_{current_question}_p{page_counters[current_question]}.jpg"
            renamed_files.append(rename_file(image_files[i], folder, new_name))
        else:
            new_name = f"{prefix}_other_{i+1}.jpg"
            current_question = None
            renamed_files.append(rename_file(image_files[i], folder, new_name))
    
    return renamed_files

def rename_and_organize_wa_files(structure, image_files, folder, prefix):
    renamed_files = []
    current_question = None

    page_counters = {}
    
    for i, page in enumerate(structure):
        if page['type'] in ["Multiple choice question", "Written answer question"]:
            number = re.sub(r'[^0-9]', '', str(page['question_number']))
            question_type = "mc" if "multiple choice" in page['type'].lower() else "wa"
            current_question = f"{question_type}_{number}"
            page_counters[current_question] = 1
            new_name = f"{prefix}_{current_question}_p1.jpg"
            renamed_files.append(rename_file(image_files[i], folder, new_name))
        elif page['type'] in ["Multiple choice solution", "Written answer solution"]:
            if page['type'] == "Multiple choice solution":
                solution_numbers = page.get('solution_number', '').split(',')
                solution_numbers = [re.sub(r'[^0-9]', '', num.strip()) for num in solution_numbers if num.strip()]
                for num in solution_numbers:
                    solution_key = f"mc_{num}"
                    page_counters[solution_key] = 1
                    new_name = f"{prefix}_{solution_key}_p1.jpg"
                    renamed_files.append(copy_and_rename_file(image_files[i], folder, new_name))
            else:  # Written answer solution
                solution_number = re.sub(r'[^0-9]', '', str(page['solution_number']))
                if solution_number:
                    last_solution_number = solution_number
                elif page['is_continuation'] == 'True' and last_solution_number:
                    solution_number = last_solution_number
                else:
                    solution_number = 'unknown'
                
                solution_key = f"wa_{solution_number}"
                if page['is_continuation'] == "false":
                    page_counters[solution_key] = 1
                else:
                    page_counters[solution_key] = page_counters.get(solution_key, 0) + 1
                new_name = f"{prefix}_{solution_key}_p{page_counters[solution_key]}.jpg"
                renamed_files.append(rename_file(image_files[i], folder, new_name))
        else:
            new_name = f"{prefix}_unknown_{i+1}.jpg"
            renamed_files.append(rename_file(image_files[i], folder, new_name))
    
    return renamed_files

def copy_and_rename_file(old_file, folder, new_name):
    old_path = old_file
    new_path = os.path.join(folder, new_name)
    
    counter = 1
    while os.path.exists(new_path):
        base_name, ext = os.path.splitext(new_name)
        new_name = f"{base_name}_{counter}{ext}"
        new_path = os.path.join(folder, new_name)
        counter += 1
    
    shutil.copy2(old_path, new_path)
    return new_path

def rename_file(old_file, folder, new_name):
    old_path = old_file
    new_path = os.path.join(folder, new_name)
    
    while os.path.exists(new_path):
        match = re.search(r'(.+)_p(\d+)\.jpg', new_name)
        if match:
            base_name = match.group(1)
            page_num = int(match.group(2))
            new_name = f"{base_name}_p{page_num + 1}.jpg"
            new_path = os.path.join(folder, new_name)
        else:
            new_name = f"{new_name[:-4]}_1.jpg"
            new_path = os.path.join(folder, new_name)
    
    os.rename(old_path, new_path)
    return new_path

def cleanup_files(folder, remove_original_pages=False):
    for filename in os.listdir(folder):
        if 'other' in filename.lower() or (remove_original_pages and filename.startswith('page_')) or 'unknown' in filename.lower():
            file_path = os.path.join(folder, filename)
            os.remove(file_path)

            print(f"Removed file: {file_path}")
