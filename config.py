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
        raise FileNotFoundError('secrets.txt file not found - create it with your API key')