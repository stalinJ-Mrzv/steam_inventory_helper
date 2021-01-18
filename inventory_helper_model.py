from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread

import requests
import time
import threading

from inventory_item import InventoryItem

class GetPriceThread(QThread):
	progress_signal = QtCore.pyqtSignal(int)

	def __init__(self, items):
		super().__init__()
		self.items = items
		self.step = 100/len(self.items)
		self.pb_count = 0

	def get_response(self, link_price):
		time.sleep(3.4)
		return requests.get(link_price)

	def get_format_price(self, price):
		return float('{:.2f}'.format(float(price[1:])))

	def run(self):
		BASE_PRICE_LINK = 'https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name='
		m = 0
		for item in self.items:
			time.sleep(0.01)
			r = self.get_response(BASE_PRICE_LINK + item.data.get('market_hash_name'))
			if r.status_code not in [200, 500]:
				item.data['price'] = 0
				self.pb_count += self.step
				self.progress_signal.emit(self.pb_count)
				continue

			json_request = r.json()

			print(str(m) + ' - ' + str(json_request) + ' - ' + item.data.get('market_hash_name'))
			m += 1

			if json_request.get('success'):
				lowest_price = json_request.get('lowest_price')
				median_price = json_request.get('median_price')
				volume = json_request.get('volume')

				if lowest_price:
					item.data['price'] = self.get_format_price(lowest_price)
					item.data['volume'] = volume
				elif median_price:
					item.data['price'] = self.get_format_price(median_price)
					item.data['volume'] = volume
				else:
					item.data['price'] = 0

			self.pb_count += self.step
			self.progress_signal.emit(self.pb_count)


class LoadInventoryThread(QThread):
	complete_signal = QtCore.pyqtSignal(str, str, list)

	def __init__(self, steam_id, app_id, pb_progress, parent = None):
		super().__init__()
		self.steam_id = steam_id
		self.app_id = app_id
		self.pb_progress = pb_progress
		self.parent = parent

		self.items = []

	def run(self):
		self.items = self.get_inventory()
		self.complete_signal.emit(self.steam_id, self.app_id, self.items)

	@QtCore.pyqtSlot(int)
	def inc_progress(self, value):
		self.pb_progress.setValue(value)

	def get_inventory(self):
		# steam_id = '76561198129642590'
		# app_id = '730'
		items = []
		link = 'https://steamcommunity.com/profiles/{0}/inventory/json/{1}/2'.format(self.steam_id, self.app_id)
		# https://steamcommunity.com/profiles/76561198129642590/inventory/json/730/2
		try:
			r = requests.get(link)
			json_request = r.json()
			if (json_request.get('success')):
				inventory_id = json_request.get('rgInventory')
				inventory_descriptions = json_request.get('rgDescriptions')

				item_amount = {}
				for item in inventory_id.values(): 
					class_id = item.get('classid')
					if class_id in item_amount:
						item_amount[class_id] += 1
					else:
						item_amount[class_id] = 1

				for inventory_item in inventory_descriptions.values():
					data = {
						'name': inventory_item.get('name'),
						'market_hash_name': inventory_item.get('market_hash_name'),
						'amount': item_amount.get(inventory_item.get('classid')),
						'classid': inventory_item.get('classid'),
						'instanceid': inventory_item.get('instanceid'),
						'tradable': inventory_item.get('tradable'),
						'marketable': inventory_item.get('marketable'),
						'price': 0,
						'volume': 0,
						'total_price': 0,
					}
					new_item = InventoryItem(data)
					items.append(new_item)
				
				thread1 = GetPriceThread(items)
				thread1.start()
				thread1.progress_signal.connect(self.inc_progress)
				thread1.wait()

				for item in items:
					item.calc_total_price()
			else:
				msgBox = QtWidgets.QMessageBox()
				msgBox.setText('Error!')
				msgBox.setInformativeText(
					'Something gone wrong =('
				)
				msgBox.exec_()

		
		except Exception as e:
			print(e)
			# print(r.json())
		return items










