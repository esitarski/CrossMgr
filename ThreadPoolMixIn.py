from socketserver import ThreadingMixIn
import threading
from queue import Queue

class ThreadPoolMixIn(ThreadingMixIn):
	"""Mix-in class to handle requests in a thread pool.
	The pool grows and thrinks depending on load.
	For instance, a threading UDP server class is created as follows:
	class ThreadPoolingUDPServer(ThreadPoolingMixIn, UDPServer):
		pass
	"""
	def init_thread_pool(self, min_workers = 5,
						 max_workers = 200, min_spare_workers = 20):
		"""Initialize thread pool."""
		self.q = Queue()
		self.min_workers = min_workers
		self.max_workers = max_workers
		self.min_spare_workers = min_spare_workers
		self.num_workers = 0
		self.num_busy_workers = 0
		self.workers_mutex = threading.Lock()
		self.start_workers(self.min_workers)

	def start_workers(self, n):
		"""Start n workers."""
		for i in range(n):
			t = threading.Thread(target = self.worker)
			t.daemon = True
			t.start()

	def worker(self):
		"""A function of a working thread.
		It gets a request from queue (blocking if there
		are no requests) and processes it.
		After processing it checks how many spare workers
		are there now and if this value is greater than
		self.min_spare_workers then the worker exits.
		Otherwise it loops infinitely.
		"""
		with self.workers_mutex:
			self.num_workers += 1
		while 1:
			(request, client_address) = self.q.get()
			with self.workers_mutex:
				self.num_busy_workers += 1
			self.process_request_thread(request, client_address)
			self.q.task_done()
			with self.workers_mutex:
				self.num_busy_workers -= 1
				if self.num_workers - self.num_busy_workers > \
						self.min_spare_workers:
					self.num_workers -= 1
					return

	def process_request(self, request, client_address):
		"""Puts a request into queue.
		If the queue size is too large, it adds extra worker.
		"""
		self.q.put((request, client_address))
		with self.workers_mutex:
			if self.q.qsize() > 3 and self.num_workers < self.max_workers:
				self.start_workers(1)

	def join(self):
		"""Wait for all busy threads"""
		self.q.join()
		
