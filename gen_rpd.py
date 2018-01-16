#!usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import math
import json

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


def get_clear_blocks(raw_blocks, stored_blocks_db='./rpd_db.json'):
    """Приводит полученные входные значения ПСБ raw_blocks к сохранненому эталону из stored_blocks_db"""
    cleared_blocks = {}
    with json.load(open(stored_blocks_db, 'r', encoding='utf-8')) as db:
        for raw_name in raw_blocks.keys():
            for stored_name in db.keys():
                if 1.0 <= NCP(raw_name, stored_name) <= 1.5:
                    new_value = raw_blocks[raw_name]
                    for stored_value in db[stored_name]:
                        if 1.0 <= NCP(new_value, stored_value) <= 1.5:
                            cleared_blocks[stored_name] = stored_value
                        elif NCP(new_value, stored_value) > 10:  # возможно, имеет смысл поменять просто на else
                            db[stored_name].append(new_value)
                            cleared_blocks[stored_name] = new_value
                            json.dump(db, open(stored_blocks_db, 'r', encoding='utf-8'), ensure_ascii=False, indent=4)
    return cleared_blocks


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
    # current_data_blocks = get_clear_blocks(load_blocks())
    current_data_blocks = load_blocks()
    build_rpd_docx(generate_text(current_data_blocks))
