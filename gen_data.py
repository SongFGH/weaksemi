import numpy as np
from sklearn.datasets import make_blobs

class genData:
	def __init__(self,n,m,k,min_gamma=1, std=0.7):
		self.n = n
		self.m = m
		self.k = k
		self.std = std
		self.min_gamma = 1
		self.gamma = 0

	def gen(self):
		while self.gamma <= self.min_gamma:
			X,y = make_blobs(n_samples=self.n,n_features=self.m,centers=self.k,cluster_std = self.std)
			X_means = [X[y==t,:].mean(axis=0) for t in xrange(self.k)]
			gammas = []

			for i in xrange(self.k):
				ri = max(np.linalg.norm(X[y==i,:]-np.tile(X_means[i],(sum(y==i),1)),axis=1))
				ra = min(np.linalg.norm(X[y!=i,:]-np.tile(X_means[i],(sum(y!=i),1)),axis=1))
				gammas.append(ra/float(ri))

			y += 1
			self.gamma = min(gammas)

		return X,y