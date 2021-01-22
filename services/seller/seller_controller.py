from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread

import sys
import os
import pickle
import requests
import time

from services.seller.seller_view import Ui_form_seller
from services.seller.seller_thread import SellerThread
from services.inventory_parser.inventory_parser_model import InventoryLoaderThread

class SellerController(QtCore.QObject):
	def __init__(self):
		super().__init__()

		self.context_ids = {
			'': 0,
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

		app_id, context_id, steam_id = self.get_selling_info()
		self.load_fresh_inventory(steam_id, app_id)

		self.ui.pb_sell.clicked.connect(self.start_selling)

		self.update_form()
		
	def update_form(self):
		self.form.hide()
		self.form.show()

	def analize_data(self):
		context_id = self.context_ids[self.data.get('app_id')]

	def start_selling(self):
		pass

	def get_selling_info(self):
		app_id = self.data.get('app_id')
		context_id = self.analize_data()
		steam_id = str(self.user.steam_id.as_64)
		self.data['steam_id'] = steam_id
		return app_id, context_id, steam_id


	def load_fresh_inventory(self, steam_id, app_id):
		inventory_loader_thread = InventoryLoaderThread(steam_id, app_id, self.ui.pb_progress)
		inventory_loader_thread.set_no_price_flag(True)
		inventory_loader_thread.complete_signal.connect(self.recv_fresh_inventory)
		inventory_loader_thread.error_signal.connect(self.msgbox_message)

		self.ui.pb_sell.setEnabled(False)
		self.ui.pb_sell.setText('Wait, loading...')

		inventory_loader_thread.start()
		inventory_loader_thread.wait(1)

		self.update_form()

	def recv_fresh_inventory(self, data):
		self.data = data
		self.fill_items_for_selection(data.get('items'))

		self.ui.pb_sell.setEnabled(True)
		self.ui.pb_sell.setText('Sell')

		current_time = self.get_current_time()
		self.ui.pte_process.appendPlainText('[{0}]: Inventory loaded'.format(current_time))
		self.ui.pte_process.moveCursor(QtGui.QTextCursor.End)

		self.update_form()


	def fill_items_for_selection(self, items):
		self.ui.cb_select_item.clear()
		for item in items:
			item_data = item.get_data()
			self.ui.cb_select_item.addItem(item_data.get('market_hash_name'))

	def get_current_time(self):
		t = time.localtime()
		current_time = time.strftime("%H:%M:%S", t)
		return current_time

	def msgbox_message(self, title, message):
		msgBox = QtWidgets.QMessageBox()
		msgBox.setText(title)
		msgBox.setInformativeText(
			message
		)
		msgBox.exec_()



