import logging 
import pandas as pd
import os
import holidays
import matplotlib.pyplot as plt
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')


if not os.path.exists(log_dir):
    os.makedirs(log_dir)


log_file_info = os.path.join(log_dir, 'info.log')
log_file_error = os.path.join(log_dir, 'error.log')


info_handler = logging.FileHandler(log_file_info)
info_handler.setLevel(logging.INFO)

error_handler = logging.FileHandler(log_file_error)
error_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('info.log'),
                        logging.StreamHandler()  
                    ])

logger = logging.getLogger()
logger.setLevel(logging.INFO)  
logger.addHandler(info_handler)
logger.addHandler(error_handler)
class DataAnalyzer:
    def __init__(self,store_df,train_df,test_df):
        self.store_df=store_df
        self.train_df=train_df
        self.test_df=test_df
    def update_data(self,data):
        """
        this method updates the train data with some column that come from store data.
        Parameter:
            data: the data you want to manipulate
        Returns:
            The same data but with more refined and updated columns
        """
        di={0:'No Holiday','0':'No Holiday','a':'Public Holiday','b':'Easter','c':'Christmas'}
        self.train_df['StateHoliday']=self.train_df['StateHoliday'].map(di)
        store_dict = self.store_df.set_index('Store')['StoreType'].to_dict()
        self.train_df['StoreType']=self.train_df['Store'].map(store_dict)
        assort_dict=self.store_df.set_index('Store')['Assortment'].to_dict()
        self.train_df['Assortment']=self.train_df['Store'].map(assort_dict)
        return self.train_df
    def compare_and_plot(self,column):
        """
        This method compared the train data and the test data on a column entered.
        Parameter:
            column: the column you want to use to compare the two datasets
        Returns:
            A bar plot comparing the proportion of the column's unique value with their frequency 
        """
        try:
            tr=self.train_df[column].value_counts()
            te=self.test_df[column].value_counts()
            d=pd.DataFrame({'Test':te,'Train':tr})
            logger.info(f"Loading the bar chart that contains the comparison of two datasets on a column")
            d.plot(kind='bar',stacked=True)
            plt.title(f'Comparing the {column} values for the two datasets')
            plt.xlabel(column)
            plt.ylabel('Frequency')
            plt.tight_layout()
            plt.show()
        except Exception as e:
            logger.error(f"Error loading plot: {e}")
            return None
    def plot_holidays(self,column,year):
        """
        This method returns a plot that shows the distribution of the column provided on a year with the holidays
        marked so we can see what happened before and after the holidays
        Parameter:
            column: A column you want to analyze
            year: the year you want to use for the holidays(for this data only the years 2013,2014 and 2015 are
            available)
        Returns:
            a line plot that shows the column's distribution while marking the days that are holidays
        """
        try:
            d=self.train_df.groupby('Date')[['Sales','Customers']].sum().reset_index()
            d=d[(d['Date']>f'{year}-01-01') & (d['Date']<f'{year}-12-31')]
            d['Date']=pd.to_datetime(d['Date'])
            us_holidays = holidays.US(years=year)
            d['is_holiday'] = d['Date'].isin(us_holidays)

            logger.info(f"Creating a plot for the {column} column while marking the holidays on that year")
            plt.figure(figsize=(12, 6))
            plt.plot(d['Date'], d[column], label=column, color='blue')
            
            holiday_dates = d[d['is_holiday']==True]['Date']
            holiday_sales = d[d['is_holiday']==True][column]
            plt.scatter(holiday_dates, holiday_sales, color='red', label='Holidays', zorder=5)
            plt.xlabel('Date')
            plt.ylabel(f'{column} Value')
            plt.title(f'{column} Value Over Time with Holidays Marked For the Year {year}')
            plt.legend()
            plt.tight_layout()
            plt.show()
        except Exception as e:
            logger.error(f"Error Loading plot: {e}")
            return None
    def plot_stateholidays(self):
            """
            This method effectively compares sales values while categorizing them by state holidays.

            Parameter:
               None
            Returns: 
            A bar chart that compares the sales on each unique stateholidays.
            """
            st=self.train_df.groupby('StateHoliday')[['Sales']].sum()
            logger.info('Showing a bar chart that shows the stateholidays distribution on sales')
            st.plot(kind='bar')
            plt.title(f"The distribution of Sales according to holidays")
            plt.xlabel('StateHoliday')
            plt.ylabel('Frequency')
            plt.show()
    def plot_promo(self,column):
        """
        This method is used to show the difference between sales on days where there is a promotion and no 
        promotion.

        Parameter:
            column: the column you want to analyze the promotion on 
        Returns:
            A line plot that differentiates the promo and non promo values based on the column given
            
        """
        try:
            self.train_df['Date']=pd.to_datetime(self.train_df['Date'])
            store=self.train_df.groupby([self.train_df['Date'].dt.to_period('M'),'Promo'])[column].mean().reset_index()
            promo=store[store['Promo']==1]
            no_promo=store[store['Promo']==0]
            logger.info(f"Compared the effect of promo on {column}")
            plt.figure(figsize=(12, 6))
            promo.plot(x='Date', y=column, ax=plt.gca(), label='Promo', color='blue')
            no_promo.plot(x='Date', y=column, ax=plt.gca(), label='No Promo', color='orange')
            plt.xlabel('Date')
            plt.ylabel(column)
            plt.title(f'{column} Comparison: Promo vs No Promo')
            plt.legend()
            plt.tight_layout()
            plt.show()
        except Exception as e:
            logger.error(f"Error while loading plot: {e}")
    def plot_storetype(self):
        """
        This method groups each storetype and calculates the total sales value

        Parameter:
            None
        Returns:
            a line plot
            
        """
        try:
            ty=self.train_df.groupby('StoreType')['Sales'].sum().reset_index()
            logger.info("Loading the bar chart of sales divided by storetype")
            ty.plot(x='StoreType',y='Sales')
            plt.xlabel('Date')
            plt.ylabel('StoreType')
            plt.title('Store Type Comparison of sales')
            plt.legend()
            plt.show()
        except Exception as e:
            logger.error(f'Error while loading plot {e}')
            return None
    def plot_weekdays(self,column):
        """
        This method finds stores that work on weekends and marks them while plotting a lineplot.

        Parameter:
            column: the column you want to analyze.
        Returns:
            A line plot 
        """
        try:
                weekdays = [1,2,3,4,5,6,7]
                open_weekdays = self.train_df[self.train_df['DayOfWeek'].isin(weekdays)].groupby('Store')['Open'].agg(lambda x: (x == 1).all())
                stores_open_all_weekdays = open_weekdays[open_weekdays].index.tolist()
                st=self.train_df.groupby('Store')[column].sum().reset_index()
                logger.info(f"Plotting the distribution of sales and marking the stores that work on all weekdays")
                plt.plot(st['Store'], st[column], color='lightblue', label=column)

                for store in stores_open_all_weekdays:
                    plt.plot(st.loc[st['Store'] == store, 'Store'],
                            st.loc[st['Store'] == store, column],
                            marker='o', color='red', linestyle='None')
                plt.legend()
                plt.title(f"The distribution of {column} for stores")
                plt.tight_layout()
                plt.show()
        except Exception as e:
            logger.error(f"Error while loading the plot {e}")
            return None
    def plot_assortment(self):
        """
        This method groups the train data by Assortment and compares each unique assortment type by total sales

        Parameter: 
            None
        Returns:
            A line plot
        """
        try:
            ass=self.train_df.groupby('Assortment')['Sales'].sum().reset_index()
            logger.info("The plot of Sales According to the assortment type")
            ass.plot(kind='bar',x='Assortment',y='Sales')
            plt.xlabel('Assortment')
            plt.ylabel('Sales')
            plt.title('The distribution of Sales in regards to the assortment type')
            plt.show()
        except Exception as e:
            logger.error(f"Error while loading the plot {e}")
            return None
    def plot_competition(self,column):
        """
        This method shows the relationship between the competition distance and the column mentioned(usually 
        sales or customers)
        Parameter:
            column: the column you want to correlate with the competition distance
        Returns:
            A scatter plot
        """
        try:
            com=self.train_df.groupby('Store')[column].sum().reset_index()
            dd=self.store_df.set_index('Store')['CompetitionDistance'].to_dict()
            com['CompetitionDistance']=com['Store'].map(dd)
            com=com.sort_values(by='CompetitionDistance')
            logger.info(f"Loading the distribution of Sales according to the competitor")
            com.plot(kind='scatter',x='CompetitionDistance',y=column)
            plt.xlabel('Competitor Distance')
            plt.ylabel(column)
            plt.title(f'The distribution of {column} in regards to competitor distance')
            plt.show()
        except Exception as e:
            logger.error(f"An error occured while loading plot: {e}")