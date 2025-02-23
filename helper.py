import os

def save_text_result(file_name, folder_name, content):
    # Create directory structure if it doesn't exist
    os.makedirs(os.path.join('results', folder_name), exist_ok=True)

    # Then open file
    with open(os.path.join('results', folder_name, file_name), "w", encoding="utf-8") as file:
        file.write(content)


def get_api_key(file_name) -> str:
    """
    Reads API key from secrets.txt file
    Returns:
        str: The API key
    Raises:
        FileNotFoundError: If secrets.txt is missing
        ValueError: If API key is not properly formatted
    """
    try:
        with open(file_name, 'r') as f:
            for line in f:
                if line.startswith('API_KEY='):
                    _, key = line.split('=', 1)
                    key = key.strip()
                    if not key:
                        raise ValueError('API_KEY is empty in secrets.txt')
                    return key
            raise ValueError('API_KEY entry not found in secrets.txt')
    except FileNotFoundError:
        raise FileNotFoundError('secrets.txt file not found - Make sure to rename "example.secret.txt" to "secret.txt" and add your API-Key')