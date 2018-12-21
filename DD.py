import os, sys
import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup
import re
import argparse


out_dir = '.'    #out dir to write files to
date = 'today'
force_dl = False    #doesn't Re-Download Existing

def main():
    global out_dir
    
    url = url_from_argv()
    print('\n[*]Starting at ',url) 
    dURL = findDarshanURL(url,date,force_dl)
    for imgURLs in dURL:
        out_dir = imgURLs.split('/')[-1]
        if not out_dir:
            out_dir = imgURLs.split('/')[-2]
        
        dPhotoURL = extract_DarshanImages(imgURLs)
        print('[*]{} Images URLs to download: \n{}'.format(len(dPhotoURL),dPhotoURL))
        saveImg(dPhotoURL)

    print('\nYS. Hari Bol! :) ')

    openFolder(out_dir)     # to open the downloaded folder




def url_from_argv():
    global date, force_dl
    url = ''    #init

    parser = argparse.ArgumentParser()
    parser.add_argument('--temple','-t','--Temple','--iskcon','--ISKCON','-i', nargs='*', help='Name of temple like Mayapur')
    parser.add_argument('--url','-u','--URL', help='Explicitly the URL page of Darshan')
    parser.add_argument('--page','-p','--Page', help='Previous pages to dowload')
    parser.add_argument('--all','-a','--All', action='store_true', help='If all pages are to be downloaded')
    parser.add_argument('--force','-f', action='store_true', help='To re-download even if already Downloaded in Past!')
    args,unknown_args = parser.parse_known_args()
    print('[*]Using Args: ',args)
    #print(unknown_args)

    if args.all:
        date = 'all'    #default is today as global
    if args.force:
        force_dl = True
    if args.temple:
        Temple = ' '.join(args.temple)  #to convert list to string
        Temple = Temple.lower()
        Temple = Temple.replace(' ','-')
        url = 'https://darshan.iskcondesiretree.com/category/iskcon-{}/'.format(Temple)
    elif args.url:
        url = arg.url
    if args.page:
        url = url + '/page/{}'.format(args.page)
    if not url:
        #url = u'https://darshan.iskcondesiretree.com/category/iskcon-kolkata/'  #default url
        #print('[-]Nothing specified! Using default: ',url)
        Temple = input("Which Temple?\n")
        Temple = Temple.lower()
        Temple = Temple.replace(' ','-')
        url = 'https://darshan.iskcondesiretree.com/category/iskcon-{}/'.format(Temple)
    return url


def extract_DarshanImages(url):

    print('[*]Downloading from ',url)
    page_x = requests.get(url)
    soup = BeautifulSoup(page_x.content, 'lxml')
    #title = soup.title.text
    #print(u'[+]Trying {}'.format(title))
    img_urls = soup.find_all("a",href=re.compile("\.jpg",re.IGNORECASE))
    dPhotos = []
    for img_url in img_urls:
        dPhotos = dPhotos + [img_url.get("href")]
    
    list(set(dPhotos))
    return(dPhotos)




def findDarshanURL(url,date='today',force_dl=False):
    D_page = requests.get(url)
    soup = BeautifulSoup(D_page.content, 'lxml')
    title = soup.title.text
    #print(title)
    #print(u'[+]Trying {}'.format(title))

    all_links = soup.find_all("a",href=re.compile("https://darshan.iskcondesiretree.com/.*?[\d]+-[\d\w]+-[\d]+")) 
    if not force_dl:
        exists_flag, all_links_new = checkIfAlreadyDownloaded(all_links,date)   # to avoid Re-Downloading
        all_links = all_links_new   #only new links
    #exists_flag=False

    if force_dl or not exists_flag:
        if date is 'today':
            dURL = [all_links[0].get("href")]           #Converting to list just for uniformity with else case
            print('[*]Going after {}'.format(dURL))
        elif date is 'all':
            dURL = []
            for link in all_links:
                dURL = dURL + [link.get("href")]
            dURL = list(set(dURL))
            print('[*]Too many pages to download... ',dURL)
        else:
            pass
    else:
        print('\n[-]Already Exists! Quitting. Use --force flag to Force Download')
        #sys.exit()
        #openFolder(re.search("https://darshan.iskcondesiretree.com/(.*?[\d]+-[\d\w]+-[\d]+)",all_links[0])[1])
        dURL = []

    return(dURL)


def checkIfAlreadyDownloaded(all_links,date='today'):
    new_links_list = []
    alreadyDownloaded = False

    for link in all_links:
        date_info = re.search("https://darshan.iskcondesiretree.com/(.*?[\d]+-[\d\w]+-[\d]+)",str(link))     #2nd element will be date info
        #when iterating over bs4 list, each link is treated as 'navigable bs4 str' not as bs4.tag
        #date_info = re.search("https://darshan.iskcondesiretree.com/(.*?[\d]+-[\d\w]+-[\d]+)",link.get('href'))     
        if not os.path.isdir(date_info[1]):
            new_links_list.append(link)
        else:
            print('[-]Exists: {} SKIPPING!'.format(date_info[1]))
        if date is 'today':     #For taday only 1st link is required, else the previous link becomes 1st one if that already existed
            break

    if not new_links_list:
        alreadyDownloaded = True

    return([alreadyDownloaded, new_links_list])


def saveImg(imgURLs):
    #print('[+]Trying to download:\n',imgURLs)
    print('[*]It looks like our Prayer has been granted!')

    for url in imgURLs:
        r = requests.get(url)

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        try:
            file_name =  unquote(unquote(url.split('/')[-1])).replace('+',' ')
            with open(out_dir + '/' + file_name,'wb') as f:
                f.write(r.content)
            print('[+]Downloaded: ',url)
        except:
            print('[-]Failed to write file.\n')

    print('\n')


def openFolder(out_dir):
    
    if 'win' in sys.platform:
        #not working in *nix
        os.startfile(out_dir)
    else:
        os.system('nautilus {} &> /dev/null &'.format(out_dir))  #to supress the WARNINGS



def url_from_argv_OLD():
    global date

    url = u'https://darshan.iskcondesiretree.com/category/iskcon-kolkata/'  #default url
    #if 'juhu' in Temple: Temple = 'juhu-sringar'  #Juhu has special URL format VERIFY again

    if len(sys.argv) >= 2:
        arg1 = sys.argv[1]
    
        if arg1 == '--all':
            date = 'all'
            try:
                arg2 = sys.argv[2]
                possible_arg2 = ['--url','-url','-u','-t','--temple']
                if arg2 in possible_arg2:
                    url = sys.argv[3]
                    if '.com' not in url: # for just temple name given as --url
                        url = 'https://darshan.iskcondesiretree.com/category/iskcon-{}/'.format(url) 
                        print('[-]Doesn\'t look like a URL: using ',url)
            except:
                print('[-]NO definite URL. Using defualt ...',url)

        elif (arg1 == '--url') or (arg1 == '-u'):
            url = sys.argv[2]
        elif (arg1 == '--iskcon') or (arg1 == '--temple'):
            try:
                arg2 = sys.argv[2]
                Temple = arg2
            except:
                Temple = input("Which Temple?\n")

            Temple = Temple.lower()
            Temple = Temple.replace(' ','-')
            url = 'https://darshan.iskcondesiretree.com/category/iskcon-{}/'.format(Temple)   #change .lower() seeing the URL
        else:
            pass

    return(url)



if __name__ == '__main__':
    main()

