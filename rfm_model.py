import datetime as dt
import numpy as np
import pandas as pd



## for Recency
def RClass(x,p,d):
    if x <= d[p][0.2]:
        return 5
    elif x <= d[p][0.4]:
        return 4
    elif x <= d[p][0.6]:
        return 3
    elif x <= d[p][0.8]:
        return 2
    else:
        return 1
## for Frequency and Monetary value
def FMClass(x,p,d):
    if x <= d[p][0.2]:
        return 1
    elif x <= d[p][0.4]:
        return 2
    elif x <= d[p][0.6]:
        return 3
    elif x <= d[p][0.8]:
        return 4
    else:
        return 5



df = pd.read_csv("./files/Retail_Data_Transactions.csv",parse_dates=["trans_date"])
now = dt.datetime(2016,12,24)
df['hist'] = (now - df['trans_date']) / np.timedelta64(1, 'D')
df = df[df["hist"] < (365*2)]

rfmTable = df.groupby("customer_id").agg(
    {
        'hist':'min','customer_id':'count','tran_amount':'sum'
    }
)
rfmTable.rename(columns={
    'hist':'recency',
    'customer_id':'frequency',
    'tran_amount':'monetary'
},inplace = True)
quantiles = rfmTable.quantile(q = [0.2,0.4,0.6,0.8])
quantiles=quantiles.to_dict()


# quantiles R，F，M
rfmSeg = rfmTable
rfmSeg['R_Seg'] = rfmSeg['recency'].apply(RClass, args=('recency',quantiles,))
rfmSeg['F_Seg'] = rfmSeg['frequency'].apply(FMClass, args=('frequency',quantiles,))
rfmSeg['M_Seg'] = rfmSeg['monetary'].apply(FMClass, args=('monetary',quantiles,))
rfmSeg = rfmTable
rfmSeg['R_Seg'] = rfmSeg['recency'].apply(RClass, args=('recency',quantiles,))
rfmSeg['F_Seg'] = rfmSeg['frequency'].apply(FMClass, args=('frequency',quantiles,))
rfmSeg['M_Seg'] = rfmSeg['monetary'].apply(FMClass, args=('monetary',quantiles,))
# combine varieties(R，F，M) into RFM
rfmSeg['RFMScore'] = rfmSeg.R_Seg.map(str) + rfmSeg.F_Seg.map(str) + rfmSeg.M_Seg.map(str)
rfmSeg = rfmSeg.sort_values(by=['RFMScore', 'monetary'], ascending=[False, False])
rfmSeg.reset_index(inplace=True)
# import response data
response = pd.read_csv('./files/Retail_Data_Response.csv')
response = response.sort_index()
rfmSeg.sort_values("customer_id",inplace = True)
rfm_response = pd.merge(rfmSeg,response,on='customer_id')
print(rfm_response.head())

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# Recency vs Response
ax = rfm_response.groupby('R_Seg')['response'].mean().plot(
    kind='bar', colormap='Blues_r'
)
ax.set_xlabel("R_Seg")
ax.set_ylabel("Proportion of Responders")
plt.show()

# Frequency vs Response
ax = rfm_response.groupby('F_Seg')['response'].mean().plot(
    kind='bar', colormap='Blues_r'
)
ax.set_xlabel("F_Seg")
ax.set_ylabel("Proportion of Responders")
plt.show()

# Monetary vs Response
ax = rfm_response.groupby('M_Seg')['response'].mean().plot(
    kind='bar', colormap='Blues_r'
)
ax.set_xlabel("M_Seg")
ax.set_ylabel("Proportion of Responders")
plt.show()
