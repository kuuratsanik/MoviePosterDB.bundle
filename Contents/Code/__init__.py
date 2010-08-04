#MoviePosterDB
#import md5
MPDB_JSON = 'http://api.movieposterdb.com/json.inc.php?imdb=%s&width=300'
defaultFlag = 'US'
flagSearchUrl = 'http://www.movieposterdb.com/images/flags/%s.gif'

def Start():
  HTTP.CacheTime = CACHE_1DAY
  HTTP.SetHeader('User-agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)')
  
class MPDBAgent(Agent.Movies):
  name = 'MoviePosterDB'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.imdb']
  
  def search(self, results, media, lang):
    if media.primary_metadata is not None:
      results.Append(MetadataSearchResult(id = media.primary_metadata.id.replace('tt',''), score = 100)) # we can use the IMDB id for this one

  def update(self, metadata, media, lang):
    queryJSON = JSON.ObjectFromURL(MPDB_JSON % metadata.id)
    if not queryJSON.has_key('errors'):
      imageUrl = queryJSON['imageurl'].replace('\\','')
      pageUrl = queryJSON['page'].replace('\\','')
      if imageUrl:
        name = imageUrl.split('/')[-1]
        #Log(md5.new(str(int(metadata.id)).encode('utf-8')).hexdigest()[9:21]) #this is a version of the algorithm we can use once we have an api key
        if name not in metadata.posters:
          try:
            metadata.posters[name] = Proxy.Media(HTTP.Request(imageUrl), sort_order = 1)
          except:
            pass
      if pageUrl:
        posterUrls = []
        @parallelize
        def loopThroughPosters():
          try:
            for pUrl in HTML.ElementFromURL(htmlStr).xpath("//td[@class='poster']"):
              #TODO: ask James how best to handle country codes
              @task
              def grabPoster(pUrl=pUrl):
                posterUrl = pUrl.xpath('div/a')[0].get('href')
                if posterUrl.count('group/') > 0:
                  for gpUrl in HTML.ElementFromURL(posterUrl).xpath("//td[@class='poster']"):
                    if gpUrl.xpath('..//img[contains(@src,"images/flags")]')[0].get('src') == flagSearchUrl % defaultFlag:
                      posterUrls.append(gpUrl)
                else:
                  try:
                    if pUrl.xpath('..//img[contains(@src,"images/flags")]')[0].get('src') == flagSearchUrl % defaultFlag:
                      posterUrls.append(pUrl)
                  except:
                    pass
          except:
            pass
                  
        i = 2
        
        # Dedupe and get URLs.
        urls = []
        urlMap = {}
        
        seen = set()
        urlPairs = [self.getPosterUrls(x) for x in posterUrls]
        urls = [x for x in urlPairs if x is not None and x[0] not in seen and not seen.add(x[0])]
            
        for urlPair in urls:
          self.getPoster(urlPair, metadata, i)
          i += 1
            
  def getPosterUrls(self, posterEl):
    try:
      posterUrl = posterEl.xpath('..//a')[0].get('href')
      largePosterUrl = HTML.ElementFromURL(posterUrl).xpath('//img[@id="poster_image"]')[0].get('src')
      thumbUrl = posterEl.xpath('..//img')[0].get('src')
      return [thumbUrl, largePosterUrl]
    except:
      return None
    
  def getPoster(self, urlPair, metadata, i):
    try:
      thumbUrl, largePosterUrl = urlPair
      proxy = Proxy.Preview
      thumb = HTTP.Request(thumbUrl)
      metadata.posters[largePosterUrl] = proxy(thumb, sort_order = i)
    except:
      pass