import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union


class JSONValidator:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content: str = ""
        self.lines: List[str] = []

    def load_file(self) -> bool:
        """Load file content into memory. Return True if successful."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            self.lines = self.content.splitlines(keepends=True)
            return True
        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found.")
            return False
        except UnicodeDecodeError:
            print(f"Error: File '{self.file_path}' cannot be decoded as UTF-8.")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False

    def validate_and_analyze(self) -> Union[int, List[Dict[str, Any]]]:
        """
        Validate JSON and return analysis.
        Returns:
            - int: number of top-level keys if valid
            - list: list of errors if invalid
        """
        if not self.load_file():
            return [{"error": f"Could not load file '{self.file_path}'", "line": 1, "description": "File access error"}]

        # Try to parse JSON
        try:
            parsed_json = json.loads(self.content)
        except json.JSONDecodeError as e:
            return self._analyze_json_error(e)

        # If valid, return number of top-level keys
        if all((isinstance(parsed_json, dict),
                len(parsed_json.keys()) == 1,
                parsed_json.get('items'))):
            parsed_json = parsed_json.get('items')
        if isinstance(parsed_json, dict):
            if len(parsed_json.keys()) == 1 and parsed_json.get('items'):
                return len(parsed_json.get('items'))
            return len(parsed_json.keys())
        elif isinstance(parsed_json, list):
            return len(parsed_json)
        else:
            # For primitive types (string, number, boolean, null)
            return 1

    def _analyze_json_error(self, error: json.JSONDecodeError) -> List[Dict[str, Any]]:
        """Analyze JSON decode error and return detailed error information."""
        errors = []

        # Basic error from json.JSONDecodeError
        errors.append(
            {"error": str(error), "line": error.lineno, "column": error.colno,
             "description": self._get_error_description(error)}
        )

        # Additional analysis for common issues
        additional_errors = self._additional_analysis(error)
        errors.extend(additional_errors)

        return errors

    def _get_error_description(self, error: json.JSONDecodeError) -> str:
        """Get a more descriptive error message."""
        msg = error.msg.lower()

        if "expecting property name" in msg:
            return "Expected a property name (key) but found something else"
        elif "expecting ',' delimiter" in msg:
            return "Expected a comma to separate items"
        elif "expecting ':' delimiter" in msg:
            return "Expected a colon to separate key and value"
        elif "delimiter" in msg and "after array element" in msg:
            return "Expected a comma or closing bracket after array element"
        elif "delimiter" in msg and "after object member" in msg:
            return "Expected a comma or closing brace after object member"
        elif "invalid control character" in msg:
            return "Invalid control character found"
        elif "invalid escape" in msg:
            return "Invalid escape sequence found"
        elif "trailing data" in msg:
            return "Extra data after the end of the JSON object"
        elif "unterminated string" in msg:
            return "String is not properly closed with a quote"
        elif "unterminated object" in msg:
            return "Object is not properly closed with '}'"
        elif "unterminated array" in msg:
            return "Array is not properly closed with ']'"
        else:
            return error.msg

    def _additional_analysis(self, error: json.JSONDecodeError) -> List[Dict[str, Any]]:
        """Perform additional analysis to find more specific issues."""
        errors = []

        # Check for common issues around the error location
        if error.lineno <= len(self.lines):
            line_content = self.lines[error.lineno - 1]

            # Check for missing closing brackets/braces nearby
            line_before = self.lines[error.lineno - 2] if error.lineno > 1 else ""
            line_after = self.lines[error.lineno] if error.lineno < len(self.lines) else ""

            # Look for unmatched brackets
            all_content_up_to_error = ''.join(self.lines[:error.lineno])
            open_braces = all_content_up_to_error.count('{')
            close_braces = all_content_up_to_error.count('}')
            open_brackets = all_content_up_to_error.count('[')
            close_brackets = all_content_up_to_error.count(']')

            if open_braces > close_braces:
                errors.append(
                    {"error": "Unmatched opening brace '{'", "line": error.lineno, "column": error.colno,
                     "description": f"There are {open_braces - close_braces} more opening braces than closing braces"}
                )
            elif open_braces < close_braces:
                errors.append(
                    {"error": "Unmatched closing brace '}'", "line": error.lineno, "column": error.colno,
                     "description": f"There are {close_braces - open_braces} more closing braces than opening braces"}
                )

            if open_brackets > close_brackets:
                errors.append(
                    {"error": "Unmatched opening bracket '['", "line": error.lineno, "column": error.colno,
                     "description": f"There are {open_brackets - close_brackets} more opening brackets than closing brackets"}
                )
            elif open_brackets < close_brackets:
                errors.append(
                    {"error": "Unmatched closing bracket ']'", "line": error.lineno, "column": error.colno,
                     "description": f"There are {close_brackets - open_brackets} more closing brackets than opening brackets"}
                )

        return errors


def validate_json_file(file_path: str) -> Union[int, List[Dict[str, Any]]]:
    """
    Main function to validate JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        - int: number of top-level keys if valid
        - list: list of error dictionaries if invalid
    """
    validator = JSONValidator(file_path)
    return validator.validate_and_analyze()


def main():
    if len(sys.argv) != 2:
        print("Usage: python app/core/utils/json_validator.py upload_volume/data.json")
        sys.exit(1)

    file_path = sys.argv[1]
    result = validate_json_file(file_path)

    if isinstance(result, int):
        print(f"Valid JSON. Number of top-level elements: {result}")
    else:
        print("Invalid JSON. Found the following errors:")
        for i, error_info in enumerate(result, 1):
            print(f"\nError {i}:")
            print(f"  Line: {error_info.get('line', '?')}")
            if 'column' in error_info:
                print(f"  Column: {error_info['column']}")
            print(f"  Error: {error_info['error']}")
            print(f"  Description: {error_info['description']}")


if __name__ == "__main__":
    main()
