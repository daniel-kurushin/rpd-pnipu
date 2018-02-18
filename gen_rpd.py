#!usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json

from compare import ngramm_compare as NC
from compare import ngramm_compare_phrase as NCP

from docxtpl import DocxTemplate, RichText


def load_blocks(input_file='./rpd.json'):
    """Загружает выделенные парсером признакосодержащие блоки (ПСБ)"""
    return json.load(open(input_file, 'r', encoding='utf-8'))


def get_clear_blocks(input_file='rpd.json'):
    """Приводит полученные входные значения ПСБ raw_blocks к сохранненому эталону из stored_blocks_db"""
    try:
        raw_blocks = load_blocks(input_file)
        clear_blocks = load_blocks('clear_rpds/' + input_file[:-5] + '_clear.json')
        cleared_blocks = {}
        for raw_name in raw_blocks.keys():
            for clear_name in clear_blocks.keys():
                if 1.0 <= NCP(raw_name, clear_name) <= 1.5:
                    if 1.0 <= NCP(str(raw_blocks[raw_name]), str(clear_blocks[clear_name])) <= 1.5:
                        cleared_blocks[clear_name] = clear_blocks[clear_name]
                    else:
                        cleared_blocks[clear_name] = raw_blocks[raw_name]
        return cleared_blocks
    except FileNotFoundError:
        print('No stored RPD template found, returning as is')
        return load_blocks(input_file)


def process_types(element):
    """Обрабатывает элементы разных типов для их включения в текст"""
    if isinstance(element, str):
        out = re.sub(r'[\[\]{}\'\"]', '', str(element))
    elif isinstance(element, list):
        out = []
        for el in element:
            out.append(process_types(el))
    elif isinstance(element, dict):
        preformatted = []
        for child_key in element.keys():
            if isinstance(element[child_key], list):
                preformatted.append({'key': child_key, 'cols': element[child_key]})
            elif isinstance(element[child_key], dict):
                preformatted.append({'key': child_key, 'cols': process_types(element[child_key])})
            else:
                preformatted.append({'key': child_key, 'cols': [process_types(element[child_key])]})
        out = preformatted
    else:
        out = re.sub(r'[\[\]{}\'\"]', '', str(element))
    return out


def generate_context(source_blocks):
    """Генерирует контекст для шаблона из очищенных признакосодержащих блоков"""
    output_context = {}
    for key in source_blocks.keys():
        safe_key = re.sub(r'[-\s]', '_', re.sub(r'[()]', '', str(key)))
        # print(safe_key)
        output_context[safe_key] = process_types(source_blocks[key])
    return output_context


def add_sub_docx(sub_docx):
    document = DocxTemplate(sub_docx)
    xml = re.sub(r'</?w:body[^>]*>', '', document.get_xml())
    return xml


def build_rpd_docx(source_blocks, template='rpd_template.docx', file_name='rpd_new.docx'):
    """Собирает DOCX-файл РПД file_name из контекста input_context и шаблона template"""
    template = DocxTemplate(template)
    contents = add_sub_docx('rpd_contents.docx')
    fos = add_sub_docx('rpd_fos.docx')
    soft = add_sub_docx('rpd_soft.docx')
    iss = add_sub_docx('rpd_soft.docx')
    labs = add_sub_docx('rpd_labs.docx')
    tools = add_sub_docx('rpd_tools.docx')
    context = generate_context(source_blocks)
    # print(context)
    context['contents'] = contents
    context['fos'] = fos
    context['soft'] = soft
    context['iss'] = iss
    context['labs'] = labs
    context['tools'] = tools
    template.render(context)
    name = source_blocks["учебно-методический комплекс дисциплины"]+"_"+source_blocks["направление подготовки"]["шифр"]+".docx"
    template.save('gen/'+re.sub(r'\s', '_', name))
    return re.sub(r'\s', '_', name)


if __name__ == '__main__':
    # current_data_blocks = get_clear_blocks('rpd_0.json')
    # print(current_data_blocks)
    current_data_blocks = load_blocks()
    build_rpd_docx(current_data_blocks)
