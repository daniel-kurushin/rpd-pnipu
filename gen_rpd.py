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
#from pymystem3 import Mystem

sections_order = ("факультет", 'кафедра', "проректор по учебной работе", 'учебно-методический комплекс дисциплины', 'программа', "направление подготовки", "профиль программы магистратуры", "квалификация выпускника", "выпускающая кафедра", "форма обучения", "курс", "семестр(-ы)", "трудоёмкость", "виды контроля", "авторы", "PAGE_BREAK", "утверждение и согласование", "цель дисциплины", "компетенции", "результаты обучения")


def process_types(element):
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
    return out


def gen(input_file = './rpd.json'):
    output_string = ''
    file_data = json.load(open(input_file, 'r', encoding='utf-8'))
    for section in sections_order:
        if section != 'PAGE_BREAK':
            for key in file_data.keys():
                distance = NCP(section, key)
                if distance >= 1.0 and distance <= 1.5:
                    output_string += key + ':'
                    output_string += process_types(file_data[key])
        else:
            output_string += section + '\n'
    return output_string


def create_docx(rpd_string='', file_name='rpd.docx'):
    rpd_doc = Document()
    rpd_data = rpd_string.split('\n')
    for line in rpd_data:
        if line == 'PAGE_BREAK':
            rpd_doc.add_page_break()
        else:
            rpd_doc.add_paragraph(line)
    rpd_doc.save(file_name)


if __name__ == '__main__':
    create_docx(gen())
