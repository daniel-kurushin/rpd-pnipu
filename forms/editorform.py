#!usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as BS
from exceptions import WrongPasswordError, WrongUsernameError

# TODO: в идеале, сюда вынести все операции по работе с базой, пожалуй


class EditorForm():
    """Форма редактора РПД."""
    def __init__(self, id = None, redirect = None, error = None):
        self.id = id
        self.redirect = redirect
        self.error = error

        self.template = 'static/page1.html'

        self.soup = BS(open(self.template, encoding='utf-8').read())

    def __str__(self):
        # self._insert_data()
        # TODO: возможно надо сделать иерархию, этот вызов у всех.
        if not self.error and not self.redirect:
            return self.soup.prettify()
        elif self.error:
            return self._insert_error()
        elif self.redirect:
            return self._insert_redirect()
        else:
            raise Exception("Непонятно!")

    # def _insert_data(self):
    #     inputs = self.soup.find('login')('input')
    #     inputs[0]['value'] = self.login if self.login != None else ""
    #     inputs[1]['value'] = self.password if self.password != None else ""

    def _insert_error(self):
        # inputs = self.soup.find('login')('input')
        # if type(self.error) == WrongPasswordError:
        #     input_to_change_class = inputs[1]
        # elif type(self.error) == WrongUsernameError:
        #     input_to_change_class = inputs[0]
        # else:
        #     input_to_change_class = inputs[0]
        # input_to_change_class['style'] = 'background-color:coral;'
        # input_to_change_class['title'] = str(self.error)
        # p = BS('<p><a href="/lost/">Забыли пароль?</a></p>').p
        # inputs[2].insert_after(p)
        return self.soup.prettify()

    def _insert_redirect(self):
        # input_to_change_class = self.soup.find('login').find('input')
        # input_to_change_class['class'] = 'error'
        # input_to_change_class['title'] = str(self.error)
        return self.soup.prettify()
