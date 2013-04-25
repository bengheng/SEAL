from email.parser import HeaderParser
from selenium import webdriver
import imaplib
import time
import re

class GmailComposer(webdriver.Firefox):

	def __init__(self):
		webdriver.Firefox.__init__(self)

	def login(self, username, password):
		''' Logs in to Gmail.
		'''
		self.username = username
		self.password = password

		# Go to the google home page
		self.get("https://www.gmail.com")

		while not self.title.startswith("Gmail: Email from Google"):
			time.sleep(1)

		# Gmail log in
		print "Logging in to Gmail..."
		inputElement = self.find_element_by_id("Email")
		inputElement.send_keys(self.username)
		inputElement = self.find_element_by_id("Passwd")
		inputElement.send_keys(self.password)
		inputElement = self.find_element_by_id("signIn")
		inputElement.click()

	def logout(self):
		''' Logs out Gmail.
		'''
		print "Logging out of Gmail..."
		self.click_by_link_text("Sign out")

	def click_by_name(self, name):
		''' Finds a link by name and click it.
		'''
		while True:
			try:
				inputElement = self.find_element_by_name(name)
				if inputElement is not None:
					print "Clicking by name \"%s\"." % name
					inputElement.click()
					break
			except:
				print "Cannot find name \"%s\" to click." % name
				time.sleep(1)

	def click_by_link_text(self, linktext):
		''' Finds a link by text and clicks it.
		'''
		while True:
			try:
				inputElement = self.find_element_by_link_text(linktext)
				if inputElement is not None:
					print "Clicking by link text \"%s\"." % linktext
					inputElement.click()
				break
			except:
				print "Cannot find link \"%s\" to click." % linktext
				time.sleep(1)

	def fill_by_name(self, name, value):
		''' Fills up a field by name.
		'''
		while True:
			try:
				inputElement = self.find_element_by_name(name)
				if inputElement is not None:
					print "Filling by name \"%s\" with \"%s\"." % (name, value)
					inputElement.send_keys(value)
				break
			except:
				print "Cannot find name \"%s\" to fill." % name
				time.sleep(1)

	def send(self, title, to, subject, body):
		''' Composes an email and sends it.
		'''
		while not self.title.startswith(title):
			print "Title is not \"%s\"" % title
			time.sleep(1)

		# Click "Compose email"
		self.click_by_link_text('Compose Mail')

		# Fill in 'to', 'subject' and 'body' fields
		self.fill_by_name('to', to)
		self.fill_by_name('subject', subject)
		self.fill_by_name('body', body)

		# Click "Send"
		print "Waiting for 30 seconds before sending..."
		time.sleep(30)
		self.click_by_name('nvp_bu_send')

	def polls_for_mail(self, \
		subjectpattern = None, \
		bodypattern = None, \
		reflags = 0):
		''' Polls for the latest UNSEEN email that matches the pattern.
		The function returns a tuple (subject, body).
		'''
		print "Polling for getalias response..."

		# Fetch 1 mail
		latest_email_id = None
		subject = ''
		aliasaddr = None
		result = (None, None)
		while True:
			time.sleep(3)
			self.refresh()

			mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
			mail.login(self.username, self.password)
			mail.select('Inbox')

			# Unfortunately, Gmail doesn't like sort...
			# mail.sort( 'REVERSE DATE', 'UTF-8', 'ALL' )
			result, data = mail.search( None, "(UNSEEN)" )
			ids = data[0]
			id_list = ids.split()
			latest_email_id = id_list[-1]

			# Fetch email
			status, data = mail.fetch(latest_email_id, '(BODY.PEEK[HEADER] FLAGS)')
			header_data = data[0][1]
			parser = HeaderParser()
			msg = parser.parsestr(header_data)

			# Tries matching subject
			if subjectpattern != None:
				print "Trying to match subject \"%s\" with pattern \"%s\"..." % \
					(msg['subject'], subjectpattern)
				matchobj = re.match(subjectpattern, msg['subject'], reflags)
				if matchobj:
					print "Found."
					result = (msg['subject'], msg['body'])
					# Now we can mark the mail as SEEN
					data = mail.fetch(latest_email_id, '(BODY[HEADER])')
					mail.close()
					mail.logout()
					break

			# Tries matching body
			if bodypattern != None:
				print "Matching body \"%s\" with pattern \"%s\"..." % \
					(msg['body'], subjectpattern)
				matchobj = re.match(bodypattern, msg['body'], reflags)
				if matchobj:
					print "Found."
					result = (msg['subject'], msg['body'])
					# Now we can mark the mail as SEEN
					data = mail.fetch(latest_email_id, '(BODY[HEADER])')
					mail.close()
					mail.logout()
					break

			mail.close()
			mail.logout()
		return result


