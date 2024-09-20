import os
import json
import openai

from file_operations import check_and_create_folder
from pdf_processing import process_exam, process_solutions, process_wa_solutions
from qa_matching import match_questions_and_solutions, match_wa_questions_and_solutions
from openai_integration import extract_qa_pairs, extract_wa_qa_pairs
from question_bank_structuring import structure_question_bank


# # Global dictionary to keep track of page counts
# page_counters = {}

# Set your OpenAI API key
os.environ['OPENAI_API_KEY'] = '<YOUR_API_KEY>'
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    exam_pdf = './exams/exam.pdf'
    mc_solutions_pdf = './exams/mc_solutions.pdf'
    wa_solutions_pdf = './exams/wa_solutions.pdf'
    output_folder = './exams/output'
    
    check_and_create_folder(output_folder)
    
    # Process exam
    renamed_exam_files, exam_folder = process_exam(exam_pdf, output_folder)
    
    # Process multiple choice solutions
    renamed_mc_solution_files, mc_solution_folder = process_solutions(mc_solutions_pdf, output_folder)
    
    # Match and extract multiple choice Q&A pairs
    mc_qa_pairs = match_questions_and_solutions(renamed_exam_files, renamed_mc_solution_files, exam_folder, mc_solution_folder)
    mc_extracted_qa_pairs = extract_qa_pairs(mc_qa_pairs, './prompt/prompt_qa_mc.txt')
    
    # Structure the question bank for multiple choice questions and save
    structured_mc_question_bank = structure_question_bank(mc_extracted_qa_pairs)
    
    # Extract exam name and year, format them for filename
    exam_name = structured_mc_question_bank['exam_info']['exam_name'].replace(' ', '_')
    exam_year = structured_mc_question_bank['exam_info']['exam_year'].replace(' ', '_')
    file_prefix = f"{exam_name.lower()}_{exam_year.lower()}"
    
    # Use the new file_prefix for output files
    structured_mc_output_file = os.path.join(output_folder, f'{file_prefix}_mc_question_bank.json')
    with open(structured_mc_output_file, 'w') as f:
        json.dump(structured_mc_question_bank, f, indent=2)
    
    # Process written answer solutions
    renamed_wa_solution_files, wa_solution_folder = process_wa_solutions(wa_solutions_pdf, output_folder)
    
    # Match and extract written answer Q&A pairs
    wa_qa_pairs = match_wa_questions_and_solutions(renamed_exam_files, renamed_wa_solution_files, exam_folder, wa_solution_folder)
    wa_extracted_qa_pairs = extract_wa_qa_pairs(wa_qa_pairs, './prompt/prompt_qa_wa.txt')
    
    # Structure the question bank for written answer questions and save
    structured_wa_question_bank = structure_question_bank(wa_extracted_qa_pairs)
    structured_wa_output_file = os.path.join(output_folder, f'{file_prefix}_wa_question_bank.json')
    with open(structured_wa_output_file, 'w') as f:
        json.dump(structured_wa_question_bank, f, indent=2)

if __name__ == "__main__":
    main()