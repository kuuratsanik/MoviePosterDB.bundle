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
            
      # Look through the posters for ones with language matches.
      for poster in queryJSON['posters']:
        poster_language = poster['language'].lower().replace('us', 'en').replace('uk', 'en').replace('ca', 'en')
        if lang == poster_language:
          Log('Adding matching language poster for language: %s', poster['language'])
          valid_names.append(self.add_poster(metadata, secret, poster, i))
          i += 1
          found = True
          
      # If we didn't find a language match, add the first foreign one.
      if i == 0 and len(queryJSON['posters']) > 0:
        Log('Falling back to foreign language poster with language: %s', queryJSON['posters'][0]['language'])
        valid_names.append(self.add_poster(metadata, secret, queryJSON['posters'][0], i))
          
    metadata.posters.validate_keys(valid_names)
    
  def add_poster(self, metadata, secret, poster, index):
    imageUrl = MPDB_ROOT + '/' + poster['image_location']
    thumbUrl = MPDB_ROOT + '/' + poster['thumbnail_location']
    full_image_url = imageUrl + '?api_key=p13x2&secret=' + secret

    Log('Adding new poster: %s' % full_image_url)
    metadata.posters[full_image_url] = Proxy.Preview(HTTP.Request(thumbUrl), sort_order = index)
    return full_image_url
    
