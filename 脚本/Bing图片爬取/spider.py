import urllib.request,re,sys,os

def get_bing_backphoto():
    if (os.path.exists('pics')== False):
        os.mkdir('pics')

    for i in range(3,10):
        url = 'http://cn.bing.com/HPImageArchive.aspx?format=js&idx='+str(i)+'&n=1&nc=1361089515117&FORM=HYLH1'
        html = urllib.request.urlopen(url).read()

        if html == 'null':
            print( 'open & read bing error!')
            sys.exit(-1)

        html = html.decode('utf-8')
        html = html.replace('/az/','http://cn.bing.com/az/')
        reg = re.compile('"url":"(.*?)","urlbase"',re.S)
        text = re.findall(reg,html)

        for imgurl in text :
            right = imgurl.rindex('/')
            print(imgurl)
            name = imgurl.replace(imgurl[:right+1],'')
            savepath = 'pics/'+ name
            urllib.request.urlretrieve(imgurl, savepath)
            print (name + ' save success!')

get_bing_backphoto()