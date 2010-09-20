MPDB_JSON = 'http://api.movieposterdb.com/json.inc.php?imdb=%s&width=300'

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
    print MPDB_JSON % metadata.id
    if not queryJSON.has_key('errors'):
      pageUrl = queryJSON['page'].replace('\\','')
      if pageUrl:
        
        @parallelize
        def loopThroughPosters():
          try:
            i = 0
            for pUrl in HTML.ElementFromURL(pageUrl).xpath("//td[@class='poster']"):
              i += 1
              @task
              def grabPoster(pUrl=pUrl, i=i):
                thumbUrl = pUrl.xpath('div/a/img')[0].get('src')
                posterUrl = thumbUrl.replace('s_', 'l_').replace('t_', 'l_')
                
                proxy = Proxy.Preview
                thumb = HTTP.Request(thumbUrl)
                metadata.posters[posterUrl] = proxy(thumb, sort_order = i)
                
          except:
            pass
