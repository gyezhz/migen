from migen.fhdl.structure import *

(SP_WITHDRAW, SP_CE) = range(2)

class RoundRobin:
	def __init__(self, n, switch_policy=SP_WITHDRAW):
		self.n = n
		self.bn = bits_for(self.n-1)
		self.request = Signal(BV(self.n))
		self.grant = Signal(BV(self.bn))
		self.switch_policy = switch_policy
		if self.switch_policy == SP_CE:
			self.ce = Signal()
	
	def get_fragment(self):
		if self.n > 1:
			cases = []
			for i in range(self.n):
				switch = []
				for j in reversed(range(i+1,i+self.n)):
					t = j % self.n
					switch = [
						If(self.request[t],
							self.grant.eq(Constant(t, BV(self.bn)))
						).Else(
							*switch
						)
					]
				if self.switch_policy == SP_WITHDRAW:
					case = [If(~self.request[i], *switch)]
				else:
					case = switch
				cases.append([Constant(i, BV(self.bn))] + case)
			statement = Case(self.grant, *cases)
			if self.switch_policy == SP_CE:
				statement = If(self.ce, statement)
			return Fragment(sync=[statement])
		else:
			return Fragment([self.grant.eq(0)])
