from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread

import time
import re

from services.seller.seller_view import Ui_form_seller
from services.seller.seller_thread import SellerThread
from services.seller.sell_item import SellItem

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
		return context_id

	def get_selling_info(self):
		app_id = self.data.get('app_id')
		context_id = self.analize_data()
		steam_id = str(self.user.steam_id.as_64)
		self.data['steam_id'] = steam_id
		return app_id, context_id, steam_id

	def start_selling(self):
		status, title, msg, item_index, count, price = self.check_input_data()
		app_id, context_id, steam_id = self.get_selling_info()

		if not status:
			self.msgbox_message(title, msg)
		else:
			sell_items = []
			item_data = self.data.get('items')[item_index].get_data()

			for i in range(count):
				sell_item_data = {
					'app_id': app_id,
					'context_id': context_id,
					'asset_id': item_data.get('ids')[i],
					'market_hash_name': item_data.get('market_hash_name'),
					'price': price,
				}
				sell_item = SellItem(sell_item_data)
				sell_items.append(sell_item)

			self.ui.pb_sell.setEnabled(False)
			self.ui.pb_sell.setText('Wait, selling...')

			seller_thread = SellerThread(self.user, self.session, sell_items)
			seller_thread.progress_signal.connect(self.inc_progress)
			seller_thread.complete_signal.connect(self.end_selling)
			seller_thread.start()
			seller_thread.wait(1)

			self.update_form()

	def check_input_data(self):
		status = False
		title = ''
		msg = ''
		item_index = self.ui.cb_select_item.currentIndex()
		count_str = self.ui.le_count.text()
		count = 0
		price_str = self.ui.le_price.text()

		while not status:
			if item_index < 0:
				title = 'Select item error'
				msg = 'Select correct item'
				break

			try:
				count = int(count_str)
				item_data = self.data.get('items')[item_index].get_data()
				print(len(item_data.get('ids')))
				if count > len(item_data.get('ids')):
					title = 'Count error'
					msg = 'Too many count'
					break

			except ValueError:
				title = 'Count error'
				msg = 'Enter correct count'
				break

			# ^(\d+(?:\.\d{2}$|\d*))$
			if not re.match(r'^(\d+\.\d{2})$', price_str):
				title = 'Price error'
				msg = 'Enter correct price'
				break

			price_str = re.sub(r'\.', '', price_str)
			status = True

		return status, title, msg, item_index, count, price_str

	def inc_progress(self, value, status, message):
		time.sleep(0.05)
		self.ui.pb_progress.setValue(value)
		self.append_process_text('[' + str(status) + ']: ' + message)

	def end_selling(self):
		self.ui.pb_sell.setEnabled(True)
		self.ui.pb_sell.setText('Sell')
		self.update_form()

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

		self.append_process_text('Inventory loaded')

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

	def append_process_text(self, message):
		current_time = self.get_current_time()
		self.ui.pte_process.appendPlainText('[{0}]: {1}'.format(current_time, message))
		self.ui.pte_process.moveCursor(QtGui.QTextCursor.End)

	def msgbox_message(self, title, message):
		msgBox = QtWidgets.QMessageBox()
		msgBox.setText(title)
		msgBox.setInformativeText(
			message
		)
		msgBox.exec_()



