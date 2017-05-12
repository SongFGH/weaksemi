# -*- coding: utf-8 -*-
# @Author: twankim
# @Date:   2017-05-05 20:22:13
# @Last Modified by:   twankim
# @Last Modified time: 2017-05-11 23:09:15

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def accuracy(y_true,y_pred):
    return 100*np.sum(y_true==y_pred)/float(len(y_true))

def mean_accuracy(y_true,y_pred):
    labels = np.unique(y_true)
    accuracy = np.zeros(len(labels))
    hamming = y_true==y_pred

    accuracy = [100*np.sum(hamming[y_true==label])/float(np.sum(y_true==label)) \
                for label in labels]
    return np.mean(accuracy)

def error(y_true,y_pred):
    return 100*np.sum(y_true!=y_pred)/float(len(y_true))

def mean_error(y_true,y_pred):
    labels = np.unique(y_true)
    num_error = np.zeros(len(labels))
    hamming = y_true!=y_pred

    error = [100*np.sum(hamming[y_true==label])/float(np.sum(y_true==label)) \
             for label in labels]
    return np.mean(error)

# Find best matching permutation of y_pred clustering
# Also need to change mpp of algorithm
def find_permutation(dataset,algo):
    # Calculate centers of original clustering
    label_org = list(np.unique(dataset.y))
    means_org = [np.mean(dataset.X[dataset.y==label,:],axis=0) for label in label_org]

    labels_map = {} # Map from algorithm's label to true label
    # Initialize label mapping
    for label in xrange(algo.k+1):
        labels_map[label] = 0

    if len(algo.labels)==0:
        return algo.y

    for label,mpp in zip(algo.labels,algo.mpps):
        # Calculate distance between estimated center and true centers
        dist = [np.linalg.norm(mpp-mean_org) for mean_org in means_org]
        
        # Assign true cluster label to the algorithm's label
        idx_best = np.argmin(dist)
        labels_map[label] = label_org[idx_best]
        
        # Remove assigned label from the list
        del means_org[idx_best]
        del label_org[idx_best]

    return [labels_map[y] for y in algo.y]

# Plot eta v.s. evaluation
# res: rep x len(qs) x len(etas)
def print_eval(eval_metric,res,qs,etas,fname,is_sum=False):
    rep = res.shape[0]
    if not is_sum:
        df_res = pd.DataFrame(res.mean(axis=0),
                              columns=etas,
                              index=qs
                              )
        df_res.index.name="q"
        df_res.columns.name='eta'
        print "\n<{} of SSAC (Averaged over {} experiments)>".format(
                eval_metric,rep)
    else:
        df_res = pd.DataFrame(res.sum(axis=0),
                              columns=etas,
                              index=qs
                              )
        df_res.index.name="q"
        df_res.columns.name='eta'
        print "\n<{} of SSAC (Total Sum over {} experiments)>".format(
                eval_metric,rep)
    print df_res
    df_res.to_csv(fname)

# Plot eta v.s. evaluation
# res: rep x len(qs) x len(etas)
def plot_eval(eval_metric,res,qs,etas,fig_name):
    rep = res.shape[0]
    f = plt.figure()
    plt.title(r"{} of SSAC (Averaged over {} experiments)".format(eval_metric,rep))
    for i_q,q in enumerate(qs):
        plt.plot(etas,res.mean(axis=0)[i_q,:],'x-',label=r'$q={}$'.format(q))
    plt.xlabel(r"$\eta$ (Number of samples per cluster)")
    plt.ylabel(eval_metric)
    if "accuracy" in eval_metric.lower():
        plt.legend(loc=4)
    elif "error" in eval_metric.lower():
        plt.legend(loc=1)
    else:
        plt.legend(loc=4)
    plt.xlim([0,np.round(1.2*max(etas))])
    
    f.savefig(fig_name,bbox_inches='tight')

def plot_hist(gammas,min_gamma,max_gamma,fig_name):
    rep = len(gammas)
    f = plt.figure()
    plt.hist(gammas,normed=True,bins=5)
    plt.title(r"Histogram of $\gamma$. min={}, max={} ({} generation)".format(min_gamma,max_gamma,rep))
    plt.xlabel(r"$\gamma")
    plt.ylabel("Probability")

    f.savefig(fig_name,bbox_inches='tight')
