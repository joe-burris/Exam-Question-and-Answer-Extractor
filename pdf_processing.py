import os
from pdf2image import convert_from_path

from file_operations import rename_and_organize_files, check_and_create_folder, cleanup_files, rename_and_organize_wa_files
from openai_integration import identify_structure

def extract_images_from_pdf(pdf_path, output_folder):
    check_and_create_folder(output_folder)
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f'page_{i+1}.jpg')
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)
    return image_paths

def identify_exam_structure(image_files):
    structure_prompt = """
    Analyze this exam page and categorize it into one of the following types:
    1) Preamble
    2) Multiple choice question
    3) Blank page
    4) Written answer question
    
    Also note Written answer questions may run across multiple pages (often denoted by the presence of "CONTINUED" at the top of the page).

    Provide your answer in the following JSON format:
    {
        "type": "One of the four types listed above",
        "question_number": "If it's a question, provide the number. Otherwise, null",
        "confidence": "High, Medium, or Low"
    }

    Ensure your response is ONLY the JSON object, with no additional text.
    """
    return identify_structure(image_files, structure_prompt)

def identify_solution_structure(image_files):
    structure_prompt = """
    Analyze this solution page and categorize it into one of the following types:
    1) Preamble
    2) Multiple choice solution
    3) Blank page
    4) Written answer solution

    Note a multiple choice solution will lead with either "ANSWER: A" or "ANSWER: B" etc.

    If the page contains solutions for multiple questions, list all question numbers.

    Provide your answer in the following JSON format:
    {
        "type": "One of the four types listed above",
        "solution_number": "If it's a solution, provide all question numbers separated by commas. Otherwise, null",
        "confidence": "High, Medium, or Low"
    }

    Ensure your response is ONLY the JSON object, with no additional text.
    """
    return identify_structure(image_files, structure_prompt)

def identify_wa_solution_structure(image_files):
    structure_prompt = """
    Analyze this written answer solution page and categorize it as follows:
    types:
    - Written answer solution
    - other page
    
    Provide your answer in the following JSON format:
    {
        "type": "One of the four types listed above (text only omit the '- ')",
        "solution_number": "The 'x' value in 'Question [x]' if present, otherwise '' .",
        "is_continuation": "False if it's a new solution (ie solution_number is populated), True if it's a continuation of a previous page (ie solution_number is null).",
        "question?": "Does the word 'Question' appear on the page. True/False"
        "confidence": "High, Medium, or Low"
    }

    note on is_continuation:
    if the page is a continuation of a previous page, then is_continuation is true.
    if the page is the start of a new solution, then is_continuation is false.
    is_continuation == True WILL NOT INCLUDE a 'Question [x]' header,
    is_continuation == True WILL INCLUDE occasional subsection lettering like b), c), d), etc.

    note on solution number:
    Solution number WILL BE DENOTED with a bold 'Question [x]' at the top left of the page.
    Solution number will be the number value 'x' in 'Question [x]'.
        other indicators that a solution number is present (but not necessarily the number itself) include:
            The phrase 'Model Solution' is found near the topof the page.
            The phrase 'Chapter References' is found near the top of the page.
            You can also find a 'a)' near the bottom of the page.
        other indicators that a solution number is NOT present include:
            if is_continuation == True, then the solution number is left blank.


    Ensure your response is ONLY the JSON object, with no additional text.

    """


    return identify_structure(image_files, structure_prompt, model='gpt-4o')

def process_exam(exam_pdf, output_folder):
    exam_folder = os.path.join(output_folder, 'images_exam')
    
    exam_images = extract_images_from_pdf(exam_pdf, exam_folder)
    exam_structure = identify_exam_structure(exam_images)
    renamed_exam_files = rename_and_organize_files(exam_structure, exam_images, exam_folder, "exam")
    
    cleanup_files(exam_folder)
    
    renamed_exam_files = [f for f in os.listdir(exam_folder) if f.endswith('.jpg')]
    
    return renamed_exam_files, exam_folder

def process_solutions(solutions_pdf, output_folder):
    solution_folder = os.path.join(output_folder, 'images_solution')
    
    solution_images = extract_images_from_pdf(solutions_pdf, solution_folder)
    solution_structure = identify_solution_structure(solution_images)
    renamed_solution_files = rename_and_organize_files(solution_structure, solution_images, solution_folder, "solution")
    
    cleanup_files(solution_folder, remove_original_pages=True)
    
    renamed_solution_files = [f for f in os.listdir(solution_folder) if f.endswith('.jpg')]
    
    return renamed_solution_files, solution_folder

def process_wa_solutions(solutions_pdf, output_folder):
    solution_folder = os.path.join(output_folder, 'images_wa_solution')
    
    solution_images = extract_images_from_pdf(solutions_pdf, solution_folder)
    solution_structure = identify_wa_solution_structure(solution_images)
    
    renamed_solution_files = rename_and_organize_wa_files(solution_structure, solution_images, solution_folder, "solution")
    
    cleanup_files(solution_folder, remove_original_pages=True)
    
    renamed_solution_files = [f for f in os.listdir(solution_folder) if f.endswith('.jpg')]
    
    return renamed_solution_files, solution_folder