from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread

from services.seller.seller import Seller
from services.seller.sell_item import SellItem


class SellerThread(QThread):
	progress_signal = QtCore.pyqtSignal(int, bool, str)
	complete_signal = QtCore.pyqtSignal()

	def __init__(self, username, session, items):
		super().__init__()
		self.username = username
		self.session = session

		self.items = items

		self.step = 100 / len(self.items)
		self.pb_count = 0
	
	def run(self):
		seller = Seller(self.username, self.session)
		amount = 1
		for item in self.items:
			item_data = item.get_data()
			app_id = item_data.get('app_id')
			context_id = item_data.get('context_id')
			asset_id = item_data.get('asset_id')
			price = item_data.get('price')
			status, message = seller.sell(app_id, context_id, asset_id, amount, price)

			self.pb_count += self.step
			self.progress_signal.emit(self.pb_count, status, message)
			
		self.complete_signal.emit()



