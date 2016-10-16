import email
import imaplib
import os
import datetime

class FetchEmail():

    connection = None
    error = None

    def __init__(self, mail_server, username, password):
        self.connection = imaplib.IMAP4_SSL(mail_server)
        self.connection.login(username, password)
        self.connection.select(readonly=False) # so we can mark mails as read

    def close_connection(self):
        """
        Close the connection to the IMAP server
        """
        if self.connection.state == 'SELECTED':
            self.connection.close()

    def save_attachment(self, msg, download_folder="/tmp", idx = 'f'):
        """
        Given a message, save its attachments to the specified
        download folder (default is /tmp)

        return: file path to attachment
        """
        files = []
        att_path = "No attachment found."
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = str(idx) + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + part.get_filename()  
            att_path = os.path.join(download_folder, filename)

            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
                files.append(att_path)

        return files

    def fetch_unread_messages(self,markAsSeen):
        """
        Retrieve unread messages
        """
        emails = []
        (result, messages) = self.connection.search(None, 'UnSeen')
        if result == "OK":
            for message in messages[0].split(' '):
                try: 
                    ret, data = self.connection.fetch(message,'(RFC822)')
                except:
                    print "No new emails to read."
                    self.close_connection()
                    return []

                msg = email.message_from_string(data[0][1])
                if isinstance(msg, str) == False:
                    emails.append(msg)
                if markAsSeen:
                    response, data = self.connection.store(message, '+FLAGS','\\Seen')
                else:
                    response, data = self.connection.store(message, '-FLAGS','\\Seen')

            return emails

        self.error = "Failed to retreive emails."
        return emails

    def parse_email_address(self, email_address):
        """
        Helper function to parse out the email address from the message

        return: tuple (name, address). Eg. ('John Doe', 'jdoe@example.com')
        """
        return email.utils.parseaddr(email_address)
