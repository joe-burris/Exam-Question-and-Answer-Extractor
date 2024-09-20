import re
import os


def match_questions_and_solutions(exam_files, solution_files, exam_folder, solution_folder):
    qa_pairs = []
    exam_dict = {}
    solution_dict = {}

    for file in exam_files:
        match = re.search(r'exam_(mc|wa)_(\d+)_p(\d+)\.jpg', os.path.basename(file))
        if match:
            question_type, question_number, _ = match.groups()
            if question_number not in exam_dict:
                exam_dict[question_number] = {"type": question_type, "files": []}
            exam_dict[question_number]["files"].append(os.path.join(exam_folder, file))

    for file in solution_files:
        match = re.search(r'solution_(mc|wa)_(\d+)_p(\d+)\.jpg', os.path.basename(file))
        if match:
            _, solution_number, _ = match.groups()
            if solution_number not in solution_dict:
                solution_dict[solution_number] = []
            solution_dict[solution_number].append(os.path.join(solution_folder, file))

    all_numbers = set(exam_dict.keys()) | set(solution_dict.keys())
    for number in sorted(all_numbers, key=int):
        exam_info = exam_dict.get(number)
        solution_files = solution_dict.get(number, [])
        
        if exam_info and solution_files:
            qa_pairs.append((exam_info, solution_files))
        elif exam_info:
            print(f"Warning: No matching solution found for question {number}")
            qa_pairs.append((exam_info, []))
        else:
            print(f"Warning: Solution found for question {number}, but no corresponding exam question")

    return qa_pairs


def match_mc_questions_and_solutions(exam_files, solution_files, exam_folder, solution_folder):
    pass

def match_wa_questions_and_solutions(exam_files, solution_files, exam_folder, solution_folder):
    qa_pairs = []
    exam_dict = {}
    solution_dict = {}

    # Process exam files
    for file in exam_files:
        match = re.search(r'exam_wa_(\d+)_p(\d+)\.jpg', os.path.basename(file))
        if match:
            question_number, page_number = match.groups()
            if question_number not in exam_dict:
                exam_dict[question_number] = []
            exam_dict[question_number].append((int(page_number), os.path.join(exam_folder, file)))

    # Process solution files
    for file in solution_files:
        match = re.search(r'solution_wa_(\d+)_p(\d+)\.jpg', os.path.basename(file))
        if match:
            solution_number, page_number = match.groups()
            if solution_number not in solution_dict:
                solution_dict[solution_number] = []
            solution_dict[solution_number].append((int(page_number), os.path.join(solution_folder, file)))

    # Sort pages for each question and solution
    for question in exam_dict.values():
        question.sort(key=lambda x: x[0])
    for solution in solution_dict.values():
        solution.sort(key=lambda x: x[0])

    # Match questions with solutions
    all_numbers = set(exam_dict.keys()) | set(solution_dict.keys())
    for number in sorted(all_numbers, key=int):
        exam_files = [file for _, file in exam_dict.get(number, [])]
        solution_files = [file for _, file in solution_dict.get(number, [])]
        
        if exam_files and solution_files:
            qa_pairs.append((exam_files, solution_files))
        elif exam_files:
            print(f"Warning: No matching solution found for WA question {number}")
            qa_pairs.append((exam_files, []))
        else:
            print(f"Warning: Solution found for WA question {number}, but no corresponding exam question")

    return qa_pairs

