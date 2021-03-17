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
	
	def sell(self, seller, item, i):
		time.sleep(3.4)
		status, message = seller.sell(item)
		message = '{0}: {1}: {2}'.format(i, item.get_data().get('market_hash_name'), message)
		return status, message

	def run(self):
		seller = Seller(self.user, self.session)
		for i, item in enumerate(self.items):
			item_data = item.get_data()

			status, message = self.sell(seller, item, i)
			while message == "We were unable to contact the game's item server. The game's item server may be down or Steam may be experiencing temporary connectivity issues. Your listing has not been created. Refresh the page and try again.":
				status, message = self.sell(seller, item, i)

			time.sleep(0.1)
			self.pb_count += self.step
			self.progress_signal.emit(self.pb_count, status, message)
			
		self.complete_signal.emit()



