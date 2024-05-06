import os
import sys
import requests
import zipfile
import io
import ast
from typing import List

def is_likely_useful_file(file_path: str, lang: str, keep_readme: bool) -> bool:
    """Determine if the file is likely to be useful by excluding certain directories and specific file types."""
    excluded_dirs = ["examples", "tests", "test", "scripts", "utils", "benchmarks"]
    utility_or_config_files = []
    github_workflow_or_docs = [".github", ".gitignore", "LICENSE"]
    
    if not keep_readme:
        github_workflow_or_docs.append("README")

    if lang == "py":
        excluded_dirs.append("__pycache__")
        utility_or_config_files.extend(["hubconf.py", "setup.py"])
        github_workflow_or_docs.extend(["stale.py", "gen-card-", "write_model_card"])
    elif lang == "go":
        excluded_dirs.append("vendor")
        utility_or_config_files.extend(["go.mod", "go.sum", "Makefile"])

    if any(part.startswith('.') for part in file_path.split('/')):
        return False
    if 'test' in file_path.lower():
        return False
    if any(excluded_dir in file_path for excluded_dir in excluded_dirs):
        return False
    if any(file_name in file_path for file_name in utility_or_config_files):
        return False
    if any(doc_file in file_path for doc_file in github_workflow_or_docs):
        return False
    return True

def is_test_file(file_content: str, lang: str) -> bool:
    """Determine if the file content suggests it is a test file."""
    test_indicators = {
        "py": ["import unittest", "import pytest", "from unittest", "from pytest"],
        "go": ["import testing", "func Test"],
    }
    return any(indicator in file_content for indicator in test_indicators.get(lang, []))

def has_sufficient_content(file_content: str, min_line_count: int = 10) -> bool:
    """Check if the file has a minimum number of substantive lines."""
    lines = [line for line in file_content.split('\n') if line.strip() and not line.strip().startswith(('#', '//'))]
    return len(lines) >= min_line_count

def remove_comments_and_docstrings(source: str, lang: str) -> str:
    """Remove comments and docstrings from the source code."""
    if lang == "py":
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                    node.value.s = ""  # Remove comments
                elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if ast.get_docstring(node):
                        node.body = node.body[1:] if isinstance(node.body[0], ast.Expr) else node.body  # Remove docstrings
            return ast.unparse(tree)
        except SyntaxError:
            return source
    return source

def download_repo_files(repo_url: str, output_file: str, languages: List[str], keep_comments: bool = False, keep_readme: bool = False, branch_or_tag: str = "master") -> None:
    """Download and process files from a GitHub repository for multiple languages."""
    download_url = f"{repo_url}/archive/refs/heads/{branch_or_tag}.zip"
    response = requests.get(download_url)

    if response.status_code != 200:
        print(f"Failed to download the repository. Status code: {response.status_code}")
        sys.exit(1)

    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    with open(output_file, "w", encoding="utf-8") as outfile:
        for file_path in zip_file.namelist():
            if file_path.endswith("/"):
                continue
            file_name = file_path.split('/')[-1]
            file_extension = file_name.split('.')[-1] if '.' in file_name else file_name
            if file_extension not in languages:
                continue
            if not is_likely_useful_file(file_path, file_extension, keep_readme):
                continue

            file_content = zip_file.read(file_path).decode("utf-8")
            if file_extension in ["py", "sh"] and (is_test_file(file_content, file_extension) or not has_sufficient_content(file_content)):
                continue
            if file_extension == "py" and not keep_comments:
                file_content = remove_comments_and_docstrings(file_content, file_extension)

            outfile.write(f"# File: {file_path}\n")
            outfile.write(file_content)
            outfile.write("\n\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Download and process files from a GitHub repository.')
    parser.add_argument('repo_url', type=str, help='The URL of the GitHub repository')
    parser.add_argument('--lang', type=str, nargs='+', choices=['go', 'py', 'md', 'sh', 'Dockerfile'], default=['py'], help='The programming languages of the repository')
    parser.add_argument('--keep-comments', action='store_true', help='Keep comments and docstrings in the source code (only applicable for Python)')
    parser.add_argument('--keep-readme', action='store_true', help='Keep the README.md file')
    parser.add_argument('--branch_or_tag', type=str, help='The branch or tag of the repository to download', default="master")

    args = parser.parse_args()

    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, f"{args.repo_url.split('/')[-1]}_combined.txt")

    download_repo_files(args.repo_url, output_file, args.lang, args.keep_comments, args.keep_readme, args.branch_or_tag)
    print(f"Combined source code for {', '.join(args.lang)} saved to {output_file}")