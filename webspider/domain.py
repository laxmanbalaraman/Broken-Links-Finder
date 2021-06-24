from urllib.parse import urlparse


# Get domain name (example.com)
def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        return results[-2] + '.' + results[-1]
    except:
        return ''


# Get sub domain name (name.example.com)
def get_sub_domain_name(url):
    try:
        #netloc gives network location Eg. netloc of (www.teams.microsoft.com) is teams.microsoft.com
        return urlparse(url).netloc
    except:
        return ''

#print(get_sub_domain_name("https://teams.microsoft.com/"));
