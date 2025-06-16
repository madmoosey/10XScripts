import ast
from dotenv import load_dotenv
import os
import re
from typing import List, Dict, Any

import openai
from pathlib import Path

# By default load_dotenv() looks for a .env file in cwd or parent dirs
load_dotenv()

openai_key = os.getenv("OPENAI_KEY")

client = openai.OpenAI(api_key=openai_key)


def _get_python_functions(file_content: str) -> List[Dict[str, Any]]:
    tree = ast.parse(file_content)
    functions = []
    lines = file_content.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno - 1
            # find end of this function by tracking nesting
            end = start
            depth = 0
            for i, line in enumerate(lines[start:], start):
                depth += line.count("{") - line.count("}")
                end = i
                if depth <= 0 and i > start:
                    break
            functions.append(
                {"name": node.name, "code": "\n".join(lines[start : end + 1])}
            )
    return functions


def _get_typescript_functions(file_content: str) -> List[Dict[str, Any]]:
    lines = file_content.splitlines()
    return lines


def get_function_details(filename: str) -> List[Dict[str, Any]]:
    """
    Return a list of dicts {"name": str, "code": str} for each top-level
    function in the given file.  Supports .py via ast, and .ts/.tsx via regex.
    """
    path = Path(filename)
    content = path.read_text()

    if path.suffix in (".py",):
        return _get_python_functions(content)
    elif path.suffix in (".ts", ".tsx"):
        return _get_typescript_functions(content)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def get_openai_code_suggestion(code, prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a dedicated software architect and the most amazing assistant imaginable!",
            },
            {"role": "user", "content": f"{prompt} for the following code \n {code}"},
        ],
    )
    return completion.choices[0].message


def clear_file_to_dir(filename: str, target_dir: str) -> None:
    """
    Create (or clear) a file named like `filename` in `target_dir`.
    The original file is untouched; only the new file is written (empty).
    """
    # Ensure the target directory exists
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    # Compute the new file path
    basename = os.path.basename(filename)
    new_path = os.path.join(target_dir, basename)

    # Open in write mode to truncate/create the file
    with open(new_path, "w") as f:
        pass


def write_to_file_to_dir(filename: str, content: str, target_dir: str) -> None:
    """
    Append `content` to a file named like `filename` in `target_dir`.
    Ensures the directory exists and creates the file if necessary.
    """
    # Ensure the target directory exists
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    # Preserve just the basename of the original file
    basename = os.path.basename(filename)
    new_path = os.path.join(target_dir, basename)

    # Open in append mode to add content (creates/truncates if necessary)
    with open(new_path, "a") as f:
        f.write(content)


def list_files(folder_path: str):
    """
    Yield Path objects for each file in the given folder.
    Skips subdirectories.
    """
    p = Path(folder_path)
    for child in p.iterdir():
        if child.is_file():
            yield child


if __name__ == "__main__":
    files_to_loop = list_files(
        "/Users/smbogo/Downloads/brs-dealercontingent20250512/brs-dc-api/src/models"
    )
    for file in files_to_loop:
        lines = get_function_details(file)
        print(file)

        print(f"Functions found in {file}:\n")
        clear_file_to_dir(file, "new")
        data = get_openai_code_suggestion(
            lines, "Modernize the following code to use the latest version of Typegoose"
        )
        print("=" * 40)
        write_to_file_to_dir(file, data.content, "new")
