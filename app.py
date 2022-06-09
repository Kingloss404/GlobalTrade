import streamlit as st
import pandas as pd
import time
import numpy as np
import pycountry_convert as pc
import plotly.express as px
import plotly.graph_objects as go
np.seterr(all="raise")

a = time.time()
@st.experimental_memo
def df_data():
  df_i = pd.read_pickle("C:\\Users\\hp\\Desktop\\Cv_project\\Dashboard_imp_exp\\filtered_data\\Importation.pkl",compression="gzip")
  df_e = pd.read_pickle("C:\\Users\\hp\\Desktop\\Cv_project\\Dashboard_imp_exp\\filtered_data\\Exportation.pkl",compression="gzip")
  return (df_i, df_e)


#Return total trade value for each country per year
def total_trade(df):
    data = df[["Reporter","Year","TradeValue"]]
    data = data.groupby(["Reporter","Year"], as_index=False).sum()
    data["TradeValue"] = data["TradeValue"].apply(lambda x: x/2)
    return data


#Same as before but adds the partner country
def ftotal_trade(df):
    dat = df[["Reporter", "Partner", "Year", "TradeValue"]]
    dat= dat.groupby(["Reporter","Partner","Year"], as_index=False).sum()
    dat[["Reporter","Partner"]] = dat[["Reporter","Partner"]].astype(str)
    dat = dat[dat["Reporter"] != dat["Partner"]]
    return dat

@st.experimental_memo
#A shortcut to grouping and returning
def pgroup(df, group, key):
    df = df.groupby(group)
    return df.get_group(key)

df_imp, df_exp = df_data()


def ttl_maker(_func):#modeified from notebook
    ttl_imp = _func(df_imp)
    ttl_exp = _func(df_exp)
    ttl_imp["Flow"] = "Import"
    ttl_exp["Flow"] = "Export"
    tot = pd.concat([ttl_imp,ttl_exp], axis = 0, ignore_index=True)
    return tot

# Add a selectbox to the sidebar:
country_box = st.sidebar.selectbox(
    'Country Name',
    df_imp["Partner"].unique()
)

# Add a slider to the sidebar:
year_box = st.sidebar.slider(
    'Year',
    2009, 2018
)

#Add a flow box:
flow_box = st.sidebar.selectbox(
    'Flow',
    ("Import","Export")
)

if flow_box =="Import":
    mode=0
else :
    mode=1

#Line Graph
line_plt = px.line(pgroup(ttl_maker(total_trade), ["Reporter"], country_box), 
x="Year", y="TradeValue", color='Flow')

#Choropleth
@st.experimental_memo
def map_maker():
    if mode ==0:
        country = pgroup(ftotal_trade(df_imp), ["Reporter","Year"], (country_box,year_box))
    else:
        country = pgroup(ftotal_trade(df_exp), ["Reporter","Year"], (country_box,year_box))
    return go.Figure(go.Choropleth(
        locations = country["Partner"],
        z = country["TradeValue"],
        text = country["Partner"],
        colorscale = 'brbg',
        autocolorscale=False,
        reversescale=True,
        marker_line_color='darkgrey',
        marker_line_width=0.5,
        colorbar_tickprefix = '$',
        colorbar_title = 'Cost<br>Thousands $',
    ))

##Pie_maker
@st.experimental_memo
def pie_grouper(df, key):
    test1 = df[["Reporter","TradeValue","Year","HS_Prod"]]
    test1 = test1.groupby(["Reporter","Year","HS_Prod"],as_index=False).sum()
    test1 = test1.groupby(["Reporter","Year"]).get_group(key)
    return test1.sort_values(by ="TradeValue", ascending=False).reset_index(drop=True)
#Helper due to segmenting
@st.experimental_memo
def summer(df):
    other = df.loc[[i for i in range(10,len(df))]]["TradeValue"].sum()
    dff = df.loc[[i for i in range(10)]]
    dff.loc[len(dff)] = [df["Reporter"][0], df["Year"][0], "Other", other]
    return dff

if mode==0:
    pie_fig = px.pie(summer(pie_grouper(df_imp, (country_box,year_box))))
else :
    pie_fig = px.pie(summer(pie_grouper(df_exp, (country_box, year_box))),values="TradeValue", names="HS_Prod",
    title="Top 10 "+flow_box+"Product ")

##Commented until Performance issue resolved
# @st.cache
# def for_the_bubbles():
#     ttl_ftrade = ttl_maker(ftotal_trade)
#     ttl_trade = ttl_maker(total_trade).rename(columns={"TradeValue":"Total_ioe"})
#     full = ttl_trade.merge(ttl_ftrade, on=["Reporter","Year","Flow"], how="inner")
#     return ttl_ftrade,ttl_trade,full

# ttl_ftrade, ttl_trade, totally = for_the_bubbles()

# ##FOR THE BUBBLES!!!!!!
# @st.experimental_memo
# def intensity_query(rep,year,part):
#     return  totally.query(f"(Reporter == '{rep}' | Reporter == '{part}') & Year == {year} & (Partner == '{rep}' | Partner == '{part}')")

# @st.experimental_memo
# def wld(year):
#     ewld = ttl_trade[["Year","Flow","Total_ioe"]].groupby(["Year","Flow"]).get_group((year,"Export"))["Total_ioe"].sum()
#     iwld = ttl_trade[["Year","Flow","Total_ioe"]].groupby(["Year","Flow"]).get_group((year,"Import"))["Total_ioe"].sum()
#     return iwld,ewld

# @st.experimental_memo
# def ivalue(rep,year,part,flow):
#     try:
#         iy = intensity_query(rep,year,part).set_index(["Reporter","Flow"])
#         ioe = ["Import","Export"]
#         xw = wld(year)[1]
#         i,e = ioe[0],ioe[1]
#         if flow == "Export":
#             i,e = ioe[1],ioe[0]
#             xw = wld(year)[0]
        
#         mij = iy.loc[(rep,i)]["TradeValue"]
#         mi = iy.loc[(rep,i)]["Total_ioe"]
#         xi = iy.loc[(rep,e)]["Total_ioe"]
#         xj = iy.loc[(part,e)]["Total_ioe"]
        
#         return (mij/mi)/(xj/(xw-xi))
#     except Exception as e:
#         return 0

# @st.experimental_memo
# def applier(x,flow):
#     return ivalue(x[0],x[1],x[2],flow)

# @st.experimental_memo
# def intensify_table(rep,year,intense):
#     df = pgroup(intense, ["Reporter","Year"],(rep,year)).reset_index(drop=True)
#     df["Import_i"] = df.apply(lambda x : applier(x,"Import"), axis=1)
#     df["Export_i"] = df.apply(lambda x : applier(x,"Export"), axis=1)
#     return df

# ##GDP_maker
# @st.cache
# def gdp_maker():
#     gdp = pd.read_csv("C:\\Users\\hp\\Desktop\\Cv_project\\Dashboard_imp_exp\\GDP.csv")
#     gdp.drop([i for i in gdp.columns[2:20]],axis=1, inplace=True)
#     gdp.drop(labels="2019", axis=1,inplace=True)
#     return gdp
    
# gdp = gdp_maker()
# gdpcopy = gdp.copy(deep=True)
# @st.experimental_memo
# def meanyear(year):
#     return gdpcopy[str(year)].mean()

# for i in range(2008,2019):
#     meani = meanyear(i)
#     gdp[str(i)].fillna(value=meani,inplace=True)

# gdp = gdp.melt(id_vars=[gdp.columns[0], "Country Code"],value_vars=[str(i) for i in range(2009,2019)])
# gdp.rename({"value":"GDP","variable":"Year","Country Code":"Partner"},axis=1,inplace = True)
# gdp["Year"] = gdp["Year"].astype(int)


# gdp_bubbles = totally.merge(gdp, on =["Partner","Year"], how="left")
# gdp_bubbles[gdp_bubbles.columns[-2]].fillna(gdp_bubbles["Partner"],inplace = True)

# gdp_bubbles = gdp_bubbles[["Reporter","Year","Partner","GDP",gdp_bubbles.columns[-2]]].drop_duplicates(ignore_index=True)
# gdp_bubbles["GDP"].fillna(value=gdp_bubbles["Year"].apply(meanyear), inplace=True)

# def alpha2_continent(iso3):
#     continents = {
#         'NA': 'North America',
#         'SA': 'South America', 
#         'AS': 'Asia',
#         'AN': 'Antarctica',
#         'OC': 'Oceania',
#         'AF': 'Africa',
#         'EU': 'Europe'
#     }
#     try:
#         code2 = pc.country_alpha3_to_country_alpha2(iso3)
#         cont = pc.country_alpha2_to_continent_code(code2)
        
#     except Exception as e:
#         return "NoCont"
    
#     return continents[cont]

# gdp_bubbles["Continent"] = gdp_bubbles["Partner"].apply(alpha2_continent)

# bubble_data = intensify_table(country_box,year_box, gdp_bubbles)

#The Bubbles
#bubble_fig = px.scatter(bubble_data, x ="Import_i", y="Export_i", size="GDP", color="Continent",hover_name="Country")

st.plotly_chart(line_plt)
st.plotly_chart(map_maker())
st.plotly_chart(pie_fig)
#st.plotly_chart(bubble_fig)