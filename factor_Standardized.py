def fun(factorOriginal):
	import numpy as np 
	import copy
	import pdb

	factor = factorOriginal
	factorWidth = factorOriginal.shape[1]
	factorHeight = factorOriginal.shape[0]
	#pdb.set_trace()

	# 1. winsorize
	upperBound = np.nanpercentile(factorOriginal,97.5,axis=1)
	lowerBound = np.nanpercentile(factorOriginal,2.5,axis=1)
	for i in range(0,factorHeight):
		#print(i)
		#pdb.set_trace()
		thisSlice = factorOriginal[i,:]
		thisSlice[thisSlice > upperBound[i]] = upperBound[i]
		thisSlice[thisSlice < lowerBound[i]] = lowerBound[i]
		factor[i,:] = thisSlice

	# standarize
	factorMean = np.nanmean(factorOriginal,axis = 1)
	factorStd  = np.nanstd(factorOriginal,axis = 1)
	for i in range(0,factorHeight):

		thisSlice = factor[i,:]
		thisSlice = (thisSlice - factorMean[i])/factorStd[i]
		factor[i,:] = thisSlice

	return factor
