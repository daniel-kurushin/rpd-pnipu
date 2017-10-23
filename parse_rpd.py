import sys
import re

from docx import Document
from json import dumps

class RPD():

	def parse(self):


	def __init__(self, docpath = "", content = {}):
		try:
			open(docpath)
			self.docx = Document(docpath)
			self.docpath = docpath
			self.parse()
		except FileNotFoundError:
			docx = Document()
		self.content = content

def test():
	rpd = RPD('РПД_дисциплины.docx')
	del rpd
	rpd = RPD()


if __name__ == '__main__':
	test()
