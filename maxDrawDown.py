#coding:utf-8
def fun(NAV):
    h=NAV[0]
    mdd=0
    for i in range(NAV.shape[0]):
        h=max(h,NAV[i])
        mdd=min(mdd,(NAV[i]-h)/h)
    return mdd




