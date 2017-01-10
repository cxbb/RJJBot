# coding=UTF-8
from base_module import BaseModule
import subprocess
import json
import random

class AqiModule(BaseModule):

  stations = [{"station":"東涌","id":2568},{"station":"屯門","id":3928},{"station":"塔門","id":2565},{"station":"元朗","id":2569},{"station":"大埔","id":2566},{"station":"沙田","id":2563},{"station":"觀塘","id":2562},{"station":"荃灣","id":2567},{"station":"葵涌","id":2561},{"station":"深水埗","id":2564},{"station":"東區","id":2560},{"station":"銅鑼灣","id":2570},{"station":"中環","id":2571},{"station":"中西區","id":2559},{"station":"旺角","id":2572 }]
  QUOTE_URL = { 'aqi': 'http://api.waqi.info/feed/@%d/?token=%s' }

  def __init__(self):
    self.command_specs = [
      { 'spec': ['aqi'], 'func': self.get_aqi_here, 'desc': '/aqi - Show AQI in HK' },
      { 'spec': ['aqi', 'list', ':'], 'desc': '/aqi list - list all stations id'},
      { 'spec': ['aqi', ':int'], 'desc': '/aqi <id> - Get AQI for station with <ID>', 'func': self.get_aqi_id},
      { 'spec': ['aqi', ':string'], 'desc': '/aqi <string> - Get AQI for station with <name>', 'func': self.get_aqi_name},
    ]
    with open('aqi-token.txt', 'r') as f:
      self.token = f.read().strip()

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
      so2 = u"二氧化硫: %d ug/m³\n" % obj['data']['iaqi']['so2']['v']
      o3 = u"臭氧: %d ug/m³\n" % obj['data']['iaqi']['o3']['v']
      if 'co' in obj['data']['iaqi']:
        co = u"一氧化碳: %d ppm\n" % obj['data']['iaqi']['co']['v']
      else:
        co = ''
      no2 = u"二氧化氮: %d ug/m³\n" % obj['data']['iaqi']['no2']['v']
      pm25 = u"PM2.5: %d ug/m³\n" % obj['data']['iaqi']['pm25']['v']
      pm10 = u"PM10: %d ug/m³\n" % obj['data']['iaqi']['pm10']['v']
      temp = u"溫度: %d °C\n" % obj['data']['iaqi']['t']['v']
      pressure = u"氣壓: %d hPa\n" % obj['data']['iaqi']['p']['v']
      uvi = u"UVI: %d\n" % obj['data']['iaqi']['uvi']['v']
      windspeed = u"風速: %d m/s\n" % obj['data']['iaqi']['uvi']['v']
      humidity = u"濕度: %d%%\n" % obj['data']['iaqi']['h']['v']
      drew = u"Dew: %d\n" % obj['data']['iaqi']['d']['v']
      aqi = "AQI: %d\n" % obj['data']['aqi']
      comment = u"Level: %s\n\n" % self.get_pollution_level(obj['data']['aqi'])
      sources = "http://aqicn.org/"
      return header + temp + humidity + uvi + so2 + o3 + co + no2 + pm25 + pm10 + aqi + comment + sources
    except Exception, e:
      raise Exception('Enjoy. Error: %s %s' % (str(e), out))
  



