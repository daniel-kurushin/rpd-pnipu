#!usr/bin/python3
# -*- coding: cp1251 -*-

from bs4 import BeautifulSoup as BS
from json import load, dumps, dump
from lingv.util import nolatin, nodigit


class SearchForm:
    """����� ������ - �������� ����� �������"""
    @staticmethod
    def _safe_get_param(dic, key):
        return dic[key] if key in dic.keys() else None

    def __init__(self, get_post_params):
        keys = get_post_params.keys()
        self._user = self._safe_get_param(get_post_params, 'login')
        self._query = self._safe_get_param(get_post_params, 'query')
        self._is_auth = self._safe_get_param(get_post_params, 'is_auth')

        self.template = 'static/rpd_main.html'

        subjectlist = load(open('database/subjects.json', encoding='utf-8'))
        subjectindex = load(open('database/subject-index.json', encoding='utf-8'))
        structure = load(open('database/structure.json', encoding='utf-8'))

        self._join_(subjectlist, subjectindex, structure)

        self.soup = BS(open(self.template).read())

    def _join_(self, _subjectlist = {}, _subjectindex = {}, structure = {}):
        rez = {}
        for faculty in _subjectlist.keys():
            for specialisation in _subjectlist[faculty].keys():
                for subject in _subjectlist[faculty][specialisation].keys():
                    _ = _subjectlist[faculty][specialisation][subject]
                    _.update({"���������":
                        {
                            "������ ������������"      : faculty,
                            "����������� ������������" : structure[faculty]['����������� ������������']
                        }
                    })
                    _.update({"�������������": specialisation})
                    _.update({"������": _subjectindex[subject]})
                    rez.update({
                        subject: _
                    })

        self.data = rez

    def _insert_data(self):
        def relsort(elem):
            try:
                key = elem[1]['rel']
            except KeyError:
                key = nolatin(nodigit(elem[0].strip().lower()))
            return key

        self.soup.find('input', 'search_text')['value'] = self._query
        self.soup.find('input', {'type' : 'hidden'})['value'] = self._user
        # from json import dumps
        # print(dumps(self.data, indent = 4, ensure_ascii = 0))
        # exit(0)
        to_insert = self.soup.find('subjectlist')
        n = 0

        sorted_data = sorted(
            self.data.items(),
            key = relsort,
            reverse = False if self._query else True
        )

        for subject, sbjdic in sorted_data:
            subject_tag = BS('<subject>\
                                <name></name>\
                                <faculty></faculty>\
                                <department></department>\
                                <speciality></speciality>\
                                <hours></hours>\
                                <rrr></rrr>\
                              </subject>').subject
            subject_tag.find('name'      ).insert(0,subject)
            subject_tag.find('faculty'   ).insert(0,sbjdic['���������']['����������� ������������'])
            subject_tag.find('department').insert(0,sbjdic['�������'])
            subject_tag.find('speciality').insert(0,sbjdic['�������������'])
            subject_tag.find('hours'     ).insert(0,sbjdic['������������'])
            try:
                subject_tag.find('rrr'       ).insert(0,str(sbjdic['rel']))
            except KeyError:
                subject_tag.find('rrr'       ).insert(0,"-")

            to_insert.insert(0, subject_tag)

    def _do_query(self, data, q_words):
        dump([data, q_words], open('/tmp/55.json', 'w'), ensure_ascii = 0, indent = 4)
        rez = {}
        for subject in data.keys():
            rel = 1
            s_words = data[subject]['������']
            for q_word in q_words.keys():
                try:
                    rel *= s_words[q_word] * q_words[q_word] * 1000
                except KeyError:
                    rel *= 0.000000001
            rel = 0 if rel == 1 else 0 if rel < 1 else rel * 1000
            if rel > 0:
                try:
                    data[subject].update({"rel":rel})
                    rez.update({subject:data[subject]})
                except Exception as e:
                    print(subject, rel)
        return rez

    def _process_query(self):
        import lingv.index as lingv
        q_words = lingv.index(str(self._query))
        rez = self._do_query(self.data, q_words)
        return rez

    def __str__(self):
        if self._query:
            self.data = self._process_query()
        self._insert_data()
        return self.soup.prettify()


if __name__ == '__main__':
    sf = SearchForm({})
    x = {"�������� ������� � ����������� ������� � ������ ����������� �� ������ ����������� �����": {
        "��������": "���: 8",
        "�������������": "������� � ���������������",
        "������������": "114,00",
        "������": {
            "���������": 0.019230769230769232,
            "�����": 0.019230769230769232,
            "�": 0.0019230769230769232,
            "�����������": 0.019230769230769232,
            "��������": 0.038461538461538464,
            "�������": 0.019230769230769232,
            "������": 0.038461538461538464,
            "��": 0.0019230769230769232,
            "����": 0.038461538461538464,
            "�������": 0.038461538461538464,
            "���������": 0.0019230769230769232,
            "������": 0.038461538461538464,
            "�": 0.0019230769230769232,
            "�����������": 0.038461538461538464,
            "����������": 0.038461538461538464,
            "���������������": 0.019230769230769232,
            "������������": 0.019230769230769232,
            "������": 0.019230769230769232,
            "����": 0.019230769230769232,
            "������": 0.038461538461538464,
            "�����������": 0.038461538461538464
        },
        "���������": {
            "����������� ������������": "���",
            "������ ������������": "������������ ���������"
        },
        "�������": "����"
        }
    }
    y0 = {
        "�������": 0.14285714285714285,
        "���������������": 0.14285714285714285,
        "�": 0.014285714285714285
    }
    y1 = {
        "��������": 0.14285714285714285,
        "�����": 0.14285714285714285,
        "�": 0.014285714285714285
    }
    y2 = {
        "������": 0.14285714285714285,
        "�����": 0.14285714285714285,
        "�": 0.014285714285714285
    }
    # sf._do_query(x, y0)
    # sf._do_query(x, y1)
    # sf._do_query(x, y2)
    print(dumps(sf._do_query(x, y0), indent=4, ensure_ascii = 0))
    print(dumps(sf._do_query(x, y1), indent=4, ensure_ascii = 0))
    print(dumps(sf._do_query(x, y2), indent=4, ensure_ascii = 0))
