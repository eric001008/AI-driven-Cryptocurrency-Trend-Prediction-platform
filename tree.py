import os

EXCLUDE_DIRS = {'.venv', 'node_modules', '__pycache__', '.idea'}

def print_tree(root_path, max_depth=3, output_file='project_structure.txt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(root_path):
            depth = root[len(root_path):].count(os.sep)
            if depth >= max_depth:
                dirs[:] = []
                continue

            indent = '  ' * depth
            dirname = os.path.basename(root) or root_path
            f.write(f"{indent}{dirname}/\n")

            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                f.write(f"{indent}  {file}\n")

print_tree('.', max_depth=4)
