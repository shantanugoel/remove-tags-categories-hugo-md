import os
import re
import sys
from pathlib import Path
import yaml
import toml

def extract_frontmatter(content):
    """Extract front matter from content."""
    # YAML front matter pattern (between --- or +++)
    yaml_pattern = re.compile(r'^(---|\+\+\+)\r?\n(.*?)\r?\n\1', re.DOTALL | re.MULTILINE)
    # TOML front matter pattern (between +++)
    toml_pattern = re.compile(r'^\+\+\+\r?\n(.*?)\r?\n\+\+\+', re.DOTALL | re.MULTILINE)
    
    yaml_match = yaml_pattern.match(content)
    toml_match = toml_pattern.match(content)
    
    if yaml_match:
        front_matter = yaml_match.group(2)
        delimiter = yaml_match.group(1)
        rest_content = content[yaml_match.end():]
        return front_matter, rest_content, delimiter, 'yaml'
    elif toml_match:
        front_matter = toml_match.group(1)
        rest_content = content[toml_match.end():]
        return front_matter, rest_content, '+++', 'toml'
    return None, content, None, None

def clean_frontmatter(directory):
    """Process all files in directory recursively."""
    modified_count = 0
    
    for path in Path(directory).rglob('*'):
        if path.is_file() and path.suffix in ['.md', '.html', '.markdown']:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                front_matter, rest_content, delimiter, fm_type = extract_frontmatter(content)
                
                if front_matter is None:
                    continue
                
                # Parse and modify front matter
                try:
                    if fm_type == 'yaml':
                        data = yaml.safe_load(front_matter)
                    else:  # toml
                        data = toml.loads(front_matter)
                    
                    if not isinstance(data, dict):
                        continue
                    
                    # Check if tags or categories exist before modifying
                    modified = False
                    if 'tags' in data:
                        del data['tags']
                        modified = True
                    if 'categories' in data:
                        del data['categories']
                        modified = True
                    
                    if not modified:
                        continue
                    
                    # Convert back to string
                    if fm_type == 'yaml':
                        new_front_matter = yaml.dump(data, allow_unicode=True, sort_keys=False)
                    else:  # toml
                        new_front_matter = toml.dumps(data)
                    
                    # Reconstruct the file content
                    new_content = f"{delimiter}\n{new_front_matter.strip()}\n{delimiter}{rest_content}"
                    
                    # Write back to file
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    
                    modified_count += 1
                    print(f"Modified: {path}")
                    
                except (yaml.YAMLError, toml.TomlDecodeError) as e:
                    print(f"Error parsing front matter in {path}: {e}")
                    
            except Exception as e:
                print(f"Error processing {path}: {e}")
    
    return modified_count

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Processing files in {directory}...")
    modified_count = clean_frontmatter(directory)
    print(f"\nCompleted! Modified {modified_count} files.")

if __name__ == "__main__":
    main()
