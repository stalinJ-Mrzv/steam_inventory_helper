from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread

import sys
import os
import pickle
import requests
import time

from inventory_helper.seller.seller_view import Ui_form_seller
from inventory_helper.seller.sell_item import SellItem


class SellerController(QtCore.QObject):
	def __init__(self):
		super().__init__()

		self.context_ids = {
			'730': 2,
		}

		self.init_ui_form()

	def init_ui_form(self):
		self.form = QtWidgets.QMainWindow()
		self.ui = Ui_form_seller()
		self.ui.setupUi(self.form)

	def set_user_data(self, user, session):
		self.user = user
		self.session = session

	def start(self, data):
		self.data = data
		context_id = self.analize_data()
		self.update_form()
		
	def update_form(self):
		self.form.hide()
		self.form.show()

	def analize_data(self):
		context_id = self.context_ids[self.data.get('app_id')]




