
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# In[2]:


from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase


# In[39]:


def read_data(years=[2008+i for i in range(8)]):
    frames = []
    for y in years:
        frames.append(pd.read_csv('data_files/sahie-{}-csv.zip'.format(y),
                                sep='\s*,\s*',skiprows=79,na_values='.',engine='python'))
        
    return pd.concat(frames)


# In[40]:


data = read_data()


# In[25]:


def query_data(data,age=0,race=0,sex=0,income=0,year=2015):
    query = data[(data['geocat'] == 50) & (data['year'] == year) & (data['agecat'] == age) & 
              (data['racecat'] == race) & (data['sexcat'] == sex) & (data['iprcat'] == income)]
    return query


# In[26]:


def plot_map(latrange,lonrange,ax,resolution='c',projection='tmerc'):
    lllat = latrange[0]
    urlat = latrange[1]
    centerlat = np.mean(latrange)
    lllon = lonrange[0]
    urlon = lonrange[1]
    centerlon = np.mean(lonrange)
    m = Basemap(resolution=resolution,  # crude, low, intermediate, high, full
            llcrnrlon = lllon, urcrnrlon = urlon,
            lon_0 = centerlon,
            llcrnrlat = lllat, urcrnrlat = urlat,
            lat_0 = centerlat,
            projection=projection,ax=ax)
    
    shp_info = m.readshapefile('shape_files/st99_d00', 'states',
                           drawbounds=True, color='lightgrey')
    
    shp_info = m.readshapefile('shape_files/cb_2015_us_county_500k',
                           'counties',
                           drawbounds=True)

    return m


# In[29]:


def color_counties(data,m,ax,mak=None,axak=None,mha=None,axha=None,norm='auto',cmap=plt.cm.viridis):
    if norm == 'auto':
        maxval = data['PCTUI'].max()
    else:
        maxval = norm
    for i, county in enumerate(m.counties_info):
        sfp = int(county['STATEFP'])
        cfp = int(county['COUNTYFP'])
        query = data['PCTUI'][(data['statefips'] == sfp) & (data['countyfips'] == cfp)]
        if query.size == 0:
            ccolor = 'white'
        else:
            ccolor = cmap(query.iloc[0]/maxval)
            
        countyseg = m.counties[i]
        poly = Polygon(countyseg, facecolor=ccolor) 
        
        if mak is not None and axak is not None and sfp == 2:
            countyseg = mak.counties[i]
            poly = Polygon(countyseg, facecolor=ccolor)  
            axak.add_patch(poly)
        elif mha is not None and axha is not None and sfp == 15:
            countyseg = mha.counties[i]
            poly = Polygon(countyseg, facecolor=ccolor)  
            axha.add_patch(poly)
        else:
            countyseg = m.counties[i]
            poly = Polygon(countyseg, facecolor=ccolor)  
            ax.add_patch(poly)
            
    return maxval


# In[47]:


from matplotlib.animation import FuncAnimation


# In[50]:


#get_ipython().magic(u'matplotlib inline')
## set up axes
fig = plt.figure(figsize=(8,4))
fig.subplots_adjust(left=0,right=0.85)
ax1 = plt.subplot2grid((3,6),(0,0),rowspan=2,colspan=2)
ax2 = plt.subplot2grid((3,6),(2,1))
ax3 = plt.subplot2grid((3,6),(0,2),rowspan=3,colspan=4)
ax1.axis('off')
ax2.axis('off')
ax3.axis('off')

## draw the counties
m1 = plot_map([48,70],[-179,-115],ax1)
m2 = plot_map([18.5,22.5],[-160,-154],ax2)
m3 = plot_map([22.0,50.5],[-119,-63],ax3)

## this is where you select which specific demographic you want to query
## a zero is selecting all available data on the demographic
query = query_data(data,age=0,race=0,sex=0,income=0,year=2008)

## select your desired color map here
cmap = plt.cm.rainbow

def update_year(year):
    ax1.patches = []
    ax2.patches = []
    ax3.patches = []
    
    query = query_data(data,age=0,race=0,sex=0,income=0,year=year)
    color_counties(query,m3,ax3,mak=m1,axak=ax1,mha=m2,axha=ax2,norm=50,cmap=cmap)
    plt.suptitle('US Health Insurance Coverage in {}'.format(year))    
    
## add a colorbar
cax = fig.add_axes([0.9, 0.15, 0.03, 0.7])
norm = Normalize(vmin=0,vmax=50)
cb = ColorbarBase(cax, cmap=cmap,norm=norm,orientation='vertical')
cb.set_label('% uninsured by county')

anim = FuncAnimation(fig, update_year, frames=[2008+i for i in range(8)], interval=1000)
anim.save('coverage_by_year.gif',dpi=80, writer='imagemagick')

