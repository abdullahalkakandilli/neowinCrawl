'''
   
Get inital datetime from neowindate.txt - aws 3 --> last_execute

Get last_feed datetime from neowin rss --> last_feed

Compare last_execute & last_feed

Crawl web indexes after last_execute until last_feed from .rss

Write list to csv file

Upload csv file to Aws s3 Bucket

'''
import urllib.request
from bs4 import BeautifulSoup
import feedparser
import datetime
import boto3
import csv



def lambda_handler(event, context):
   
    s3 = boto3.client("s3")
    s3v2 = boto3.resource('s3')
    if event:
        #file_obj = event["Records"][0]
        bucketname = str("aws-crawl-trigger")
        
        fileObj = s3.get_object(Bucket=bucketname, Key="neowindate.txt")
        file_content = fileObj["Body"].read().decode('utf-8')
   
    
        
        last_execute = datetime.datetime.strptime(file_content, '%a, %d %b %Y %H:%M:%S %z')
        #last_execute will come from aws S3 config datatime
        print("last execute log: ", last_execute)
        print("last feed log: ")
        feed = feedparser.parse('https://www.neowin.net/news/rss')
        
        last_feed = datetime.datetime.strptime(feed.entries[0].published, '%a, %d %b %Y %H:%M:%S %z')
        #websites last entry's publish time - last_feed
        
        
        
        
        

        if last_execute == last_feed:
            print("all is update")   #if there is no new entry, exit script
            
        else:
            title_list = []
            link_list = []
            
            for entry in feed.entries:
                pub_date = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                print("pub date log: ", pub_date)
                test_log = entry.link
                if(pub_date > last_execute):
                    title_list.append(entry.title)
                    link_list.append(entry.link)
                    print("entry link log: ",test_log )
            
        body_list = []
        
        for val in link_list:
            final_para =""
            soup2 = BeautifulSoup(urllib.request.urlopen(val).read(),"html.parser")
            b_tags = soup2.find_all("p") #find all <p> items from html page resource
            
            for i in b_tags:
                #collecting paragraphs
                full_para = i.text
                final_para = final_para+full_para
                print(final_para)
                
            body_list.append(" ".join(final_para.strip()))
    #--------------------------------------------------------------------#        
    feed = feedparser.parse('https://www.neowin.net/news/rss')        
    key2 = 'neowindate.txt'
    fileObj3 = s3.get_object(Bucket=bucketname, Key="neowindate.txt")
    with open('/tmp/neowindate.txt', 'w') as f:
        f.write(feed.entries[0].published)
       
    bucket = s3v2.Bucket(bucketname)
    bucket.upload_file('/tmp/neowindate.txt',key2)
    
    #--------------------------------------------------------------------#
    
    key = 'neowincrawl.csv'
    getfile = s3.get_object(Bucket=bucketname, Key="neowincrawl.csv")
    #Only then you can write the data into the '/tmp' folder.
    rows = zip(title_list,link_list,body_list)
    with open('/tmp/neowincrawl.csv', 'w') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
           
    #upload the data into s3
    bucket = s3v2.Bucket(bucketname)
    bucket.upload_file('/tmp/neowincrawl.csv', key)
    
    
    
    
          
    
    
   

        

    
    
  
    
    
    
