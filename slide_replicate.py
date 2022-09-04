import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Importing data from CSV files
booking_df = pd.read_csv('bookings_filename.csv')
spend_src_df = pd.read_csv('spend_filename.csv')
pd.set_option('display.max_columns', None)

# checking data
# print(spend_df.head())
# print(spend_df.dtypes)
# print(booking_df.dtypes)

# dropping two columns from raw data
spend_df = spend_src_df.iloc[:, :-2]

# print(spend_df.head())
# print(spend_df.dtypes)

# adding LOS Bucket Column to dfs
spend_los_conditions = [
    (spend_df['LOS'] < 7),
    (spend_df['LOS'] >= 7)
    ]
spend_los_values = [spend_df['LOS'].astype(str), "7+"]
spend_df['LOS_Bucket'] = np.select(spend_los_conditions, spend_los_values)


bookings_los_conditions = [
    (booking_df['LOS'] < 7),
    (booking_df['LOS'] >= 7)
]
bookings_los_values = [booking_df['LOS'].astype(str), "7+"]
booking_df['LOS_Bucket'] = np.select(bookings_los_conditions, bookings_los_values)

# Adding DTA Bucket Column to dfs
spend_dta_conditions = [
    (spend_df['DTA'] <= 7),
    (spend_df['DTA'] > 7)
]
spend_dta_values = [spend_df['DTA'].astype(str), "Over 7"]
spend_df['DTA_Bucket'] = np.select(spend_dta_conditions, spend_dta_values)

bookings_dta_conditions = [
    (booking_df['DTA'] <= 7),
    (booking_df['DTA'] > 7)
]
bookings_dta_values = [booking_df['DTA'].astype(str), "Over 7"]
booking_df['DTA_Bucket'] = np.select(bookings_dta_conditions, bookings_dta_values)

booking_df['LOS_Bucket'] = booking_df['LOS_Bucket'].astype('category')
booking_df['DTA_Bucket'] = booking_df['DTA_Bucket'].astype('category')

# Creating Tables LOS Slide
# Impressions
slideLOS_tableImp = pd.pivot_table(spend_df, index=['LOS_Bucket'], values=['IMPRESSIONS'], aggfunc=np.sum)
slideLOS_tableImp['% of Total'] = (slideLOS_tableImp['IMPRESSIONS'] / slideLOS_tableImp['IMPRESSIONS'].sum()) * 100
slideLOS_tableImp['IMPRESSIONS'] = slideLOS_tableImp['IMPRESSIONS'].astype(int)
slideLOS_tableImp['% of Total'] = slideLOS_tableImp['% of Total'].round(decimals=2)
# print(slideLOS_tableImp)

# # Clicks
slideLOS_tableClick = pd.pivot_table(spend_df, index=['LOS_Bucket'], values=['CLICKS'], aggfunc=np.sum)
slideLOS_tableClick['% of Total'] = (slideLOS_tableClick['CLICKS'] / slideLOS_tableClick['CLICKS'].sum()) * 100
slideLOS_tableClick['CLICKS'] = slideLOS_tableClick['CLICKS'].astype(int)
slideLOS_tableClick['% of Total'] = slideLOS_tableClick['% of Total'].round(decimals=2)
# print(slideLOS_tableClick)

# Bookings
slideLOS_tableBookings = pd.pivot_table(booking_df, index=['LOS_Bucket'], values=['BOOKINGS'], aggfunc=np.sum)
slideLOS_tableBookings['% of Total'] = (slideLOS_tableBookings['BOOKINGS']
                                        / slideLOS_tableBookings['BOOKINGS'].sum()) * 100
slideLOS_tableBookings['BOOKINGS'] = slideLOS_tableBookings['BOOKINGS'].astype(int)
slideLOS_tableBookings['% of Total'] = slideLOS_tableBookings['% of Total'].round(decimals=2)
# print(slideLOS_tableBookings)

slide1 = [slideLOS_tableImp, slideLOS_tableClick, slideLOS_tableBookings]


# Creating Tables DTA Slide
slideDTA_tableBookings = pd.pivot_table(booking_df, index=['DTA_Bucket'], values=['BOOKINGS'], aggfunc=np.sum)
slideDTA_tableBookings['% of Total'] = (slideDTA_tableBookings['BOOKINGS']
                                        / slideDTA_tableBookings['BOOKINGS'].sum()) * 100
slideDTA_tableBookings['BOOKINGS'] = slideDTA_tableBookings['BOOKINGS'].astype(int)
slideDTA_tableBookings['% of Total'] = slideDTA_tableBookings['% of Total'].round(decimals=2)
# print(slideDTA_tableBookings)

slide2 = [slideDTA_tableBookings]

# Creating Popularity Ranking Slide
# Creating CrossTab
slideRanked_tab = pd.pivot_table(booking_df, index=['DTA_Bucket'], values=['BOOKINGS'], columns=['LOS_Bucket'],
                                 aggfunc=np.sum, margins=True, margins_name="% of Total")
BOOKINGS_TOTAL = booking_df['BOOKINGS'].sum()
slideRanked_tab = slideRanked_tab / BOOKINGS_TOTAL
# print(slideRanked_tab)

# Creating Trends within Popular Itineraries slide
# Creating Top 5 ranking list
rankbooking_df = booking_df
rankbooking_df['ITIN'] = 'LOS: ' + rankbooking_df['LOS'].astype(str) + " DTA: " + rankbooking_df['DTA'].astype(str)
rankbooking_df = rankbooking_df.groupby('ITIN').agg(TOTAL_BOOKINGS=('BOOKINGS', 'sum'))
rankbooking_df['% OF TOTAL'] = (rankbooking_df['TOTAL_BOOKINGS']/BOOKINGS_TOTAL).round(decimals=4)
rankbooking_df['RANK'] = rankbooking_df['TOTAL_BOOKINGS'].rank(ascending=0).astype(int)
rankbooking_df = rankbooking_df[rankbooking_df['RANK'] <= 5]
rankbooking_df = rankbooking_df.sort_values('RANK')
# print(rankbooking_df)

slide3 = [slideRanked_tab, rankbooking_df]

# Building Trends within Itinerary Slide
# Creating df with only top 5 bookings
# Filtering df based on the top 5 values
popular_df = booking_df[((booking_df['LOS'] == 1) & (booking_df['DTA'] == 0)) |
                        ((booking_df['LOS'] == 1) & (booking_df['DTA'] == 1)) |
                        ((booking_df['LOS'] == 1) & (booking_df['DTA'] == 2)) |
                        ((booking_df['LOS'] == 2) & (booking_df['DTA'] == 0)) |
                        ((booking_df['LOS'] == 2) & (booking_df['DTA'] == 1))]
dow_df = popular_df.groupby('BOOKING_DOW').agg(TOTAL_BOOKINGS=('BOOKINGS', 'sum'))
dow_df = dow_df.reset_index(level=0)
dow_df['BOOKING_DOW'] = pd.Categorical(dow_df['BOOKING_DOW'], ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
dow_df = dow_df.sort_values("BOOKING_DOW")
# print(dow_df)

ax = dow_df.plot.bar(x='BOOKING_DOW', y='TOTAL_BOOKINGS', title="Popular Bookings by DOW", rot=0)
# plt.show()

slide4 = [dow_df]

# Ignoring warning doesn't seem to be an issue will investigate if needed
pd.options.mode.chained_assignment = None

# Building Pricing within Itinerary Details slide
# Creating df with clean spend details
pricing_df = spend_df[spend_df['COMPARISON_TO_LOWEST_PRICE (%)'] > -1]
pricing_df['IS_CHEAPEST'] = np.where(pricing_df['COMPARISON_TO_LOWEST_PRICE (%)'] >= 0, 0, 1)
is_cheapest_tab = pd.crosstab(pricing_df['DTA_Bucket'], pricing_df['LOS_Bucket'], values=pricing_df['IS_CHEAPEST'],
                              aggfunc="mean")

slide5 = [is_cheapest_tab]
# print(is_cheapest_tab)

spend_itinerary_tab = pd.pivot_table(spend_df, index=['DTA_Bucket'], values=['SPEND'], columns=['LOS_Bucket'],
                                     aggfunc=np.sum, margins=True, margins_name="Total Spend $")
spend_itinerary_tab['SPEND'] = spend_itinerary_tab['SPEND'].round(decimals=0).astype(int)
# print(spend_itinerary_tab)

slide6 = [spend_itinerary_tab]

slidedeck = [slide1, slide2, slide3, slide4, slide5, slide6]


def slideprint(x):
    """
    Function to print the same output on presentation slides.
    User enters an integer value 1 to 6 and function will print
    corresponding slide's data tables.
    there is no error checking or exception handling
    TODO: Add error handling
    :param x:user entered int value 1-6
    :return:None
    """
    i = x - 1
    slide = slidedeck[i]
    print("*"*20, "  Printing Slide: {}  ".format(x), "*"*20)
    print()
    for count, tab in enumerate(slide):
        print("*"*20, "  Printing Table: {}  ".format(count + 1), "*"*20)
        print(tab)
        print()
    if x == 4:
        plt.show()

    print(print("*"*22, "  End of Slide   ", "*"*21))


# There is no error checking please only enter integer values 1 - 6
slideprint(1)
