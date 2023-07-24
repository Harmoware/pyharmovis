import os
import html
import jinja2
import pandas
import requests
import json

from pyharmovis.template import getHtml
from IPython.display import HTML  # noqa

def render_json_to_html(widgetCdnPath,mapboxApiKey,movesLayer,movesbase,depotsLayer,depotsBase,viewport,orbitViewSw):
    basehtml = getHtml()
    template = jinja2.Template(source=basehtml)
    return template.render(
        widgetCdnPath=widgetCdnPath,
        mapboxApiKey=mapboxApiKey,
        movesLayer=movesLayer,
        movesbase=movesbase,
        depotsLayer=depotsLayer,
        depotsBase=depotsBase,
        viewport=viewport,
        orbitViewSw=orbitViewSw
    )

class HvDeck:
    widgetCdnPath = None
    mapboxApiKey = None
    movesLayerName = None
    movesbasedataframe = None
    depotsLayerName = None
    depotsBasedataframe = None
    viewport = None

    def __init__(self,mapboxApiKey='MAPBOX_ACCESS_TOKEN',widgetCdnPath='http://192.168.197.229/HarmoVis-widget/library.js'):
        self.mapboxApiKey = os.environ.get(mapboxApiKey)
        if(self.mapboxApiKey == None):
            self.mapboxApiKey = ""
            print("Mapbox ApiKey could not be obtained.")
        self.widgetCdnPath = widgetCdnPath

    def setApiKey(self,mapboxApiKey=None):
        self.mapboxApiKey = os.environ.get(mapboxApiKey)
        if(self.mapboxApiKey == None):
            self.mapboxApiKey = mapboxApiKey
        print("mapboxApiKey:",self.mapboxApiKey)

    def setLayer(self,layer=None):
        layers = []
        if(type(layer) is list):
            layers = layer
        else:
            layers.append(layer)
        for layerItem in layers:
            if(type(layerItem) is MovesLayer):
                self.movesbasedataframe = layerItem.dataframe
                self.movesLayerName = layerItem.layerName
            elif(type(layerItem) is PointCloudLayer):
                self.movesbasedataframe = layerItem.dataframe
                self.movesLayerName = layerItem.layerName
            elif(type(layerItem) is DepotsLayer):
                self.depotsBasedataframe = layerItem.dataframe
                self.depotsLayerName = layerItem.layerName
            else:
                print("HvDeck.setLayer : Unsupported data!")

    def setViewport(self,viewport=None):
        if(type(viewport) is dict):
            self.viewport = viewport
        else:
            print("HvDeck.setViewport : Unsupported data!")

    def display(self,width="100%",height=600,orbitViewSw=False):
        html_str = render_json_to_html(
            self.widgetCdnPath,
            self.mapboxApiKey,
            self.movesLayerName,
            self.movesbasedataframe,
            self.depotsLayerName,
            self.depotsBasedataframe,
            self.viewport,
            orbitViewSw
            )
        srcdoc = html.escape(html_str)
        iframe = f"""<iframe width={width} height={height} frameborder="0" srcdoc="{srcdoc}"></iframe>"""
        return HTML(iframe)

    def to_html(self,filename='Sample.html',orbitViewSw=False):
        html_str = render_json_to_html(
            self.widgetCdnPath,
            self.mapboxApiKey,
            self.movesLayerName,
            self.movesbasedataframe,
            self.depotsLayerName,
            self.depotsBasedataframe,
            self.viewport,
            orbitViewSw
            )
        with open(filename, "w+", encoding="utf-8") as f:
            f.write(html_str)

class MovesLayer:
    dataframe = None
    layerName = "MovesLayer"

    def __init__(self,dataframe=None):
        if dataframe is None:
            self.dataframe = dataframe
        else:
            self.setData(dataframe)

    def setData(self,dataframe):
        if (type(dataframe) is pandas.core.frame.DataFrame):
            json_str = "["
            for num1 in range(len(dataframe.index)):
                json_str += """{"operation":["""
                for num2 in range(len(dataframe.columns)):
                    if dataframe[num2][num1] != None:
                        json_str += json.dumps(dataframe[num2][num1]) + ","
                json_str += "]},"
            json_str += "]"
            self.dataframe = json_str
        elif(type(dataframe) is str):
            r = requests.get(dataframe)
            self.dataframe = r.text
        elif(type(dataframe) is list):
            self.dataframe = dataframe
        else:
            print("MovesLayer.setData : Unsupported data!")

class PointCloudLayer(MovesLayer):
    def __init__(self,dataframe=None):
        super().__init__(dataframe)
        self.layerName = "PointCloudLayer"

class DepotsLayer:
    dataframe = None
    layerName = "DepotsLayer"

    def __init__(self,dataframe=None):
        if dataframe is None:
            self.dataframe = dataframe
        else:
            self.setData(dataframe)

    def setData(self,dataframe):
        if (type(dataframe) is pandas.core.frame.DataFrame):
            json_str = "["
            for index, row in dataframe.iterrows():
                json_str += "{"
                for item in dataframe:
                    if str(row[item]) != 'nan':
                        if(type(row[item]) is str):
                            json_str += '"'+str(item)+'":"'+str(row[item])+'",'
                        else:
                            json_str += '"'+str(item)+'":'+str(row[item])+','
                json_str += "},"
            json_str += "]"
            self.dataframe = json_str
        elif(type(dataframe) is str):
            r = requests.get(dataframe)
            self.dataframe = r.text
        elif(type(dataframe) is list):
            self.dataframe = dataframe
        else:
            print("DepotsLayer.setData : Unsupported data!")
