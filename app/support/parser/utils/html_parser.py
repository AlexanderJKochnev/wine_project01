# app/support/parser/utils/html_parser.py
import re
from typing import Dict, Any, Tuple
from bs4 import BeautifulSoup
import json
import html


def parse_html_to_dict(html_content: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Parse HTML content and extract key-value pairs.
    
    Args:
        html_content: Raw HTML string to parse
        
    Returns:
        Tuple of (parsed_dict, field_mapping) where:
        - parsed_dict: Dictionary with extracted key-value pairs
        - field_mapping: Dictionary mapping short names to full names for field keys
    """
    if not html_content:
        return {}, {}
    
    soup = BeautifulSoup(html_content, 'html.parser')
    result = {}
    field_mapping = {}
    
    # Extract the product name from h1 tag
    h1_tag = soup.find('h1')
    if h1_tag:
        product_name = h1_tag.get_text(strip=True)
        result['product_name'] = product_name
        field_mapping['product_name'] = 'Наименование продукта'
    
    # Find all div pairs with the specified classes
    two_sixth_divs = soup.find_all('div', class_='two_sixth first')
    three_fifth_divs = soup.find_all('div', class_='three_fifth')
    
    # Pair them up based on their positions
    min_len = min(len(two_sixth_divs), len(three_fifth_divs))
    
    for i in range(min_len):
        key_elem = two_sixth_divs[i]
        value_elem = three_fifth_divs[i]
        
        key = key_elem.get_text(strip=True)
        value = value_elem.get_text(strip=True)
        
        # Create a short name for the key (first 25 characters, replace spaces with underscores)
        short_name = re.sub(r'[^\w\s-]', '', key[:25]).replace(' ', '_').replace('-', '_').lower()
        short_name = re.sub(r'_+', '_', short_name)  # Replace multiple underscores with single
        
        result[short_name] = value
        field_mapping[short_name] = key
    
    return result, field_mapping


def clean_html_content(html_content: str) -> str:
    """
    Clean HTML content by unescaping HTML entities and normalizing whitespace.
    """
    if not html_content:
        return ""
    
    # Unescape HTML entities
    cleaned = html.unescape(html_content)
    
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned


def convert_to_json(data: Dict[str, Any]) -> str:
    """
    Convert dictionary to JSON string.
    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error converting to JSON: {e}")
        return json.dumps({}, ensure_ascii=False)


def parse_html_to_dict_simple(html_content: str) -> Dict[str, Any]:
    """
    Parse HTML content and extract key-value pairs, returning only the parsed dictionary.
    
    Args:
        html_content: Raw HTML string to parse
        
    Returns:
        Dictionary with extracted key-value pairs
    """
    parsed_dict, _ = parse_html_to_dict(html_content)
    return parsed_dict


def parse_rawdata_html(html_content: str) -> str:
    """
    Main function to parse rawdata HTML and return JSON string.
    """
    parsed_dict, _ = parse_html_to_dict(html_content)
    return convert_to_json(parsed_dict)