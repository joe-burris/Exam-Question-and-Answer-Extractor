# Exam Question and Answer Extractor

## Objective

This project aims to automate the process of extracting questions and answers from actuarial exam PDFs and their corresponding solution PDFs. The exams and solutions are typically published across various PDF files, typically dividing out the multiple choice sections from the written answer sections as well as the answer sheets from the question sheets. The main goals are:

1. Convert exam and solution PDFs into images.
2. Identify and categorize different types of questions (multiple-choice and written answer).
3. Match questions with their corresponding solutions.
4. Extract the full text of questions and answers using OpenAI's GPT-4 model.
5. Structure the extracted data into a standardized JSON format for easy use and integration.

## Key Features

- PDF to image conversion
- Automatic identification of question and solution types
- Matching of exam questions with their solutions
- AI-powered text extraction from images
- Separate processing for multiple-choice and written answer questions
- Structured output in JSON format

## How It Works

1. **PDF Processing**: The system first converts exam and solution PDFs into images.

2. **Structure Identification**: It then analyzes each image to identify whether it's a question, solution, or other type of content.

3. **Question-Answer Matching**: The system matches questions from the exam with their corresponding solutions.

4. **Text Extraction**: Using OpenAI's GPT-4 model, the system extracts the full text of questions and answers from the images.

5. **Data Structuring**: Finally, it structures the extracted data into a standardized JSON format.

## Setup and Usage

Actuarial exam MLC can be found here:
http://web.archive.org/web/20170624121139/https://www.soa.org/education/exam-req/syllabus-study-materials/edu-multiple-choice-exam.aspx

## Output

The system generates two main output files:
- `mc_question_bank.json`: Contains structured data for multiple-choice questions and answers.
- `wa_question_bank.json`: Contains structured data for written answer questions and answers.

## Dependencies

- Python 3.x
- OpenAI API
- pdf2image

## Project Structure
.
├── main.py

├── pdf_processing.py

├── file_operations.py

├── openai_integration.py

├── question_bank_structuring.py

├── utils.py

├── qa_matching.py

├── prompt/

│ ├── prompt_qa_mc.txt

│ └── prompt_qa_wa.txt

└── exams/

├── exam.pdf

├── mc_solutions.pdf

├── wa_solutions.pdf

└── output/
├── mc_question_bank.json
└── wa_question_bank.json
