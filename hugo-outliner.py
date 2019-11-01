import argparse
import json
import os
import re
import subprocess
import shutil

import toml


def check_no_duplicates(names):
    seen = []
    for name in names:
        if name in seen:
            raise ValueError(f'duplicate value found: {name}')
        check_name(name)
        seen.append(name)


def check_name(name):
    pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(pattern, name):
        raise ValueError(f'name invalid: {name}')


def change_front_matter(path, title, pre, order):
    path = os.path.join('content', path)
    if not os.path.exists(path):
        raise OSError(f'file not found: {path}')
    inside = False
    front_matter = ''
    main_content = ''
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            if line == '+++\n' and i == 0:
                inside = True
            elif line == '+++\n':
                inside = False
            elif inside:
                front_matter += line
            else:
                main_content += line
    front_matter = toml.loads(front_matter)
    front_matter['title'] = title
    front_matter['pre'] = pre
    front_matter['weight'] = order
    print(toml.dumps(front_matter))
    content = ''
    content += '+++'
    content += toml.dumps(front_matter)
    content += '+++'
    content += main_content
    with open(path, 'w') as f:
        f.write(content)
    return front_matter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('outline')
    args = parser.parse_args()

    with open(args.outline) as f:
        outline = json.load(f)

    chapters = outline['Chapters']
    chapter_names = [chapter['Name'] for chapter in chapters]
    check_no_duplicates(chapter_names)

    for i, chapter in enumerate(chapters):
        cmd = ['hugo',
               'new',
               '--kind',
               'chapter',
               '{}/_index.ja.md'.format(chapter['Name'])]
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = out.stderr.decode('utf-8')
        print(out)
        name = cmd[-1]
        print(change_front_matter(name, chapter['Title'], f'<b>{i + 1}. </b>', i + 1))

        sections = chapter['Sections']
        section_names = [section['Name'] for section in sections]
        check_no_duplicates(section_names)

        for j, section in enumerate(sections):
            cmd = ['hugo',
                   'new',
                   '{}/{}/_index.ja.md'.format(chapter['Name'], section['Name'])]
            out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = out.stderr.decode('utf-8')
            print(out)
            name = cmd[-1]
            print(change_front_matter(name, section['Title'], f'<b>{i + 1}.{j + 1}. </b>', j + 1))



if __name__ == '__main__':
    main()
