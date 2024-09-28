import requests
import pandas as pd

country_codes_url = 'https://www.olympedia.org/countries'
countries_df = pd.read_html(country_codes_url)[0]
# print(countries)

df = pd.DataFrame()
for i in range(len(countries_df)):
    country_code = countries_df.loc[i, 'Abbreviation']
    url = 'https://www.olympedia.org/counts/country/' + country_code
    print(url)
    genders_df = pd.read_html(url)[0]
    for j in range(2, len(genders_df)-2):
        id = genders_df.loc[j, 0]
        df.loc[id, country_code + 'm'] = genders_df.loc[j, len(genders_df.columns)-3]
        df.loc[id, country_code + 'w'] = genders_df.loc[j, len(genders_df.columns)-2]
        df.loc[id, country_code + 'all'] = genders_df.loc[j, len(genders_df.columns)-1]

df = df.replace(to_replace={'-':0}) # replace hyphens with 0s
df.to_csv('genders.csv', index=True)