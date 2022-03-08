import re
str='https://www.jstor.org/stable'
print(re.sub('https://(.+?)/', 'https://helkjklsjdkj/', str))
print(re.search('https://(.+?)/', str).group(1))