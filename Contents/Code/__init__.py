# MoviePosterDB
MPDB_ROOT = 'http://movieposterdb.plexapp.com'
MPDB_JSON = MPDB_ROOT + '/1/request.json?imdb_id=%s&api_key=p13x2&secret=%s&width=720&thumb_width=100'
MPDB_SECRET = 'e3c77873abc4866d9e28277a9114c60c'

def Start():
  HTTP.CacheTime = CACHE_1DAY
  
class MPDBAgent(Agent.Movies):
  name = 'MoviePosterDB'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.imdb']
  
  def search(self, results, media, lang):
    if media.primary_metadata is not None:
      results.Append(MetadataSearchResult(id = media.primary_metadata.id.replace('tt',''), score = 100))

  def update(self, metadata, media, lang):
    imdb_code = metadata.id.lstrip('t0')
    secret = Hash.MD5( ''.join([MPDB_SECRET, imdb_code]))[10:22]
    queryJSON = JSON.ObjectFromURL(MPDB_JSON % (imdb_code, secret), cacheTime=10)
    valid_names = list()

    if not queryJSON.has_key('errors') and queryJSON.has_key('posters'):
      i = 0
      valid_names = list()
      
      for poster in queryJSON['posters']:
        imageUrl = MPDB_ROOT + '/' + poster['image_location']
        thumbUrl = MPDB_ROOT + '/' + poster['thumbnail_location']
        full_image_url = imageUrl + '?api_key=p13x2&secret=' + secret
        metadata.posters[full_image_url] = Proxy.Preview(HTTP.Request(thumbUrl), sort_order = i)
        valid_names.append(full_image_url)
        i += 1
     
    metadata.posters.validate_keys(valid_names)
