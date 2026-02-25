class Foo(object):
    def __init__(self, args, something):
        self.data = 42
        self.args = args*2

class Bar(Foo):
    def __init__(self):
        args = 80
        super().__init__(args)
        self.data = 50

b = Bar()
print(b.data)
print(b.args)
