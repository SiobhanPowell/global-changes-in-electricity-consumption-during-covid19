import numpy as np
import os
import pandas as pd
import datetime



def get_hdd_cdd(year,region,num_days_2020,main_dir):
    '''Get HDD and CDD data for specified region'''
    if region in ['Region_CAL','Region_CAR','Region_CENT','Region_FLA','Region_MIDA','Region_MIDW','Region_NE','Region_NY','Region_NW','Region_SE','Region_SW','Region_TEN','Region_TEX','Region_US48']:
        hdd_vec,cdd_vec,week_hdd_vec,week_cdd_vec=get_hdd_cdd_US(year,region,num_days_2020,main_dir)
    else:
        hdd_vec,cdd_vec,week_hdd_vec,week_cdd_vec=get_hdd_cdd_rest(year,region,num_days_2020,main_dir)

    return hdd_vec,cdd_vec,week_hdd_vec,week_cdd_vec
        
def get_hdd_cdd_US(year,region,num_days_2020,main_dir):
    '''Get HDD and CDD data for US region'''
    
    if year in ['2019','2018','2017','2015','2014','2013','2011','2010']:
        num_days=365
        num_weeks=53
    elif year in ['2016','2012']:
        num_days=366
        num_weeks=53
    elif year=='2020':
        
        num_days=num_days_2020
        num_weeks=int(np.floor(num_days_2020/7))


#     os.chdir(main_dir+'\\Raw\\weather')

    if region=='Region_CAL':
        hdd_region='CA'
    elif region=='Region_CAR':
        hdd_region=5
    elif region=='Region_CENT':
        hdd_region=4
    elif region=='Region_FLA':
        hdd_region='FL'
    elif region=='Region_MIDA':
        hdd_region=2
    elif region=='Region_MIDW':
        hdd_region=4
    elif region=='Region_NE':
        hdd_region=1
    elif region=='Region_NY':
        hdd_region='NY'
    elif region=='Region_NW':
        hdd_region=8
    elif region=='Region_SE':
        hdd_region='GA'
    elif region=='Region_SW':
        hdd_region='AZ'#'AZ'
    elif region=='Region_TEN':
        hdd_region='TN'
    elif region=='Region_TEX':
        hdd_region='TX'
    elif region=='Region_US48':
        hdd_region=10
        
    if type(hdd_region)==int:
        hdd_data=pd.read_csv('../Data/Raw/weather/'+'hdd_noaa_'+year+'.csv',header=3)
        hdd_vec=np.array(hdd_data.loc[hdd_region-1])[1:num_days+1]
    
        cdd_data=pd.read_csv('../Data/Raw/weather/'+'cdd_noaa_'+year+'.csv',header=3)
        cdd_vec=np.array(cdd_data.loc[hdd_region-1])[1:num_days+1]
    elif type(hdd_region)==str:
        hdd_data=pd.read_csv('../Data/Raw/weather/'+'hdd_noaa_states_'+year+'.csv',header=3)
        zipped_hdd = zip(hdd_data.Region,np.arange(len(hdd_data.Region)))
        region_dict = dict(zipped_hdd)
        
        hdd_data=hdd_data[hdd_data.Region==hdd_region]
        hdd_vec=np.array(hdd_data.loc[region_dict[hdd_region]])[1:num_days+1]

        cdd_data=pd.read_csv('../Data/Raw/weather/'+'cdd_noaa_states_'+year+'.csv',header=3)       
        cdd_data=cdd_data[cdd_data.Region==hdd_region]
        cdd_vec=np.array(cdd_data.loc[region_dict[hdd_region]])[1:num_days+1]


    week_hdd_vec=np.zeros((num_weeks,))
    week_cdd_vec=np.zeros((num_weeks,))
    
    for i in range(num_weeks):
        week_hdd_vec[i]=np.mean(hdd_vec[i*7:min((i+1)*7,num_days)])
        week_cdd_vec[i]=np.mean(cdd_vec[i*7:min((i+1)*7,num_days)])

    return hdd_vec,cdd_vec,week_hdd_vec,week_cdd_vec

def get_hdd_cdd_rest(year,region,num_days_2020,main_dir):
    '''Get HDD and CDD data for non US regions'''
#     os.chdir(main_dir+'\\Raw\\weather')
    
    
    if year in ['2019','2018','2017','2015','2014','2013','2011','2010']:
        num_days=365
        num_weeks=53
    elif year in ['2016','2012']:
        num_days=366
        num_weeks=53
    elif year=='2020':
        
        num_days=num_days_2020
        num_weeks=int(np.floor(num_days_2020/7))
    
    temp_data=pd.read_csv('../Data/Raw/weather/'+region+'.csv')
    temp_data=temp_data.set_index(pd.DatetimeIndex(temp_data['day']))
    temp_data=temp_data[temp_data.index.year==int(year)]
    temp_data=temp_data.resample('D').bfill()
    
    hdd_vec=np.array(temp_data.hdd_us)
    cdd_vec=np.array(temp_data.cdd_us)
    
    hdd_vec=hdd_vec[0:num_days]
    cdd_vec=cdd_vec[0:num_days]
    
    week_hdd_vec=np.zeros((num_weeks,))
    week_cdd_vec=np.zeros((num_weeks,))
    
    for i in range(num_weeks):
        week_hdd_vec[i]=np.mean(hdd_vec[i*7:min((i+1)*7,num_days)])
        week_cdd_vec[i]=np.mean(cdd_vec[i*7:min((i+1)*7,num_days)])
    
    
    
    return hdd_vec, cdd_vec,week_hdd_vec,week_cdd_vec

def get_weekdays(year):
    '''Get weekdays for specific year'''
    start_date=datetime.datetime(int(year),1,1,0)
    end_date=datetime.datetime(int(year)+1,1,1,0)
    dt=datetime.timedelta(days=1)
    t=start_date
    
    weekday_list=[]
    
    while t<end_date:
        weekday_list.append(t.weekday()) 
        t=t+dt
        
    weekday_vec=np.array(weekday_list)
    
    return weekday_vec

def get_month(year,num_days_2020):
    '''Get month variable for specific year'''
    start_date=datetime.datetime(int(year),1,1,0)
    end_date=datetime.datetime(int(year)+1,1,1,0)
    dt=datetime.timedelta(days=1)
    t=start_date
    
    if year!='2020':
        num_weeks=53
    elif year=='2020':
        num_weeks=int(np.floor(num_days_2020/7))
    
    month_list=[]
    while t<end_date:
        month_list.append(t.month) 
        t=t+dt
        
    month_vec=np.array(month_list)
    week_month=np.zeros((num_weeks,))
    
    for i in range(num_weeks):
        week_month[i]=np.argmax(np.bincount(month_vec[i*7:(i+1)*7]))
    
    return month_vec,week_month
    

def get_holidays(year,num_days_2020,region,model_type,main_dir):
    '''Get holidays for specific region and year'''
    
    if year in ['2019','2018','2017','2015','2014','2013','2011','2010']:
        num_days=365
        num_weeks=53
    elif year in ['2016','2012']:
        num_days=366
        num_weeks=53
    elif year=='2020':
            num_days=num_days_2020
            num_weeks=int(np.floor(num_days/7))

#     os.chdir(main_dir+'\\Raw')
    
    if model_type=='day':
        data=pd.read_csv('../Data/Raw/'+'holidays_daily.csv')
    elif model_type=='week':
        data=pd.read_csv('../Data/Raw/'+'holidays_week.csv')
        
    if region in ['Region_CAL','Region_CAR','Region_CENT','Region_FLA','Region_MIDA',
             'Region_MIDW','Region_NE','Region_NY','Region_NW','Region_SE','Region_SW',
             'Region_TEN','Region_TEX','Region_US48']:
        data=data[data.Country=='us']
    elif region in ['Alberta','Ontario','British_Columbia']:
        data=data[data.Country=='canada']
    elif region=='Czech_Republic':
        data=data[data.Country=='czech']
    elif region=='New_Zealand':
        data=data[data.Country=='new-zealand']
    elif region=='United-Kingdom':
        data=data[data.Country=='uk']
    else:      
        data=data[data.Country==region.lower()]
        
    data=data.set_index(pd.DatetimeIndex(data['Date']))
    data_base=data[data.index.year==2016]
    
    data_temp=data[data.index.year==int(year)]
    holiday_names_base=list(pd.unique(data_base.Holiday))
    
    
    holidays=np.zeros((366,len(holiday_names_base)))
    for i in range(len(holiday_names_base)):
        data_temp_filt=data_temp[data_temp.Holiday==holiday_names_base[i]]
        for j in range(len(data_temp_filt.index)):
            day_of_year=data_temp_filt.index[j].timetuple().tm_yday
            holidays[day_of_year-1,i]=1
    holidays=holidays[0:num_days,:]

    week_holidays=np.zeros((num_weeks,len(holiday_names_base)))
    for i in range(num_weeks):
        week_holidays[i,:]=np.max(holidays[i*7:(i+1)*7,:],axis=0)

    return holidays,week_holidays
    
