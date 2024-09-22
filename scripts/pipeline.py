import pandas as pd
import holidays
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,LabelEncoder
class DataUpdate:
    def __init__(self,data1,data2):
        self.data1=data1
        self.data2=data2
    def date_generator(self):
        weekdays=[1,2,3,4,5]
        weekends=[6,7]
        dic={0:'No Holiday',"0":'No Holiday','a':'Public Holiday','b':'Easter','c':'Christmas'}
        
        self.data2['Date']=pd.to_datetime(self.data2['Date'])
        self.data2['Year']=self.data2['Date'].dt.year
        self.data2['Month']=self.data2['Date'].dt.month
        self.data2['Day']=self.data2['Date'].dt.day
        self.data2['Weekdays']=self.data2['DayOfWeek'].isin(weekdays)
        self.data2['Weekends']=self.data2['DayOfWeek'].isin(weekends)
        us_holidays=holidays.US()
        self.data2['Holidays']=self.data2['Date'].apply(lambda x: us_holidays[x] if x in us_holidays else 'Not Holiday')
        self.data2['StateHoliday']=self.data2['StateHoliday'].map(dic)
        return self.data2
    def missing_handler(self):
        null_columns=['CompetitionDistance','CompetitionOpenSinceMonth','CompetitionOpenSinceYear',
              'Promo2SinceWeek','Promo2SinceYear','PromoInterval']
        for i in null_columns:
            if self.data1[i].dtype=='O':
                self.data1[i].fillna('No Promo',inplace=True)
            else:
                self.data1[i].fillna(0.0,inplace=True)
        return self.data1
    def merge(self,d1,d2):
        merged=d2.merge(d1,on='Store',how='inner')
        return merged
    def encoder(self,data):
        categorical_cols = ['StateHoliday', 'Holidays', 'StoreType', 'Assortment', 'PromoInterval']
        encoder=LabelEncoder()
        for i in categorical_cols:
            data[i]=encoder.fit_transform(data[i])
        return data
    def scaler(self,data):
        scaler=StandardScaler()
        cols=['CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear', 'Promo2SinceYear','Promo2SinceWeek']
        data[cols]=scaler.fit_transform(data[cols])
        return data
    def transform(self):
        data2=self.date_generator()
        data1=self.missing_handler()
        data_new=self.merge(data2,data1)
        data_new=self.encoder(data_new)
        data_new=self.scaler(data_new)
        return data_new
        
        
                
    
        
