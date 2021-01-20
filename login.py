import requests

import steam.webauth as wa

from getpass import getpass

from inventory_helper.inventory_helper import MainController

def main():
	username = input('Username: ')
	password = getpass()

	# Or type username and password here
	# username = 'USERNAME_HERE'
	# password = 'PASSWORD_HERE'


	user = wa.WebAuth(username)
	session = user.cli_login(password)

	if session:
		controller = MainController()
		controller.set_user_data(user, session)
		controller.start()

	else:
		print('something gone wrong')

if __name__ == '__main__':
	main()