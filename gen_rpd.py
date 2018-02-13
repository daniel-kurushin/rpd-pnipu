#!usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import math
import json
import os

from docx import Document
from bs4 import BeautifulSoup as BS

from compare import ngramm_compare as NC
from compare import ngramm_compare_phrase as NCP
from compare import MIN_W, MIN_P
# from pymystem3 import Mystem

sections_order = ("факультет", 'кафедра', "проректор по учебной работе", 'учебно-методический комплекс дисциплины',
                  'программа', "направление подготовки", "профиль программы магистратуры", "квалификация выпускника",
                  "выпускающая кафедра", "форма обучения", "курс", "семестр(-ы)", "трудоёмкость", "виды контроля",
                  "авторы", "PAGE_BREAK", "утверждение и согласование", "цель дисциплины", "компетенции",
                  "результаты обучения")


def load_blocks(input_file='./rpd.json'):
    """Загружает выделенные парсером признакосодержащие блоки (ПСБ)"""
    return json.load(open(input_file, 'r', encoding='utf-8'))


def get_clear_types(raw_element, stored_element):
    """Обрабатывает каждый тип сырых данных с попыткой приведения его к сохраненному эталону"""
    # тут пока что принимается на доверие, что типы сырого и сохраненного элемента совпадают, но это только пока
    if isinstance(raw_element, str):
        if 1.0 <= NCP(raw_element, stored_element) <= 1.5:
            return stored_element
        else:  # возможно, имеет смысл поменять просто на else
            return raw_element
    elif isinstance(raw_element, list):
        clear_list = []
        for i in range(0, len(raw_element)):
            if i < len(stored_element):
                clear_list.append(get_clear_types(raw_element[i], stored_element[i]))
            elif len(stored_element) > i:
                clear_list.append(stored_element[i:])
            else:
                clear_list.append(raw_element[i])
        return clear_list
    elif isinstance(raw_element, dict):
        clear_dict = {}
        for key in raw_element.keys():
            for cl_key in stored_element.keys():
                if 1.0 <= NCP(key, cl_key) <= 1.5:
                    clear_dict[cl_key] = get_clear_types(raw_element[key], stored_element[cl_key])
                else:
                    clear_dict[key] = get_clear_types(raw_element[key], stored_element[cl_key])
            else:
                clear_dict[key] = raw_element[key]
    else:
        return raw_element


def get_clear_blocks(input_file='rpd.json'):
    """Приводит полученные входные значения ПСБ raw_blocks к сохранненому эталону из stored_blocks_db"""
    try:
        raw_blocks = load_blocks(input_file)
        clear_blocks = load_blocks('clear_rpds/' + input_file[:-5] + '_clear.json')
        cleared_blocks = {}
        for raw_name in raw_blocks.keys():
            for clear_name in clear_blocks.keys():
                if 1.0 <= NCP(raw_name, clear_name) <= 1.5:
                    cleared_blocks[clear_name] = get_clear_types(raw_blocks[raw_name], clear_blocks[clear_name])
        return cleared_blocks
    except FileNotFoundError:
        print('No stored RPD template found, returning as is')
        return load_blocks(input_file)


def process_types(element):
    """Обрабатывает элементы разных типов для их включения в текст"""
    out = ''
    if isinstance(element, str):
        out = ' ' + element + '\n'
    elif isinstance(element, list):
        out += '\n'
        for child_element in element:
            out += process_types(child_element)
    elif isinstance(element, dict):
        out += '\n'
        for key in element.keys():
            out += key
            out += process_types(element[key])
    else:
        out = ' ' + str(element) + '\n'
    return out


def generate_text(source_blocks):
    """Генерирует текст из очищенных признакосодержащих блоков"""
    output_string = ''
    for section in sections_order:
        if section != 'PAGE_BREAK':
            for key in source_blocks.keys():
                distance = NCP(section, key)
                if 1.0 <= distance <= 1.5:
                    output_string += key + ':'
                    output_string += process_types(source_blocks[key])
        else:
            output_string += section + '\n'
    return output_string


def build_rpd_docx(rpd_string='', file_name='rpd.docx'):
    """Собирает DOCX-файл РПД file_name из строкового представления РПД rpd_string"""
    rpd_doc = Document()
    rpd_data = rpd_string.split('\n')
    for line in rpd_data:
        if line == 'PAGE_BREAK':
            rpd_doc.add_page_break()
        else:
            rpd_doc.add_paragraph(line)
    rpd_doc.save(file_name)


if __name__ == '__main__':
    # current_data_blocks = get_clear_blocks('rpd_0.json')
    # print(current_data_blocks)
    current_data_blocks = load_blocks()
    build_rpd_docx(generate_text(current_data_blocks))
