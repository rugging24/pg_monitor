#!/usr/bin/python


def getStatus(V,Wn,Cr,Mn=0,Mx=0) :
	if V < Wn and Wn < Cr  : #and V < Mx and Cr <= Mx and Wn >= Mn :
		return 0
	elif Wn <= V and V < Cr : #and V < Mx and Cr <= Mx and Wn >= Mn :
		return 1
	elif Wn <= Cr and Cr <= V  :
		return 2
	else :
		return 3
