import HTMLParser
import urllib
import sys

class parseLinks(HTMLParser.HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'src':
            for name, value in attrs:
                print(value)


urlText = []
class parseText(HTMLParser.HTMLParser):
    def handle_data(self, data):
        if data != '/n':
            urlText.append(data)

if __name__ == "__main__":
    #lparser = parseLinks()
    lparser = parseText()
    lparser.feed(urllib.urlopen("http://www.cankaoxiaoxi.com/photo/20200306/2403792_3.shtml").read())
    lparser.close()
    for item in urlText:
        print(item)
