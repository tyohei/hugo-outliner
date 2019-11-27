import argparse
import json
import os
import re
import subprocess

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
    content += '+++\n'
    content += toml.dumps(front_matter)
    content += '+++\n'
    content += main_content
    with open(path, 'w') as f:
        f.write(content)
    return front_matter


def check_weights(entries):
    weights = []
    for entry in entries:
        weight = entry.get('Weight', None)
        if weight is not None:
            if not isinstance(weight, int):
                raise ValueError(f'invalid weight: {weight}')
            if weight in weights:
                raise ValueError(f'dumplicate weight found in JSON: {weight}')
        weights.append(weight)

    if not all([w is None for w in weights]) and \
            not all([isinstance(w, int) for w in weights]):
        raise ValueError("""``Weights'' keyword are specified in some of the chapters/sections, but others are not.""")  # NOQA

    return weights


def get_weights(entries):
    weights = []
    for entry in entries:
        weights.append(entry.get('Weight', None))
    return weights


def add_order(entries, weights):

    if all([w is None for w in weights]):
        for i, entry in enumerate(entries):
            entry['Order'] = i + 1
            entry['Weight'] = i + 1
        return entries

    if all([isinstance(w, int) for w in weights]):
        entries.sort(key=lambda e: e['Weight'])
        for i, entry in enumerate(entries):
            entry['Order'] = i + 1
        return entries


def check_outline_is_valid(outline):
    chapters = outline['Chapters']
    chapter_names = [chapter['Name'] for chapter in chapters]
    check_no_duplicates(chapter_names)
    check_weights(chapters)
    for chapter in chapters:
        sections = chapter['Sections']
        section_names = [section['Name'] for section in sections]
        check_no_duplicates(section_names)
        check_weights(sections)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('outline')
    args = parser.parse_args()

    if not os.path.exists('./content'):
        os.makedirs('./content')

    with open(args.outline) as f:
        outline = json.load(f)

    check_outline_is_valid(outline)

    chapters = outline['Chapters']
    chapter_weights = get_weights(chapters)
    chapters = add_order(chapters, chapter_weights)
    for chapter in chapters:
        weight_i = chapter['Weight']
        order_i = chapter['Order']
        cmd = ['hugo',
               'new',
               '--kind',
               'chapter',
               '{}/_index.ja.md'.format(chapter['Name'])]
        out = subprocess.run(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out = out.stderr.decode('utf-8')
        print(out)
        name = cmd[-1]
        print(change_front_matter(name,
                                  chapter['Title'],
                                  f'<b>{order_i}. </b>',
                                  weight_i))

        sections = chapter['Sections']
        section_weights = get_weights(sections)
        sections = add_order(sections, section_weights)
        for section in sections:
            weight_j = section['Weight']
            order_j = section['Order']
            cmd = ['hugo',
                   'new',
                   '{}/{}/_index.ja.md'.format(chapter['Name'], section['Name'])]  # NOQA
            out = subprocess.run(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out = out.stderr.decode('utf-8')
            print(out)
            name = cmd[-1]
            print(change_front_matter(name,
                                      section['Title'],
                                      f'<b>{weight_i}.{weight_j}. </b>',
                                      order_j))


if __name__ == '__main__':
    main()
