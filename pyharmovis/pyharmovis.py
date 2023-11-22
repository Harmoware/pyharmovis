import os
import html
import jinja2
import pandas
import requests
import json

from pyharmovis.template import getHtml
from IPython.display import HTML  # noqa

def render_json_to_html(widgetCdnPath,mapboxApiKey,movesLayer,movesbase,depotsLayer,depotsBase,viewport,property,orbitViewSw):
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
        property=property,
        orbitViewSw=orbitViewSw
    )

class HvDeck:
    widgetCdnPath = None
    mapboxApiKey = None
    movesLayerName = []
    movesbasedataframe = None
    depotsLayerName = []
    depotsBasedataframe = None
    viewport = None
    property = None

    def __init__(self,mapboxApiKey='MAPBOX_ACCESS_TOKEN',widgetCdnPath='http://192.168.197.229/HarmoVis-widget/library.js'):
        if(mapboxApiKey == ""):
            self.mapboxApiKey = ""
        else:
            self.mapboxApiKey = os.environ.get(mapboxApiKey)
            if(self.mapboxApiKey == None):
                self.mapboxApiKey = ""
                print("Mapbox ApiKey could not be obtained.")
        self.widgetCdnPath = widgetCdnPath
        self.movesLayerName = []
        self.movesbasedataframe = None
        self.depotsLayerName = []
        self.depotsBasedataframe = None
        self.viewport = None
        self.property = None


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
                if layerItem.dataframe is not None:
                    self.movesbasedataframe = layerItem.dataframe
                self.movesLayerName.append(layerItem.layerName)
                self.movesLayerName.append(layerItem.assignProps)
            elif(type(layerItem) is PointCloudLayer):
                if layerItem.dataframe is not None:
                    self.movesbasedataframe = layerItem.dataframe
                self.movesLayerName.append(layerItem.layerName)
                self.movesLayerName.append(layerItem.assignProps)
            elif(type(layerItem) is TextLayer):
                if layerItem.dataframe is not None:
                    self.movesbasedataframe = layerItem.dataframe
                self.movesLayerName.append(layerItem.layerName)
                self.movesLayerName.append(layerItem.assignProps)
            elif(type(layerItem) is Heatmap3dLayer):
                if layerItem.dataframe is not None:
                    self.movesbasedataframe = layerItem.dataframe
                self.movesLayerName.append(layerItem.layerName)
                self.movesLayerName.append(layerItem.assignProps)
            elif(type(layerItem) is DepotsLayer):
                if layerItem.dataframe is not None:
                    self.depotsBasedataframe = layerItem.dataframe
                self.depotsLayerName.append(layerItem.layerName)
                self.depotsLayerName.append(layerItem.assignProps)
            else:
                print("HvDeck.setLayer : Unsupported data!")

    def setViewport(self,viewport=None):
        if(type(viewport) is dict):
            self.viewport = json.dumps(viewport,ensure_ascii=False)
        else:
            print("HvDeck.setViewport : Unsupported data!")

    def setProperty(self,property=None):
        if(type(property) is dict):
            self.property = json.dumps(property,ensure_ascii=False)
        else:
            print("HvDeck.setProperty : Unsupported data!")

    def display(self,width="100%",height=600,orbitViewSw=False):
        if(type(orbitViewSw) is not bool):
            print("HvDeck.display : Unsupported data!")
        html_str = render_json_to_html(
            self.widgetCdnPath,
            self.mapboxApiKey,
            self.movesLayerName,
            self.movesbasedataframe,
            self.depotsLayerName,
            self.depotsBasedataframe,
            self.viewport,
            self.property,
            orbitViewSw
            )
        srcdoc = html.escape(html_str)
        iframe = f"""<iframe width={width} height={height} frameborder="0" srcdoc="{srcdoc}"></iframe>"""
        return HTML(iframe)

    def to_html(self,filename='Sample.html',orbitViewSw=False):
        if(type(orbitViewSw) is not bool):
            print("HvDeck.display : Unsupported data!")
        html_str = render_json_to_html(
            self.widgetCdnPath,
            self.mapboxApiKey,
            self.movesLayerName,
            self.movesbasedataframe,
            self.depotsLayerName,
            self.depotsBasedataframe,
            self.viewport,
            self.property,
            orbitViewSw
            )
        with open(filename, "w+", encoding="utf-8") as f:
            f.write(html_str)

class MovesLayer:
    dataframe = None
    layerName = "MovesLayer"
    assignProps = '{}'

    def __init__(self,dataframe=None):
        if dataframe is not None:
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
            print(self.layerName + ".setData : Unsupported data!")

    def setLayaerProps(self,assignProps):
        if(type(assignProps) is dict):
            self.assignProps = json.dumps(assignProps,ensure_ascii=False)
        else:
            print(self.layerName + ".setLayaerProps : Unsupported data!")

class PointCloudLayer(MovesLayer):
    def __init__(self,dataframe=None):
        super().__init__(dataframe)
        self.layerName = "PointCloudLayer"

class TextLayer(MovesLayer):
    def __init__(self,dataframe=None):
        super().__init__(dataframe)
        self.layerName = "TextLayer"

class Heatmap3dLayer(MovesLayer):
    def __init__(self,dataframe=None):
        super().__init__(dataframe)
        self.layerName = "Heatmap3dLayer"

class DepotsLayer:
    dataframe = None
    layerName = "DepotsLayer"
    assignProps = '{}'

    def __init__(self,dataframe=None):
        dataframe = None
        if dataframe is not None:
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
            print(self.layerName + ".setData : Unsupported data!")

    def setLayaerProps(self,assignProps):
        if(type(assignProps) is dict):
            self.assignProps = json.dumps(assignProps,ensure_ascii=False)
        else:
            print(self.layerName + ".setLayaerProps : Unsupported data!")
