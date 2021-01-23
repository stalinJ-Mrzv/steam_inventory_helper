from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread

import time

from services.seller.seller import Seller


class SellerThread(QThread):
	progress_signal = QtCore.pyqtSignal(int, bool, str)
	complete_signal = QtCore.pyqtSignal()

	def __init__(self, user, session, items):
		super().__init__()
		self.user = user
		self.session = session

		self.items = items

		self.step = 100 / len(self.items)
		self.pb_count = 0
	
	def run(self):
		seller = Seller(self.user, self.session)
		for item in self.items:
			item_data = item.get_data()

			status, message = seller.sell(item)
			message = item_data.get('market_hash_name') + ': ' + message

			self.pb_count += self.step
			self.progress_signal.emit(self.pb_count, status, message)
			time.sleep(3.4)
			
		self.complete_signal.emit()



