import sys
import os
import requests
from PyQt5.QtWidgets import QVBoxLayout,QMessageBox,QTableWidgetItem
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
import resources
import json

API_KEY = 'HIKG6DRBH95PSUK3' #replace with your own code

def showDialog(msg):
	msgBox = QMessageBox()
	msgBox.setIcon(QMessageBox.Information)
	msgBox.setText(msg)
	msgBox.setWindowTitle("Warning")
	msgBox.setStandardButtons(QMessageBox.Ok)
	returnValue = msgBox.exec()

class MyWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = uic.loadUi("GUI.ui", self)
		onlyInt = QtGui.QIntValidator()
		onlyInt.setRange(0,9999999)
		self.ui.lineEdit_2.setValidator(onlyInt)
		for i in range(8):
			self.ui.tableWidget.resizeColumnToContents(i)
		self.Data = {}
		self.readData()
		# labels = ['Symbol','Current Price','Change','Change Percentage','Quantity','Price of owned','Purchased for','Profit']
		# self.ui.tableWidget.setHorizontalHeaderLabels(labels)

		self.ui.add.clicked.connect(self.addStock)
		self.ui.remove.clicked.connect(self.removeStock)

	def getStockData(self,symbol):
		API = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
		try:
			response = requests.get(API)
		except:
			showDialog('Error: Unable to connect to API')
			return None
		else:
			data = response.json()
			try:
				length = len(data['Global Quote'])
			except:
				showDialog('Error: No Symbol Provided')
				return None
			else:
				if length == 0:
					showDialog("Error: Couldn't find a stock with this symbol.")
					return None
				else:
					return data['Global Quote']

	def addStock(self):
		s = self.ui.lineEdit.text().upper()
		data = self.getStockData(s)
		try:
			quantity = int(self.ui.lineEdit_2.text())
		except:
			showDialog('Error: No Quantity Provided')
			return
		symbol = data['01. symbol']
		if data != None:
			quantity = int(self.ui.lineEdit_2.text())
			try:
				test = self.Data[symbol]
			except:
				self.Data[symbol] = {'quantity': quantity, 'purchased for': quantity * float(data['05. price'])}
				self.ui.tableWidget.insertRow(self.ui.tableWidget.rowCount())
				print(self.ui.tableWidget.rowCount())
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,0,self.createCenteredTableWidgetItem(symbol))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,1,self.createCenteredTableWidgetItem(str(quantity)))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,2,self.createCenteredTableWidgetItem(data['05. price']))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,3,self.createCenteredTableWidgetItem(data['09. change']))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,4,self.createCenteredTableWidgetItem(data['10. change percent']))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,5,self.createCenteredTableWidgetItem(str(quantity*float(data['05. price']))))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,6,self.createCenteredTableWidgetItem(str(quantity*float(data['05. price']))))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,7,self.createCenteredTableWidgetItem(str(0)))
			else:
				self.Data[symbol]['quantity'] += quantity
				self.Data[symbol]['purchased for'] += quantity * float(data['05. price'])
				pos = self.ui.tableWidget.row(self.ui.tableWidget.findItems(symbol,Qt.MatchContains)[0])
				self.ui.tableWidget.setItem(pos,0,self.createCenteredTableWidgetItem(symbol))
				self.ui.tableWidget.setItem(pos,1,self.createCenteredTableWidgetItem(str(self.Data[symbol]['quantity'])))
				self.ui.tableWidget.setItem(pos,2,self.createCenteredTableWidgetItem(data['05. price']))
				self.ui.tableWidget.setItem(pos,3,self.createCenteredTableWidgetItem(data['09. change']))
				self.ui.tableWidget.setItem(pos,4,self.createCenteredTableWidgetItem(data['10. change percent']))
				self.ui.tableWidget.setItem(pos,5,self.createCenteredTableWidgetItem(str(self.Data[symbol]['quantity']*float(data['05. price']))))
				self.ui.tableWidget.setItem(pos,6,self.createCenteredTableWidgetItem(str(self.Data[symbol]['purchased for'])))
				self.ui.tableWidget.setItem(pos,7,self.createCenteredTableWidgetItem(str(self.Data[symbol]['quantity']*float(data['05. price'])-self.Data[symbol]['purchased for'])))

			print(self.Data)
			self.saveData()

	def removeStock(self):
		try:
			s = self.ui.lineEdit.text().upper()
		except:
			showDialog('Error: No Stock Provided')
			return
		try:
			quantity = int(self.ui.lineEdit_2.text())
		except:
			showDialog('Error: No Quantity Provided')
			return
		keys = self.Data.copy()
		for i in keys.keys():
			if s == i:
				new_price = float(self.ui.tableWidget.item(self.ui.tableWidget.row(self.ui.tableWidget.findItems(s,Qt.MatchContains)[0]),2).text())
				new_quantity = self.Data[i]['quantity'] - quantity
				new_purchasedfor = self.Data[i]['purchased for'] - quantity*new_price
				if new_quantity == 0:
					del self.Data[i]
					self.saveData()
					self.readData()
					return
				else:
					self.Data[i]['quantity'] = new_quantity
					self.Data[i]['purchased for'] = new_purchasedfor
					self.saveData()
					self.readData()
					return
		showDialog("Error: Couldn't find an owned stock with this symbol")

	def createCenteredTableWidgetItem(self,text):
		item = QTableWidgetItem(text)
		item.setTextAlignment(Qt.AlignCenter)
		return item

	def saveData(self):
		f = open('user data.txt', 'w')
		f.write(str(self.Data))
		f.close()

	def readData(self):
		try:
			f = open('user data.txt','r')
		except:
			open('user data.txt','x')
			f = open('user data.txt','r')
		data = f.read()
		if data == '':
			self.Data = {}
			f.close()
		else:
			data = eval(data)
			f.close()
			self.Data = data
			symbols = data.keys()
			self.ui.tableWidget.setRowCount(0)
			for i in symbols:
				new_data = self.getStockData(i)
				quantity = data[i]['quantity']
				self.ui.tableWidget.insertRow(self.ui.tableWidget.rowCount())
				print(self.ui.tableWidget.rowCount())
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,0,self.createCenteredTableWidgetItem(i))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,1,self.createCenteredTableWidgetItem(str(quantity)))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,2,self.createCenteredTableWidgetItem(new_data['05. price']))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,3,self.createCenteredTableWidgetItem(new_data['09. change']))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,4,self.createCenteredTableWidgetItem(new_data['10. change percent']))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,5,self.createCenteredTableWidgetItem(str(quantity*float(new_data['05. price']))))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,6,self.createCenteredTableWidgetItem(str(data[i]['purchased for'])))
				self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount()-1,7,self.createCenteredTableWidgetItem(str(quantity*float(new_data['05. price'])-data[i]['purchased for'])))
		