from __future__ import print_function
import sys
import argparse
import unittest
from xmlrpc.server import SimpleXMLRPCServer

class Node(object):

    def __init__(self, key=None, value=None, prev=None, next=None):
        self.key = key
        self.value = value
        self.prev = prev
        self.next = next

class Forgetful(object):

    """
    Forgetful works like a dict except its storage
    is limited to a a fixed number of elements. If the capacy
    is exceteded, those elements that have not been accessed
    for the longest time, are deleted. The only methods prvided
    are __setitem__, __getitem__, __delitem__, __len__.

    Designed as for caching.

    Example:

    >>> d = Forgetful(1000)
    >>> d['key'] = 'value'
    >>> assert d['key'] == 'value']
    >>> assert len(d) <= d.max_elements
    >>> del d['key']

    Running time is O(1) and about 1microsecond per set/set

    """

    def __init__(self, max_elements=1e3):
        self.max_elements = max_elements
        self.storage = dict()
        self.fifo = Node()
        self.last = self.fifo
        self.counter = 0

    def __len__(self):
        return self.counter

    def update(self, node):
        if not self.counter:
            self.fifo.next = node
            node.prev = self.fifo
            self.last = node
            self.counter += 1
        elif self.last != node:
            if node.prev:
                node.prev.next = node.next
                if node.next:
                    node.next.prev = node.prev
            else:
                self.counter += 1
            self.last.next = node
            node.prev = self.last
            node.next = None
            self.last = node
        while self.counter > self.max_elements:            
            node = self.fifo.next
            self.fifo.next = node.next
            if node.next:
                self.fifo.next.prev = self.fifo
            del self.storage[node.key]
            self.counter -= 1

    def __setitem__(self, key, value):
        node = self.storage.get(key)
        if node:
            node.value = value
        else:
            node = Node(key, value)
            self.storage[key] = node
        self.update(node)

    def get(self, key, default=None, update=True):
        node = self.storage.get(key)
        if not node: 
            return default
        if update:
            self.update(node)
        return node.value

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        node = self.storage.get(key)
        if node:
            del self.storage[key]
            if node.next:
                node.next.prev = node.prev
            node.prev.next = node.next
            self.counter -= 1

    def add(self, key, term, default=0):
        value = self.get(key, default, update=False)
        value = value + term
        self[key] = value
        return value

    forget = __delitem__
    set = __setitem__
    
def benchmark(n):
    import random, time
    fs = Forgetful(n)
    v = [str(random.randint(1000,9999)) for k in range(10*n)]
    t0 = time.time()
    for x in v:
        fs[x] = x
    t = (time.time()-t0) / len(v)
    assert len(fs) > 8000
    assert len(fs) == len(fs.storage)
    return t


def server(domain = '0.0.0.0:8081', size=10000):
    ip, port = domain.split(':')
    s = Forgetful(size)
    with SimpleXMLRPCServer((ip, int(port)), allow_none=True) as server:
        server.register_function(s.get, 'get')
        server.register_function(s.set, 'set')
        server.register_function(s.forget, 'forget')
        server.register_function(s.add, 'add')
        server.register_function(s.__len__, 'length')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)

class TestForgetful(unittest.TestCase):

    def test_insert(self):
        benchmark(n=1000000)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', default='0.0.0.0:8081', help='ip:port where to server')
    parser.add_argument('-s', '--size', type=int, default=10000, help='max number of elements')
    parser.add_argument('-b', '--benchmark', action='store_true', help='run benchmarks')
    parser.add_argument('-t', '--tests', action='store_true', help='run test')
    args = parser.parse_args()
    if args.tests:
        runner = unittest.TextTestRunner()
        itersuite = unittest.TestLoader().loadTestsFromTestCase(TestForgetful)
        runner.run(itersuite)
    if args.benchmark:
        print('time per operation %f seconds' % benchmark(args.size))
    if not args.tests and not args.benchmark:
        server(args.domain, args.size)

if __name__ == '__main__':
    main()
