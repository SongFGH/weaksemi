# -*- coding: utf-8 -*-
# @Author: twankim
# @Date:   2017-02-24 17:46:51
# @Last Modified by:   twankim
# @Last Modified time: 2017-05-09 15:04:40

import numpy as np
import time
import sys
import os
import argparse
import matplotlib.pyplot as plt

from ssac import weakSSAC
from gen_data import genData
from utils import *

weak = "randaom"
delta = 0.99
std = 1.5
base_dir='./results'

def main(args):
	rep = args.rep
	k = args.k
	n = args.n
	m = args.m
	qs = [float(q) for q in args.qs.split(',')]
	etas = [float(eta) for eta in args.etas.split(',')]
	beta = args.beta
	i_plot = np.random.randint(0,rep) # Index of experiment to plot the figure
	verbose = args.verbose
	
	res_acc = np.zeros((rep,len(qs),len(etas))) # Accuracy of clustering
	res_mean_acc = np.zeros((rep,len(qs),len(etas))) # Mean accuracy of clustering (per cluster)
	res_err = np.zeros((rep,len(qs),len(etas))) # Accuracy of clustering
	res_mean_err = np.zeros((rep,len(qs),len(etas))) # Mean accuracy of clustering (per cluster)
	gammas = np.zeros(rep)

	# Make directories to save results
	if not os.path.exists(base_dir):
		os.makedirs(base_dir)
	res_dir = base_dir + '/{}_{}'.format(args.min_gamma,args.max_gamma)
	if not os.path.exists(res_dir):
		os.makedirs(res_dir)

	for i_rep in xrange(rep):
		# Generate Synthetic data
		# m dimensional, n points, k cluster
		# min_gamma: minimum gamma margin
		if verbose:
		    print "({}/{})... Generating data".format(i_rep+1,rep)
		dataset = genData(n,m,k,args.min_gamma,args.max_gamma,std)
		X,y_true = dataset.gen()
		gamma = dataset.gamma
		gammas[i_rep] = gamma
		print "({}/{})... Synthetic data is generated: gamma={}, (n,m,k,std)=({},{},{},{})".format(
			    i_rep+1,rep,gamma,n,m,k,std)

		algo = weakSSAC(X,y_true,k,q)
		# Test SSAC algorithm for different q's and eta's (fix beta in this case)
		for i_q,q in enumerate(qs):
			# Calculate proper eta and beta based on parameters including delta
			if verbose:
			    print "   - Proper eta={}, beta={} (delta={})".format(
			 	        dataset.calc_eta(q,delta),dataset.calc_beta(q,delta),delta)
	
			for i_eta,eta in enumerate(etas):
				if verbose:
				    print "     <Test: q={}, eta={}, beta={}>".format(q,eta,beta)
				algo.set_params(q,eta,beta)
				algo.fit()
				
				y_pred = algo.y
				mpps = algo.mpps # Estimated cluster centers
				# print "     ... Clustering is done. Number of binary search steps = {}\n".format(algo.bs_num)

				# For evaluation & plotting, find best permutation of cluster assignment
				y_pred_perm = find_permutation(dataset,algo)

				# Calculate accuracy and mean accuracy
				res_acc[i_rep,i_q,i_eta] = accuracy(y_true,y_pred_perm)
				res_mean_acc[i_rep,i_q,i_eta] = mean_accuracy(y_true,y_pred_perm)

				# Calculate number of errors
				res_err[i_rep,i_q,i_eta] = numerror(y_true,y_pred_perm)
				res_mean_err[i_rep,i_q,i_eta] = mean_numerror(y_true,y_pred_perm)
	
				if args.isplot and (i_rep == i_plot) and (m<=2):
					if verbose:
					    print " ... Plotting"
					f = plt.figure(figsize=(14,7))
					plt.suptitle(r"SSAC with {} weak oracle ($q={},\eta={}, \beta={}$)".format(weak,q,eta,beta))
	
					# Plot original clustering (k-means)
					plt.subplot(121)
					plt.scatter(X[:,0],X[:,1],c=y_true)
					plt.title("True dataset ($\gamma$={:.2f})".format(gamma))
	
					# Plot SSAC result
					plt.subplot(122)
					plt.scatter(X[:,0],X[:,1],c=y_pred_perm)
					plt.title("SSAC result ($\gamma$={:.2f})".format(gamma))
	
					# Plot estimated cluster centers
					for t in xrange(k):
						mpp = mpps[t]
						plt.plot(mpp[0],mpp[1],'w^',ms=15)

					f.savefig(res_dir+'/fig_n{}_m{}_k{}_q{}_e{}.pdf'.format(n,m,k,q,eta),bbox_inches='tight')
					plt.close()

	# Write result as table
	# !!!!!!!!!!Need to be implemented

	# Plot Accuracy vs. eta
	fig_name = res_dir+'/fig_{}_n{}_m{}_k{}.pdf'.format("acc",n,m,k)
	plot_eval("Accuracy",res_acc,qs,etas,fig_name)
	# Plot Mean Accuracy vs. eta
	fig_name = res_dir+'/fig_{}_n{}_m{}_k{}.pdf'.format("meanacc",n,m,k)
	plot_eval("Mean Accuracy",res_mean_acc,qs,etas,fig_name)

	# Plot Accuracy vs. eta
	fig_name = res_dir+'/fig_{}_n{}_m{}_k{}.pdf'.format("numerr",n,m,k)
	plot_eval("# Error",res_err,qs,etas,fig_name)
	# Plot Mean Accuracy vs. eta
	# fig_name = res_dir+'/fig_{}_n{}_m{}_k{}.pdf'.format("meannumerr",n,m,k)
	# plot_eval("Mean # Error",np.log10(res_mean_err),qs,etas,fig_name)

	# Plot histogram of gammas
	plot_hist(gammas,args.min_gamma,args.max_gamma)

	plt.show()
	
def parse_args():
    def str2bool(v):
        return v.lower() in ('true', '1')

    parser = argparse.ArgumentParser(description=
                        'Test Semi-Supervised Active Clustering with Weak Oracles: Random-weak model')
    parser.add_argument('-rep', dest='rep',
                        help='Number of experiments to repeat',
                        default = 50, type = int)
    parser.add_argument('-k', dest='k',
                        help='Number of clusters in synthetic data',
                        default = 3, type = int)
    parser.add_argument('-n', dest='n',
                        help='Number of data points in synthetic data',
                        default = 5000, type = int)
    parser.add_argument('-m', dest='m',
                        help='Dimension of data points in synthetic data',
                        default = 2, type = int)
    parser.add_argument('-qs', dest='qs',
                        help='Probabilities q (not-sure with 1-q) ex) 0.7,0.85,1',
                        default = '0.7,0.85,1', type = str)
    parser.add_argument('-etas', dest='etas',
                        help='etas: parameter for sampling (phase 1) ex) 10,50',
                        default = '2,5,10,20,50', type = str)
    parser.add_argument('-beta', dest='beta',
                        help='beta: parameter for sampling (phase 2)',
                        default = 10, type = int)
    parser.add_argument('-g_min', dest='min_gamma',
                        help='minimum gamma margin (default:1)',
                        default = 1.0, type = float)
    parser.add_argument('-g_max', dest='max_gamma',
                        help='minimum gamma margin (default:1)',
                        default = 1.25, type = float)
    parser.add_argument('-isplot', dest='isplot',
                        help='plot the result: True/False',
                        default = True, type = str2bool)
    parser.add_argument('-verbose', dest='verbose',
                        help='verbose: True/False',
                        default = False, type = str2bool)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
	args = parse_args()
	print "Called with args:"
	print args
	sys.exit(main(args))
