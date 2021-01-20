from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread

import sys
import os
import pickle
import requests
import time

from inventory_helper.inventory_helper_view import Ui_form_inventory_helper
from inventory_helper.inventory_helper_model import LoadInventoryThread
from inventory_helper.inventory_item import InventoryItem


class InventoryHelperController(QtCore.QObject):
	show_seller_view_signal = QtCore.pyqtSignal(list)

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
		self.ui = Ui_form_inventory_helper()
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


		self.update_form()

		sys.exit(self.app.exec_())

	def update_form(self):
		self.form.hide()
		self.form.show()

	def split_data(self):
		steam_id = self.data.get('steam_id')
		app_id = self.data.get('app_id')
		items = self.data.get('items')
		return steam_id, app_id, items

	def load(self):
		self.ui.pb_progress.setValue(0)
		steam_id = str(self.user.steam_id.as_64)
		if self.ui.cb_app_id.currentIndex() == 0:
			app_id = '730'
		get_inventory_thread_instance = LoadInventoryThread(steam_id, app_id, self.ui.pb_progress)
		get_inventory_thread_instance.complete_signal.connect(self.save_and_load_in_table)
		self.ui.pb_load.setEnabled(False)
		self.ui.pb_load.setText('Wait, loading...')
		get_inventory_thread_instance.start()
		get_inventory_thread_instance.wait(1)
		self.update_form()

	def load_cached_data(self):
		if os.path.exists(self.CACHE_FILE_NAME):
			with open(self.CACHE_FILE_NAME, 'rb') as f:
				self.data = pickle.load(f)
			self.load_in_table(self.data)

	
	def save_and_load_in_table(self, data):
		self.data = data 
		with open(self.CACHE_FILE_NAME, 'wb') as f:
			pickle.dump(self.data, f)
		self.load_in_table(self.data)

	def load_in_table(self, data):
		steam_id, app_id, items = self.split_data()

		self.print_table(2, 1)
		inventory_price = self.calc_inventory_price(items)
		self.ui.le_inventory_price.setText('{:.2f}'.format(inventory_price))
		self.ui.le_status.setText('OK')
		self.ui.tw_inventory.resizeColumnsToContents()
		self.ui.pb_load.setEnabled(True)
		self.ui.pb_load.setText('Load')
		self.update_form()

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

		steam_id, app_id, items = self.split_data()
		
		self.ui.tw_inventory.setRowCount(len(items))

		self.ui.le_steam_id.setText(steam_id)
		if app_id == '730':
			self.ui.cb_app_id.setCurrentIndex(0)

		for i, item in enumerate(items):
			self.type_data(i, item)
			
		self.ui.tw_inventory.sortItems(sort, vect)
		self.update_form()

	def type_data(self, row, item):
		new_item = QtWidgets.QTableWidgetItem(item.data.get('name'))
		self.ui.tw_inventory.setItem(row, 0, new_item)

		new_item = QtWidgets.QTableWidgetItem(item.data.get('amount'))
		new_item.setData(QtCore.Qt.EditRole, item.data.get('amount'))
		self.ui.tw_inventory.setItem(row, 1, new_item)

		new_item = QtWidgets.QTableWidgetItem(item.data.get('price'))
		new_item.setData(QtCore.Qt.EditRole, item.data.get('price'))
		self.ui.tw_inventory.setItem(row, 2, new_item)

		new_item = QtWidgets.QTableWidgetItem(item.data.get('total_price'))
		new_item.setData(QtCore.Qt.EditRole, item.data.get('total_price'))
		self.ui.tw_inventory.setItem(row, 3, new_item)

		new_item = QtWidgets.QTableWidgetItem(item.data.get('volume'))
		self.ui.tw_inventory.setItem(row, 4, new_item)

		if item.data.get('tradable') == 1:
			new_item = QtWidgets.QTableWidgetItem('+')
		else:
			new_item = QtWidgets.QTableWidgetItem('-')
		self.ui.tw_inventory.setItem(row, 5, new_item)

		if item.data.get('marketable') == 1:
			new_item = QtWidgets.QTableWidgetItem('+')
		else:
			new_item = QtWidgets.QTableWidgetItem('-')
		self.ui.tw_inventory.setItem(row, 6, new_item)

	def calc_inventory_price(self, items):
		inventory_price = 0
		for item in items:
			inventory_price += item.data.get('total_price')
		return inventory_price

	def launch_selling(self):
		self.show_seller_view_signal.emit(self.data)




