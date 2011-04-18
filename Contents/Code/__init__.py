from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

import re

PLUGIN_PREFIX = '/photos/page3'
BASE = 'http://www.page3.com'
INDEX = BASE + '/includes/archive/dates/'

MONTH_NAMES = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
YEAR0 = 2003
####################################################################################################

# TODO: wallpapers, video

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, L('Page 3'), 'icon-default.png', 'art-default.png')
  
  Plugin.AddViewGroup('Cover', viewMode='Coverflow', mediaType='items')
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  
  MediaContainer.title1 = L('Page 3')
  MediaContainer.viewGroup = 'Cover'
  MediaContainer.art = R('art-default.png')
  
  HTTP.SetCacheTime(CACHE_1DAY)
  
####################################################################################################

def MainMenu():
  dir = MediaContainer(viewGroup='List')
  dir.Append(Function(DirectoryItem(NamesMenu, title='Girls by name', thumb=R('icon-default.png'))))
  dir.Append(Function(DirectoryItem(AllMenu, title='All', thumb=R('icon-default.png')), replaceParent=False))
  return dir

def NamesMenu(sender):
  dir = MediaContainer()
  index = 1

  while True:
    page = XML.ElementFromURL('http://page3.com/includes/girls/%i.html' % index, True)
    if page == None:
      break
    else:
      for girl in page.xpath('//div[@id="aToZ_list_namepad"]/a'):
        title = girl.text
        url = girl.get('href').replace(' ', '_')
        if url == '/': continue
        url = BASE + url
        try:
          thumb = BASE + girl.get('onmouseover').split("'")[1].replace(' ', '_')
        except:
          thumb = R('default-icon.png')
        dir.Append(Function(DirectoryItem(GirlMenu, title=title, thumb=thumb), key=url))
    index += 1
  return dir

def AllMenu(sender=None, sortBy='date', key=None, replaceParent=True):
  c = ContextMenu(includeStandardItems=False)
  c.Append(Function(DirectoryItem(GirlMenu, title="By same girl")))
  if sortBy == 'date':
    c.Append(Function(DirectoryItem(NameMenu, title="Sort by name")))
  else:
    c.Append(Function(DirectoryItem(AllMenu, title="Sort by date")))
#  c.Append(Function(DirectoryItem(GirlsMenu, title="Browse Girls")))
  dir = MediaContainer(contextMenu=c, replaceParent=replaceParent)
    
  now = Datetime.Now()
  thisYear = now.year
  thisMonth = now.month
  years = range(YEAR0, thisYear + 1)
  years.reverse()
  
  for year in years:
    if year == thisYear:
      r = range(0, thisMonth)
    else:
      r = range(0, 12)
    r.reverse()
    for month in r:
      page = XML.ElementFromURL(INDEX + str(year) + '_' + MONTH_NAMES[month] + '.html', True)
      script = page.xpath('//script')[0].text
      for img in page.xpath('//div[@class="archive_imagediv"]//img'):
        if img.get('src').split('/')[-1] == 'icon_archive_blank.gif':
          continue
        contextKey = BASE + '/'.join(img.get('src').split('/')[0:3])
        title = img.get('src').split('/')[2].replace('_', ' ').title()
        if title.endswith('Unknown') or title.endswith('Resource'):
          title = title.split(' ')[0]
        dateToPass = img.get('onclick').split("'")[1]
        images = re.findall(r"mainImage\d+\['%s'\] \= '([^']*)'" % dateToPass, script)  #"
        for image in images:
          thumb = BASE + image
          dir.Append(Function(PhotoItem(PhotoMenu, title=title, contextKey=contextKey, contextArgs={}, thumb=thumb), url=thumb))
  return dir

def PhotoMenu(url, sender=None):
  return Redirect(url)

def NameMenu(sender=None, key=None):
  dir = AllMenu(sortBy='name')
  dir.Sort('title')
  return dir


def GirlMenu(sender, key):
  dir = MediaContainer()
  for script in XML.ElementFromURL(key, True).xpath('//script'):
    scriptText = script.text
    if scriptText != None:
      images = re.findall(r"image_name\[\d+\] \= '([^']*)'", script.text)  #"
      for image in images:
        if 'main_image' in image:
          thumb = BASE + '/girl/' + image
          dir.Append(PhotoItem(thumb, title=sender.itemTitle, thumb=thumb))
  return dir
  
def GirlsMenu(sender, key):
  dir1 = NameMenu()
  dir2 = MediaContainer()
  name = None
  for item in dir1:
    if item.title != name:
      dir2.Append(Function(DirectoryItem(GirlMenu, title=item.title, thumb=item.key), url=item.contextKey))
      name = item.title
  return dir2

