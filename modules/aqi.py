# coding=UTF-8
from base_module import BaseModule
import subprocess
import json
import random

class AqiModule(BaseModule):

  stations = [{"station":"東涌","id":2568},{"station":"屯門","id":3928},{"station":"塔門","id":2565},{"station":"元朗","id":2569},{"station":"大埔","id":2566},{"station":"沙田","id":2563},{"station":"觀塘","id":2562},{"station":"荃灣","id":2567},{"station":"葵涌","id":2561},{"station":"深水埗","id":2564},{"station":"東區","id":2560},{"station":"銅鑼灣","id":2570},{"station":"中環","id":2571},{"station":"中西區","id":2559},{"station":"旺角","id":2572 }, {'station': '北京', 'id': 447}]
  QUOTE_URL = { 'aqi': 'http://api.waqi.info/feed/@%d/?token=%s' }

  def __init__(self):
    self.command_specs = [
      { 'spec': ['aqi'], 'func': self.get_aqi_here, 'desc': '/aqi - Show AQI in HK' },
      { 'spec': ['aqi', 'help'], 'desc': '/aqi help - Show this help', 'func': self.help},
      { 'spec': ['aqi', 'list', ':'], 'desc': '/aqi list - list all stations id', 'func': self.list_all_stations},
      { 'spec': ['aqi', ':int'], 'desc': '/aqi &lt;id&gt; - Get AQI for station with &lt;ID&gt;', 'func': self.get_aqi_id},
      { 'spec': ['aqi', ':string'], 'desc': '/aqi &lt;name&gt; - Get AQI for station with &lt;name&gt;', 'func': self.get_aqi_name}
    ]
    with open('aqi-token.txt', 'r') as f:
      self.token = f.read().strip()
  
  def list_all_stations(self, cmd): 
    return u"ID 地點\n" + u"\n".join([ "<"+str(station['id'])+"> "+station['station'].decode('utf-8') for station in AqiModule.stations ])

  def get_aqi_here(self, cmd):
    return self.get_aqi(2559)

  def get_aqi_id(self, cmd):
    return self.get_aqi(cmd[1])

  def get_aqi_name(self, cmd):
    stationId = [ o['id'] for o in AqiModule.stations if o['station'].decode('utf-8') == cmd[1] ]
    stationId = 2559 if stationId == [] else stationId[0]
    return self.get_aqi(stationId)
    
  def get_pollution_level(self, aqi):
    if aqi <= 50:
      return u"優"
    elif aqi <= 100:
      return u"良"
    elif aqi <= 150:
      return u"輕度"
    elif aqi <= 200:
      return u"中度"
    elif aqi <= 300:
      return u"重度"
    return u"嚴重"

  def get_aqi(self, stationId):
    try:
      p = subprocess.Popen(['curl', '-L', '-k', (AqiModule.QUOTE_URL['aqi'] % (stationId, self.token))], stdout=subprocess.PIPE)
      out, err = p.communicate()
      obj = json.loads(out)
      header = "%s at %s\n" % (obj['data']['city']['name'], obj['data']['time']['s'] )
      if 'url' in obj['data']['city']:
        sources = obj['data']['city']['url']
      else:
        sources = 'http://aqicn.org'
      iaqi = obj['data']['iaqi']
      so2 = u"二氧化硫: %d ug/m³\n" % iaqi['so2']['v'] if 'so2' in iaqi else ''
      o3 = u"臭氧: %d ug/m³\n" % iaqi['o3']['v'] if 'o3' in iaqi else ''
      co = u"一氧化碳: %d ppm\n" % iaqi['co']['v'] if 'co' in iaqi else ''
      no2 = u"二氧化氮: %d ug/m³\n" % iaqi['no2']['v'] if 'no2' in iaqi else ''
      pm25 = u"PM2.5: %d ug/m³\n" % iaqi['pm25']['v'] if 'pm25' in iaqi else ''
      pm10 = u"PM10: %d ug/m³\n" % iaqi['pm10']['v'] if 'pm10' in iaqi else ''
      temp = u"溫度: %d °C\n" % iaqi['t']['v'] if 't' in iaqi else ''
      pressure = u"氣壓: %d hPa\n" % iaqi['p']['v'] if 'p' in iaqi else ''
      uvi = u"UVI: %d\n" % iaqi['uvi']['v'] if 'uvi' in iaqi else ''
      windspeed = u"風速: %d m/s\n" % iaqi['w']['v'] if 'w' in iaqi else ''
      humidity = u"濕度: %d%%\n" % iaqi['h']['v'] if 'h' in iaqi else ''
      dew = u"Dew: %d\n" % iaqi['d']['v'] if 'd' in iaqi else ''
      comment = u"%s" % self.get_pollution_level(obj['data']['aqi'])
      aqi = "AQI: %d (%s)\n" % (obj['data']['aqi'], comment)
      return header + temp + humidity + uvi + so2 + o3 + co + no2 + pm25 + pm10 + aqi + sources
    except Exception, e:
      raise Exception('Enjoy. Error: %s %s' % (str(e), out))
  



