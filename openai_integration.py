import os
import json
import openai
import base64


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def identify_structure(image_files, prompt, model="gpt-4o-mini"):
    structure = []
    for image_file in image_files:
        encoded_image = encode_image(image_file)
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ],
                }
            ],
            response_format={ "type": "json_object" },
            max_tokens=300,
        )
        try:
            structure.append(json.loads(response.choices[0].message['content']))
        except json.JSONDecodeError:
            print(f"Error parsing JSON for {image_file}. Response: {response.choices[0].message['content']}")
            structure.append({"type": "Error", "question_number": None, "solution_number": None, "confidence": "Low"})
    return structure

def extract_qa_pairs(qa_pairs, prompt_file):
    with open(prompt_file, 'r') as file:
        qa_inner_prompt = file.read().strip()

    extracted_qa_pairs = []
    for question_info, solution_files in qa_pairs:
        question_type = "Multiple choice" if question_info["type"] == "mc" else "Written answer"
        qa_prompt = f"Extract the full text of this {question_type} question and its corresponding solution. No preamble, no postscript, no additional text, just the json as described: {qa_inner_prompt}"
        
        encoded_question_images = [encode_image(file) for file in question_info["files"]]
        encoded_images_solution = [encode_image(file) for file in solution_files]
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": qa_prompt},
                            *[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} for img in encoded_question_images + encoded_images_solution]
                        ],
                    }
                ],
                response_format={ "type": "json_object" },
                max_tokens=4096,
            )
            
            try:
                extracted_qa_pairs.append(json.loads(response.choices[0].message['content']))
            except json.JSONDecodeError:
                print(f"Failed to parse response as JSON for question {question_info['files'][0]}. Storing raw content.")
                extracted_qa_pairs.append({"raw_content": response.choices[0].message['content'], "question_file": question_info['files'][0]})
        
        except openai.error.OpenAIError as e:
            print(f"OpenAI API error for question {question_info['files'][0]}: {str(e)}")
            extracted_qa_pairs.append({"error": str(e), "question_file": question_info['files'][0]})

    return extracted_qa_pairs

def extract_mc_qa_pairs(qa_pairs, prompt_file):
    pass

def extract_wa_qa_pairs(qa_pairs, prompt_file):
    with open(prompt_file, 'r') as file:
        qa_inner_prompt = file.read().strip()

    extracted_qa_pairs = []
    for question_info, solution_files in qa_pairs:
        qa_prompt = f"""
        Extract the full text of this written answer question and its corresponding solution.
        The question may span multiple images, and the solution may also span multiple images.
        Ensure you capture all information across all provided images.
        No preamble, no postscript, no additional text, just the json as described:
        {qa_inner_prompt}
        """
        
        encoded_question_images = [encode_image(file) for file in question_info]
        encoded_solution_images = [encode_image(file) for file in solution_files]
        
        all_images = encoded_question_images + encoded_solution_images
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": qa_prompt},
                            *[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} for img in all_images]
                        ],
                    }
                ],
                response_format={ "type": "json_object" },
                max_tokens=4096,
            )
            
            try:
                extracted_qa = json.loads(response.choices[0].message['content'])
                extracted_qa['question_files'] = question_info
                extracted_qa['solution_files'] = solution_files
                extracted_qa_pairs.append(extracted_qa)
            except json.JSONDecodeError:
                print(f"Failed to parse response as JSON for WA question {question_info['files'][0]}. Storing raw content.")
                extracted_qa_pairs.append({
                    "raw_content": response.choices[0].message['content'],
                    "question_files": question_info['files'],
                    "solution_files": solution_files
                })
        
        except openai.error.OpenAIError as e:
            print(f"OpenAI API error for WA question {question_info[0]}: {str(e)}")
            extracted_qa_pairs.append({
                "error": str(e),
                "question_files": question_info,
                "solution_files": solution_files
            })

    return extracted_qa_pairs