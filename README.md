# GitHub Repository to File Converter

This Python script allows you to download and process files from a GitHub repository, making it easier to share code with chatbots that have large context capabilities but don't automatically download code from GitHub.

## Features

- Download and process files from a GitHub repository
- Support for both public and private repositories
- Filter files based on programming languages (Python, Go, Markdown, Bash, Dockerfile)
- Exclude certain directories, file types, and test files
- Remove comments and docstrings from Python source code (optional)
- Keep the README.md file (optional)
- Specify a branch or tag to download from (default: "master")

## Usage

To download and process files from a public GitHub repository, run the following command:

```
python github2file.py https://github.com/username/repository
```

For a private repository, use the following format:

```
python github2file.py https://<USERNAME>:<GITHUB_ACCESS_TOKEN>@github.com/username/repository
```

Replace `<USERNAME>` with your GitHub username and `<GITHUB_ACCESS_TOKEN>` with your GitHub personal access token.

### Optional Arguments

- `--lang`: Specify the programming languages of the repository. Choices: 'go', 'py', 'md', 'sh', 'Dockerfile' (default: ['py']).
- `--keep-comments`: Keep comments and docstrings in the source code (only applicable for Python).
- `--keep-readme`: Keep the README.md file.
- `--branch_or_tag`: Specify the branch or tag of the repository to download (default: "master").

### Example

To download and process files from the Hugging Face Transformers repository, including Python, Markdown, and Bash files, run:

```
python github2file.py https://github.com/huggingface/transformers --lang py md sh
```

This will create a file named `transformers_combined.txt` containing the combined source code from the repository.

To download and process files from a private repository, including the README.md file, run:

```
python github2file.py https://<USERNAME>:<GITHUB_ACCESS_TOKEN>@github.com/username/private-repo --keep-readme
```

## Output

The script will create a file named `repository_combined.txt` (e.g., `transformers_combined.txt`) containing the combined source code from the specified repository. You can then share this file with chatbots like Claude for further analysis or discussion.

## Requirements

- Python 3.x
- `requests` library

## License

This project is open-source and available under the [MIT License](LICENSE).