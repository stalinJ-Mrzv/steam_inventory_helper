from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread

from .seller import Seller


class SellerThread(QThread):
	progress_signal = QtCore.pyqtSignal(int, bool, str)
	complete_signal = QtCore.pyqtSignal()

	def __init__(self):
		super().__init__()
	
	def run(self):
		seller = Seller(self.username, self.session)
		amount = 1
		for item in self.items:
			status, message = seller.sell(item.app_id, item.context_id, item.inventory_item.data.get('id'), amount, item.price)
			self.pb_count += self.step
			self.progress_signal.emit(self.pb_count, status, message)
		self.complete_signal.emit()


	def set_user_info(self, username, session):
		self.username = username
		self.session = session

	def set_data(self, items):
		self.items = items
		self.step = 100/len(self.items)
		self.pb_count = 0