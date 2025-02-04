import re
import sys
import requests

def extract_username_profile(url):
    # Remove fragment (#) if present
    url = url.split('#')[0]
    
    # Match the expected pattern
    match = re.search(r"https://sky\.shiiyu\.moe/stats/([^/]+)(?:/([^/#]+))?", url)
    
    if match:
        username = re.sub(r"[^a-zA-Z0-9_]", "", match.group(1))
        profile = re.sub(r"[^a-zA-Z0-9_]", "", match.group(2)) if match.group(2) else None
        return username, profile
    
    return None, None

def parse_networth(value):
    if isinstance(value, str):
        multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
        try:
            if value[-1] in multipliers:
                return float(value[:-1]) * multipliers[value[-1]]
            return float(value)
        except ValueError:
            return 0
    return float(value)

def format_networth(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return str(value)

def process_file(filename):
    total_networth_value = 0
    try:
        with open(filename, 'r') as file:
            for line in file:
                username, profile = extract_username_profile(line.strip())
                if username:
                    if profile:
                        print(username, profile)
                        response = requests.get(f"https://api.vajeservices.xyz/skyblock/networth/{username}/{profile}")
                    else:
                        response = requests.get(f"https://api.vajeservices.xyz/skyblock/networth/{username}")
                    
                    data = response.json()
                    net = parse_networth(data.get("Networth", "0"))
                    unsoul = parse_networth(data.get("Unsoulbound_Networth", "0"))
                    
                    total_networth_value += net + unsoul
                    total_networth = format_networth(net + unsoul)
                    print(f"Total Networth: {total_networth}")
        
        print(f"Overall Total Networth: {format_networth(total_networth_value)}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
    else:
        process_file(sys.argv[1])