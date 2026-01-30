#!/usr/bin/env python3
# Fetch latest amendments/circulars from official portals and write data/amendments.json
import os, json, re
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dparser

MAX_ITEMS = int(os.getenv('MAX_ITEMS','60'))
HEADERS={'User-Agent':'Mozilla/5.0'}

def norm_date(s):
    try:
        return dparser.parse(s, dayfirst=True, fuzzy=True).strftime('%Y-%m-%d')
    except Exception:
        return ''

def make_item(title, date, source, link, summary=''):
    title=' '.join((title or '').split())
    return {'title':title,'date':date or '','source':source,'link':link,'summary':summary}

# SEBI circulars
def fetch_sebi_circulars(limit=20):
    url='https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=7&smid=0'
    r=requests.get(url,headers=HEADERS,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,'lxml'); items=[]
    for tr in soup.select('table tr')[1:]:
        tds=tr.find_all('td');
        if len(tds)<2: continue
        date_txt=tds[0].get_text(strip=True); a=tds[1].find('a')
        title=(a.get_text(strip=True) if a else tds[1].get_text(strip=True))
        href=urljoin(url,a.get('href','')) if a else url
        d=norm_date(date_txt)
        if title: items.append(make_item(title,d,'SEBI',href))
        if len(items)>=limit: break
    return items

# GST Council notifications
def fetch_gst_notifications(limit=15):
    url='https://gstcouncil.gov.in/cgst-tax-notification'
    r=requests.get(url,headers=HEADERS,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,'lxml'); items=[]
    for tr in soup.select('table tr')[1:]:
        tds=tr.find_all('td');
        if len(tds)<3: continue
        title=tds[2].get_text(' ',strip=True)
        mid=tds[1].get_text(' ',strip=True)
        m=re.search(r'(\d{1,2}[\-/ ]\w+[\-/ ]\d{4}|\d{1,2}[\-/ ]\d{1,2}[\-/ ]\d{2,4})', mid)
        date=norm_date(m.group(0)) if m else ''
        a=tds[1].find('a') or tds[2].find('a')
        href=urljoin(url,a.get('href','')) if a else url
        items.append(make_item(title or mid,date,'GST Council',href))
        if len(items)>=limit: break
    return items

# CBDT
def fetch_cbdt(limit=15):
    url='https://incometaxindia.gov.in/Pages/communications/index.aspx'
    r=requests.get(url,headers=HEADERS,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,'lxml'); items=[]
    for row in soup.select('table tr'):
        cols=row.find_all('td')
        if len(cols)<2: continue
        a=cols[0].find('a') or cols[1].find('a')
        if not a: continue
        title=a.get_text(' ',strip=True)
        href=urljoin(url,a.get('href',''))
        date=norm_date(cols[-1].get_text(strip=True))
        items.append(make_item(title,date,'CBDT',href))
        if len(items)>=limit: break
    return items

# RBI MDs
def fetch_rbi_master_directions(limit=10):
    url='https://www.rbi.org.in/Scripts/BS_ViewMasterDirections.aspx'
    r=requests.get(url,headers=HEADERS,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,'lxml'); items=[]
    for a in soup.select('a'):
        txt=a.get_text(' ',strip=True)
        if not txt: continue
        if 'Master Direction' in txt or 'Directions' in txt:
            href=urljoin(url,a.get('href',''))
            items.append(make_item(txt,'','RBI',href))
            if len(items)>=limit: break
    return items

# MCA notifications
def fetch_mca_notifications(limit=20):
    url='https://www.mca.gov.in/content/mca/global/en/acts-rules/ebooks/notifications.html'
    r=requests.get(url,headers=HEADERS,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,'lxml'); items=[]
    for tr in soup.select('table tr'):
        tds=tr.find_all('td')
        if len(tds)<2: continue
        title=tds[0].get_text(' ',strip=True)
        date=norm_date(tds[-1].get_text(' ',strip=True))
        a=tr.find('a'); href=urljoin(url,a.get('href','')) if a else url
        if title: items.append(make_item(title,date,'MCA',href))
        if len(items)>=limit: break
    return items

# NFRA circulars
def fetch_nfra_circulars(limit=20):
    url='https://nfra.gov.in/document-category/circulars/'
    r=requests.get(url,headers=HEADERS,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,'lxml'); items=[]
    for card in soup.select('article, div.views-row, li'):
        a=card.find('a')
        if not a: continue
        title=a.get_text(' ',strip=True)
        href=urljoin(url,a.get('href',''))
        text=card.get_text(' ',strip=True)
        m=re.search(r'(\d{1,2}[\-/ ]\w+[\-/ ]\d{4}|\d{1,2}[\-/ ]\d{1,2}[\-/ ]\d{2,4}|\w+\s\d{1,2},\s\d{4})', text)
        date=norm_date(m.group(0)) if m else ''
        if title: items.append(make_item(title,date,'NFRA',href))
        if len(items)>=limit: break
    return items

# ICAI announcements
def fetch_icai_announcements(limit=20):
    url='https://www.icai.org/category/announcements'
    r=requests.get(url,headers=HEADERS,timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,'lxml'); items=[]
    for li in soup.select('li, div, p'):
        a=li.find('a');
        if not a: continue
        title=a.get_text(' ',strip=True)
        if not title: continue
        text=li.get_text(' ',strip=True)
        m=re.search(r'\((\d{1,2}-\d{2}-\d{4}|\d{1,2}-\d{1,2}-\d{4})\)', text)
        date=norm_date(m.group(1)) if m else ''
        href=urljoin(url,a.get('href',''))
        if 'icai.org' not in href: continue
        items.append(make_item(title,date,'ICAI',href))
        if len(items)>=limit: break
    return items

# ICAI GN indices
def fetch_icai_guidance_notes(limit=12):
    urls=['https://www.icai.org/post/guidance-notes','https://www.icai.org/post/guidance-notes-on-auditing-aspects']
    items=[]
    for u in urls:
        r=requests.get(u,headers=HEADERS,timeout=30); r.raise_for_status()
        soup=BeautifulSoup(r.text,'lxml')
        for a in soup.select('a'):
            t=a.get_text(' ',strip=True)
            if not t: continue
            if 'Guidance' in t:
                href=urljoin(u,a.get('href',''))
                if 'icai.org' not in href: continue
                items.append(make_item(t,'','ICAI',href))
                if len(items)>=limit: return items
    return items

# de-dup + sort

def unique(items):
    seen=set(); out=[]
    for it in items:
        key=(it['title'].lower(), it['link'])
        if key in seen: continue
        seen.add(key); out.append(it)
    return out


def main():
    all_items=[]
    for fn in (fetch_sebi_circulars, fetch_gst_notifications, fetch_cbdt, fetch_rbi_master_directions, fetch_mca_notifications, fetch_nfra_circulars, fetch_icai_announcements, fetch_icai_guidance_notes):
        try:
            all_items += fn()
        except Exception as e:
            print('source failed:', fn.__name__, e)
    def key(it):
        try: return datetime.strptime(it.get('date') or '1900-01-01','%Y-%m-%d')
        except: return datetime(1900,1,1)
    all_items=unique(all_items)
    all_items.sort(key=key, reverse=True)
    all_items=all_items[:MAX_ITEMS]
    os.makedirs('data', exist_ok=True)
    with open('data/amendments.json','w',encoding='utf-8') as f:
        json.dump({'items': all_items}, f, ensure_ascii=False, indent=2)
    print('Wrote', len(all_items), 'items')

if __name__=='__main__':
    main()
