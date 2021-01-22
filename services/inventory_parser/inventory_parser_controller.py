from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread

import sys
import os
import pickle
import requests
import time

from services.inventory_parser.inventory_parser_view import Ui_form_inventory_parser
from services.inventory_parser.inventory_parser_model import InventoryLoaderThread


class InventoryParserController(QtCore.QObject):
	show_seller_view_signal = QtCore.pyqtSignal(dict)

	def __init__(self):
		super().__init__()
		self.CACHE_FILE_NAME = 'cacheload.dat'
		self.HEADERS = ['Name', 'Amount', 'Price', 'Total price', 'Volume', 'Tradable', 'Marketable']
		self.data = {
			'steam_id':'',
			'app_id':'',
			'items':[],
		}

		self.init_ui_form()

	def init_ui_form(self):
		self.app = QtWidgets.QApplication(sys.argv)

		self.form = QtWidgets.QMainWindow()
		self.ui = Ui_form_inventory_parser()
		self.ui.setupUi(self.form)

	def set_user_data(self, user, session):
		self.user = user
		self.session = session

	def start(self):
		self.ui.tw_inventory.setColumnCount(len(self.HEADERS))
		self.ui.tw_inventory.setHorizontalHeaderLabels(self.HEADERS)
		self.load_cached_data()

		self.ui.tw_inventory.resizeColumnsToContents()
		
		self.ui.pb_load.clicked.connect(self.load)
		self.ui.pb_sell.clicked.connect(self.launch_selling)
		
		self.ui.le_steam_id.setText(str(self.user.steam_id.as_64))
		# self.ui.le_steam_id.setText('76561198129642590')

		self.update_form()

		sys.exit(self.app.exec_())

	def update_form(self):
		self.form.hide()
		self.form.show()

	def load(self):
		self.ui.pb_progress.setValue(0)
		steam_id = str(self.user.steam_id.as_64)
		# steam_id = '76561198129642590'
		if self.ui.cb_app_id.currentIndex() == 0:
			app_id = '730'

		inventory_loader_thread = InventoryLoaderThread(steam_id, app_id, self.ui.pb_progress)
		inventory_loader_thread.complete_signal.connect(self.save_and_load_in_table)
		inventory_loader_thread.error_signal.connect(self.msgbox_message)

		self.ui.pb_load.setEnabled(False)
		self.ui.pb_load.setText('Wait, loading...')

		inventory_loader_thread.start()
		inventory_loader_thread.wait(1)

		self.update_form()

	def load_cached_data(self):
		if os.path.exists(self.CACHE_FILE_NAME):
			with open(self.CACHE_FILE_NAME, 'rb') as f:
				self.data = pickle.load(f)
			self.load_in_table()

	
	def save_and_load_in_table(self, data):
		self.data = data 
		with open(self.CACHE_FILE_NAME, 'wb') as f:
			pickle.dump(self.data, f)
		self.load_in_table()

	def load_in_table(self):
		steam_id, app_id, items = self.unpack_data()

		self.print_table(2, 1)
		inventory_price = self.calc_inventory_price(items)
		self.ui.le_inventory_price.setText('{:.2f}'.format(inventory_price))
		self.ui.le_status.setText('OK')
		self.ui.tw_inventory.resizeColumnsToContents()
		self.ui.pb_load.setEnabled(True)
		self.ui.pb_load.setText('Load')
		self.update_form()

	def unpack_data(self):
		steam_id = self.data.get('steam_id')
		app_id = self.data.get('app_id')
		items = self.data.get('items')
		return steam_id, app_id, items

	def print_table(self, sort, vect):
		'''
			sort: 
			0 - by name
			1 - by amount
			2 - by price
			3 - by total price
			4 - by volume
			5 - by tradable
			6 - by marketable

			vect:
			0 - ascending
			1 - descending
		'''

		steam_id, app_id, items = self.unpack_data()
		
		self.ui.tw_inventory.setRowCount(len(items))

		self.ui.le_steam_id.setText(steam_id)
		if app_id == '730':
			self.ui.cb_app_id.setCurrentIndex(0)

		for i, item in enumerate(items):
			self.type_data(i, item)
			
		self.ui.tw_inventory.sortItems(sort, vect)
		self.update_form()

	def type_data(self, row, item):
		item_data = item.get_data()

		new_item = QtWidgets.QTableWidgetItem(item_data.get('market_hash_name'))
		self.ui.tw_inventory.setItem(row, 0, new_item)

		new_item = QtWidgets.QTableWidgetItem(item_data.get('amount'))
		new_item.setData(QtCore.Qt.EditRole, item_data.get('amount'))
		self.ui.tw_inventory.setItem(row, 1, new_item)

		new_item = QtWidgets.QTableWidgetItem(item_data.get('price'))
		new_item.setData(QtCore.Qt.EditRole, item_data.get('price'))
		self.ui.tw_inventory.setItem(row, 2, new_item)

		new_item = QtWidgets.QTableWidgetItem(item_data.get('total_price'))
		new_item.setData(QtCore.Qt.EditRole, item_data.get('total_price'))
		self.ui.tw_inventory.setItem(row, 3, new_item)

		new_item = QtWidgets.QTableWidgetItem(item_data.get('volume'))
		self.ui.tw_inventory.setItem(row, 4, new_item)

		if item_data.get('tradable') == 1:
			new_item = QtWidgets.QTableWidgetItem('+')
		else:
			new_item = QtWidgets.QTableWidgetItem('-')
		self.ui.tw_inventory.setItem(row, 5, new_item)

		if item_data.get('marketable') == 1:
			new_item = QtWidgets.QTableWidgetItem('+')
		else:
			new_item = QtWidgets.QTableWidgetItem('-')
		self.ui.tw_inventory.setItem(row, 6, new_item)

	def calc_inventory_price(self, items):
		inventory_price = 0
		for item in items:
			item_data = item.get_data()
			inventory_price += item_data.get('total_price')
		return inventory_price

	def launch_selling(self):
		self.show_seller_view_signal.emit(self.data)

	def msgbox_message(self, title, message):
		msgBox = QtWidgets.QMessageBox()
		msgBox.setText(title)
		msgBox.setInformativeText(
			message
		)
		msgBox.exec_()



