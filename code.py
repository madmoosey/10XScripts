import ast

import openai
from pprint import pprint


client = openai.OpenAI(api_key = "")


def get_function_details(filename):
    with open(filename, "r") as file:
        file_content = file.read()
    
    # Parse the file content into an Abstract Syntax Tree (AST)
    tree = ast.parse(file_content)
    
    # Extract all function definitions with line numbers
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Extract function source code using its location in the file
            start_line = node.lineno - 1  # Line numbers are 1-indexed in AST
            end_line = max([child.lineno for child in ast.walk(node) if hasattr(child, 'lineno')])
            function_code = file_content.splitlines()[start_line:end_line]
            functions.append({
                'name': node.name,
                'code': "\n".join(function_code)
            })
    
    return functions


def get_openai_code_suggestion(code):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a dedicated software architect and the most amazing assistant imaginable!"},
        {"role": "user", "content": f"write django unit tests using testcase for the following code \n {code}"}
    ]
    )
    return completion.choices[0].message

def clear_file(filename):
    # Open the file in write mode ('w') to erase its content
    with open(filename, 'w') as file:
        pass  # This just opens and immediately closes the file, erasing its content


def write_to_file(filename, content):
    with open(filename, 'a') as file:
        file.write(content)



if __name__ == "__main__":
    files_to_loop = ["card_generation","ieopenai", "semrush", "topic_extraction"]
    for file in files_to_loop:
        filename = f"/Users/seanmbogo/Desktop/projects/Gentileschi/services/django_api/apps/etl/workers/{file}.py"
        functions = get_function_details(filename)
        save_file_name = f"{file}.py"
        
        print(f"Functions found in {filename}:\n")
        clear_file(save_file_name)
        for func in functions:
            print(f"Function: {func['name']}")
            print(f"Code:\n{func['code']}")
            data = get_openai_code_suggestion(func['code'])
            print("="*40)
            write_to_file(save_file_name, data.content)
