# Daily counterfactual electricity modeling to estimate consumpton changes

import numpy as np
import os
import pandas as pd
import load_covid_data
from sklearn.preprocessing import OneHotEncoder
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from sklearn.preprocessing import PolynomialFeatures


#Region
region='United-Kingdom'

#alpha for confidence interval
alpha_ci=0.05

# #main directory
# main_dir='C:\\Users\\Documents\\global-changes-in-electricity-consumption-during-covid19'

#number of folds in the k-folds cross validation
num_valid=10

#set random number generator seed (uncomment for reproduceable results)
#np.random.seed(0)


#Get number of days and weeks of data in 2020 by checking length of hdd/cdd and electricity data
# os.chdir(main_dir+'\\Raw\\electricity')
energy_test_df=pd.read_csv('../Data/Raw/electricity/'+region+'_'+'2020'+'_day.csv')
#US regions
if 'Region' in region:
#     os.chdir(main_dir+'\\Raw\\weather')
    hdd_data=pd.read_csv('../Data/Raw/weather/'+'hdd_noaa_'+'2020'+'.csv',header=3)
    num_days_2020=min(energy_test_df.shape[0],hdd_data.shape[1]-1)
#All other regions
else:
#     os.chdir(main_dir+'\\Raw\\weather')
    temp_data=pd.read_csv('../Data/Raw/weather/'+region+'.csv')
    temp_data=temp_data.set_index(pd.DatetimeIndex(temp_data['day']))
    temp_data=temp_data[temp_data.index.year==int('2020')]
    temp_data=temp_data.resample('D').bfill()
    num_days_2020=min(energy_test_df.shape[0],temp_data.shape[0])
num_weeks_2020=np.floor(num_days_2020/7)

#specify training/validation set years
if region in ['Ukraine','Mexico']:
    year_list=['2018','2019','2020']   
elif region in ['Japan','Russia']:
    year_list=['2017','2018','2019','2020']     
else:   
    year_list=['2016','2017','2018','2019','2020']    


#Load test set 
# os.chdir(main_dir+'\\Raw\\electricity')
year='2020'
#load mean daily demand (MW) and mean weekly demand (MW) and convert to daily energy (MWh) and weekly energy (MWh)
energy_test_df=pd.read_csv('../Data/Raw/electricity/'+region+'_'+year+'_day.csv')
energy_test=np.array(energy_test_df.demand[0:int(num_days_2020)])*24
energy_test_week_df=pd.read_csv('../Data/Raw/electricity/'+region+'_'+year+'_week.csv')
energy_test_week=np.array(energy_test_week_df.demand[0:int(num_weeks_2020)])*24*7

hdd_test,cdd_test,_,_=load_covid_data.get_hdd_cdd(year,region,num_days_2020,main_dir)
year_test=np.ones(energy_test.shape)*(len(year_list)-1+1)
month_test,_=load_covid_data.get_month(year,num_days_2020)
month_test=month_test[0:num_days_2020]
holidays_test,_=load_covid_data.get_holidays(year,num_days_2020,region,'day',main_dir)
weekdays_test=load_covid_data.get_weekdays(year)
weekdays_test=weekdays_test[0:num_days_2020]

#Load combined training and validation set
i=0
for year in year_list:
#     os.chdir(main_dir+'\\Raw\\electricity')

    energy_temp_df=pd.read_csv('../Data/Raw/electricity/'+region+'_'+year+'_day.csv')
    energy_temp=np.array(energy_temp_df.demand)*24 #convert from mean daily demand to daily energy
    hdd_temp,cdd_temp,_,_=load_covid_data.get_hdd_cdd(year,region,num_days_2020,main_dir)
    year_temp=np.ones(energy_temp.shape)*(i+1)
    month_temp,_=load_covid_data.get_month(year,num_days_2020)
    holidays_temp,_=load_covid_data.get_holidays(year,num_days_2020,region,'day',main_dir)
    weekdays_temp=load_covid_data.get_weekdays(year)

    #only use first two months of 2020 for training/validation
    if year=='2020':
        energy_temp=energy_temp[0:31+29]
        hdd_temp=hdd_temp[0:31+29]
        cdd_temp=cdd_temp[0:31+29]
        year_temp=year_temp[0:31+29]
        month_temp=month_temp[0:31+29]
        holidays_temp=holidays_temp[0:31+29]
        weekdays_temp=weekdays_temp[0:31+29]

    if i==0:
        energy_total=energy_temp
        hdd_total=hdd_temp
        cdd_total=cdd_temp
        year_total=year_temp
        month_total=month_temp
        holidays_total=holidays_temp
        weekdays_total=weekdays_temp
    else:
        energy_total=np.concatenate((energy_total,energy_temp))
        hdd_total=np.concatenate((hdd_total,hdd_temp))
        cdd_total=np.concatenate((cdd_total,cdd_temp))
        year_total=np.concatenate((year_total,year_temp))
        month_total=np.concatenate((month_total,month_temp))
        holidays_total=np.concatenate((holidays_total,holidays_temp),axis=0)
        weekdays_total=np.concatenate((weekdays_total,weekdays_temp))
    i=i+1
    
#% filter out NANs
cdd_total=cdd_total[np.isnan(energy_total)==False]   
hdd_total=hdd_total[np.isnan(energy_total)==False] 
year_total=year_total[np.isnan(energy_total)==False]   
month_total=month_total[np.isnan(energy_total)==False]   
holidays_total=holidays_total[np.isnan(energy_total)==False,:]  
weekdays_total=weekdays_total[np.isnan(energy_total)==False] 
energy_total=energy_total[np.isnan(energy_total)==False]   

#% Build onehot arrays for dummies, leave out last one
enc_month=OneHotEncoder(sparse=False).fit(month_total.reshape(-1,1))
month_total_OH=enc_month.transform(month_total.reshape(-1,1))[:,:-1]
month_test_OH=enc_month.transform(month_test.reshape(-1,1))[:,:-1]

enc_year=OneHotEncoder(sparse=False).fit(year_total.reshape(-1,1))
year_total_OH=enc_year.transform(year_total.reshape(-1,1))[:,:-1]
year_test_OH=enc_year.transform(year_test.reshape(-1,1))[:,:-1]

enc_weekdays=OneHotEncoder(sparse=False).fit(weekdays_total.reshape(-1,1))
weekdays_total_OH=enc_weekdays.transform(weekdays_total.reshape(-1,1))[:,:-1]
weekdays_test_OH=enc_weekdays.transform(weekdays_test.reshape(-1,1))[:,:-1]
  
#% Do k-fold cross validation
rmse_valid=np.zeros((num_valid,4))
rmse_train=np.zeros((num_valid,4))

#mask for k folds of training/validation set
valid_mask=np.random.choice(np.arange(num_valid),size=(len(energy_total),),replace=True,p=np.ones(num_valid)/num_valid)

#loop through folds
for current_valid in range(num_valid):
    
    cdd_train=cdd_total[valid_mask!=current_valid]
    hdd_train=hdd_total[valid_mask!=current_valid]
    year_train=year_total[valid_mask!=current_valid]
    month_train=month_total[valid_mask!=current_valid]
    holidays_train=holidays_total[valid_mask!=current_valid,:]
    energy_train=energy_total[valid_mask!=current_valid]
    month_train_OH=month_total_OH[valid_mask!=current_valid,:]
    year_train_OH=year_total_OH[valid_mask!=current_valid,:]
    weekdays_train_OH=weekdays_total_OH[valid_mask!=current_valid,:]
    
    cdd_valid=cdd_total[valid_mask==current_valid]
    hdd_valid=hdd_total[valid_mask==current_valid]
    year_valid=year_total[valid_mask==current_valid]
    month_valid=month_total[valid_mask==current_valid]
    holidays_valid=holidays_total[valid_mask==current_valid,:]
    energy_valid=energy_total[valid_mask==current_valid]
    month_valid_OH=month_total_OH[valid_mask==current_valid,:]
    year_valid_OH=year_total_OH[valid_mask==current_valid,:]
    weekdays_valid_OH=weekdays_total_OH[valid_mask==current_valid,:]
    
    y_train_pred=np.zeros((energy_train.shape[0],4))
    y_valid=np.zeros((energy_valid.shape[0],4))
    
    #loop through different orders polynomials of hdd/cdd terms
    for order in range(1,5):
        #training
        hdd_poly_train=PolynomialFeatures(order,include_bias=False).fit_transform(hdd_train.reshape(-1,1))
        cdd_poly_train=PolynomialFeatures(order,include_bias=False).fit_transform(cdd_train.reshape(-1,1))
        
        x_train=np.concatenate((holidays_train,cdd_poly_train,hdd_poly_train,month_train_OH,year_train_OH,weekdays_train_OH),axis=1)
        y_train=energy_train
        x_train=sm.add_constant(x_train)
        x_train=x_train.astype(np.float64)
        lr=sm.OLS(y_train, x_train).fit() 
        y_train_pred[:,order-1]=lr.predict(x_train)
        
        #validation
        hdd_poly_valid=PolynomialFeatures(order,include_bias=False).fit_transform(hdd_valid.reshape(-1,1))
        cdd_poly_valid=PolynomialFeatures(order,include_bias=False).fit_transform(cdd_valid.reshape(-1,1))
        
        x_valid=np.concatenate((holidays_valid,cdd_poly_valid,hdd_poly_valid,month_valid_OH,year_valid_OH,weekdays_valid_OH),axis=1)
        x_valid=sm.add_constant(x_valid)
        y_valid[:,order-1]=lr.predict(x_valid)
        
        #residuals
        resid_train=energy_train-y_train_pred[:,order-1]
        resid_valid=energy_valid-y_valid[:,order-1]
        
        #Calculate errors for training and validation
        train_mean_energy=np.mean(energy_train) 
        rmse_train[current_valid,order-1]=((np.mean(resid_train**2))**0.5)/train_mean_energy
        rmse_valid[current_valid,order-1]=((np.mean(resid_valid**2))**0.5)/train_mean_energy
    

#% select model and save model selection statistics

model_selection=np.argmin(np.mean(rmse_valid,axis=0))

# os.chdir(main_dir+'\\Intermediate')
np.savetxt('../Data/Intermediate/consumption_change_estimates/'+region+'_train_rmse.txt',rmse_train)
np.savetxt('../Data/Intermediate/consumption_change_estimates/'+region+'_valid_rmse.txt',rmse_valid)
np.savetxt('../Data/Intermediate/consumption_change_estimates/'+region+'_modelselect.txt',np.array([model_selection]))

#%final model fit using complete training + validation set and selected model order

#fit final model
hdd_poly_total=PolynomialFeatures(model_selection+1,include_bias=False).fit_transform(hdd_total.reshape(-1,1))
cdd_poly_total=PolynomialFeatures(model_selection+1,include_bias=False).fit_transform(cdd_total.reshape(-1,1))

x_total=np.concatenate((holidays_total,cdd_poly_total,hdd_poly_total,month_total_OH,year_total_OH,weekdays_total_OH),axis=1)
y_total=energy_total
x_total=sm.add_constant(x_total)
x_total=x_total.astype(np.float64)
lr=sm.OLS(y_total, x_total).fit() 

#evaluate on test set
hdd_poly_test=PolynomialFeatures(model_selection+1,include_bias=False).fit_transform(hdd_test.reshape(-1,1))
cdd_poly_test=PolynomialFeatures(model_selection+1,include_bias=False).fit_transform(cdd_test.reshape(-1,1))

x_test=np.concatenate((holidays_test,cdd_poly_test,hdd_poly_test,month_test_OH,year_test_OH,weekdays_test_OH),axis=1)
x_test=sm.add_constant(x_test,has_constant='add')
x_test=x_test.astype(np.float64)
y_test=lr.predict(x_test)

#calculate holiday effects. Select holidays based on p-values of coefficicents
pvals=lr.pvalues
holiday_pvals=pvals[1:holidays_total.shape[1]+1]
coefs=lr.params
holiday_coefs=coefs[1:holidays_total.shape[1]+1]

num_holiday_days=0
sum_holiday_effect=0
total_mean_energy=np.mean(energy_total) 

for i in range(holiday_coefs.shape[0]):
    if holiday_pvals[i]<0.05:
        num_holiday_days_temp=holidays_total[holidays_total[:,i]==1].shape[0]
        if num_holiday_days_temp>0:
            sum_holiday_effect=sum_holiday_effect+num_holiday_days_temp*(holiday_coefs[i]/total_mean_energy)
            num_holiday_days=num_holiday_days+num_holiday_days_temp

avg_holiday_effect=sum_holiday_effect/num_holiday_days
avg_weekday_effect=np.array([np.mean(coefs[-6:-1])/total_mean_energy,coefs[-1]/(2*total_mean_energy)])

# os.chdir(main_dir+'\\Intermediate')
np.savetxt('../Data/Intermediate/consumption_change_estimates/'+region+'_holiday_effect.txt',np.array([avg_holiday_effect]))


#Confidence interval for daily predictions
sdev_test_1m, lower_pred_test, upper_pred_test = wls_prediction_std(lr, exog=x_test, alpha=alpha_ci)

#weekly predictions
y_test_week=np.zeros((int(num_weeks_2020,)))
for i in range(int(num_weeks_2020)):
    y_test_week[i]=np.mean(y_test[i*7:(i+1)*7])*7



#Calculate percent reduction

perc_red=-100*(y_test-energy_test)/y_test
perc_red_upper=-100*(upper_pred_test-energy_test)/upper_pred_test
perc_red_lower=-100*(lower_pred_test-energy_test)/lower_pred_test

perc_red_week=-100*(y_test_week-energy_test_week)/y_test_week


#% output daily results in csv

data_output=np.concatenate((np.arange(1,y_test.shape[0]+1).reshape(-1,1),perc_red.reshape(-1,1),
                            perc_red_lower.reshape(-1,1),perc_red_upper.reshape(-1,1)),axis=1)
labels=['day_2020','percent_red','percent_red_upper','percent_red_lower']
df_output=pd.DataFrame(data_output,columns=labels)
# os.chdir(main_dir+'\\Intermediate')
df_output.to_csv('../Data/Intermediate/consumption_change_estimates/'+region+'_final.csv')

data_output=np.concatenate((np.arange(1,y_test_week.shape[0]+1).reshape(-1,1),perc_red_week.reshape(-1,1)),axis=1)
labels=['week_2020','percent_red']
df_output=pd.DataFrame(data_output,columns=labels)
# os.chdir(main_dir+'\\Intermediate')
df_output.to_csv('../Data/Intermediate/consumption_change_estimates/'+region+'_final_week.csv')