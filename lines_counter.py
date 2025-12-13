import os


def count_lines():
    total = 0
    datas = []
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        length = len(f.readlines())
                        total += length
                        datas.append((path, length))
                except FileNotFoundError:
                    continue
    datas.sort(key=lambda el: el[1], reverse=True)
    print("\n".join(f"{path} : {length}" for path, length in datas))

    print(f"Total lines: {total}")


if __name__ == "__main__":
    count_lines()
