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
            if(type(layerItem) is MovesLayer or
               type(layerItem) is PointCloudLayer or
               type(layerItem) is TextLayer or
               type(layerItem) is Heatmap3dLayer or
               type(layerItem) is Heatmap2dLayer or
               type(layerItem) is ScatterplotLayer or
               type(layerItem) is GridCellLayer or
               type(layerItem) is ColumnLayer or
               type(layerItem) is PolygonLayer or
               type(layerItem) is SimpleMeshLayer or
               type(layerItem) is ArcLayer):
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

def transData(sourceData,transParams={}):
    resultData = sourceData
    if "positionkey" in transParams:
        positionkey = transParams["positionkey"]
        if positionkey in resultData:
            positionData = resultData.pop(positionkey)
            resultData["position"] = positionData
    elif "long_x_key" in transParams and "lati_y_key" in transParams:
        long_x_key = transParams["long_x_key"]
        lati_y_key = transParams["lati_y_key"]
        if long_x_key in resultData and lati_y_key in resultData:
            long_x_Data = resultData.pop(long_x_key)
            lati_y_Data = resultData.pop(lati_y_key)
            height_z_Data = 0
            if "height_z_key" in transParams:
                height_z_key = transParams["height_z_key"]
                if height_z_key in resultData:
                    height_z_Data = resultData.pop(height_z_key)
            resultData["position"] = [long_x_Data,lati_y_Data,height_z_Data]
    if "elapsedtimekey" in transParams:
        elapsedtimekey = transParams["elapsedtimekey"]
        if elapsedtimekey in resultData:
            elapsedtimeData = resultData.pop(elapsedtimekey)
            resultData["elapsedtime"] = elapsedtimeData
    return resultData

class MovesLayer:
    dataframe = None
    layerName = "MovesLayer"
    assignProps = '{}'

    def __init__(self,dataframe=None,transParams={}):
        if dataframe is not None:
            self.setData(dataframe,transParams)

    def setData(self,dataframe=None,transParams={}):
        if(type(transParams) is not dict):
            print(self.layerName + ".setData : Unsupported transParams!")
            return
        if dataframe is None:
            self.assignProps = json.dumps(transParams,ensure_ascii=False)
        elif (type(dataframe) is pandas.core.frame.DataFrame):
            json_str = "["
            for num1 in range(len(dataframe.index)):
                json_str += """{"operation":["""
                for num2 in range(len(dataframe.columns)):
                    if dataframe[num2][num1] != None:
                        json_str += json.dumps(transData(dataframe[num2][num1],transParams)) + ","
                json_str += "]},"
            json_str += "]"
            self.dataframe = json_str
            self.assignProps = json.dumps(transParams,ensure_ascii=False)
        elif(type(dataframe) is str):
            r = requests.get(dataframe)
            fileData = json.loads(r.text)
            for lineData in fileData:
                if "operationkey" in transParams:
                    operationkey = transParams["operationkey"]
                    if operationkey in lineData:
                        operationData = lineData.pop(operationkey)
                        lineData["operation"] = operationData
                    operationData = lineData["operation"]
                    for posData in operationData:
                        posData = transData(posData,transParams)
            self.dataframe = json.dumps(fileData)
            self.assignProps = json.dumps(transParams,ensure_ascii=False)
        elif(type(dataframe) is list):
            fileData = dataframe
            for lineData in fileData:
                if "operationkey" in transParams:
                    operationkey = transParams["operationkey"]
                    if operationkey in lineData:
                        operationData = lineData.pop(operationkey)
                        lineData["operation"] = operationData
                    operationData = lineData["operation"]
                    for posData in operationData:
                        posData = transData(posData,transParams)
            self.dataframe = json.dumps(fileData)
            self.assignProps = json.dumps(transParams,ensure_ascii=False)
        else:
            print(self.layerName + ".setData : Unsupported dataframe!")

    def setLayaerProps(self,assignProps):
        if(type(assignProps) is dict):
            self.assignProps = json.dumps(assignProps,ensure_ascii=False)
        else:
            print(self.layerName + ".setLayaerProps : Unsupported assignProps!")

class PointCloudLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "PointCloudLayer"

class TextLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "TextLayer"

class Heatmap3dLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "Heatmap3dLayer"

class Heatmap2dLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "Heatmap2dLayer"

class ScatterplotLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "ScatterplotLayer"

class GridCellLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "GridCellLayer"

class ColumnLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "ColumnLayer"

class PolygonLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "PolygonLayer"

class SimpleMeshLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "SimpleMeshLayer"

class ArcLayer(MovesLayer):
    def __init__(self,dataframe=None,transParams={}):
        super().__init__(dataframe,transParams)
        self.layerName = "ArcLayer"

class DepotsLayer:
    dataframe = None
    layerName = "DepotsLayer"
    assignProps = '{}'

    def __init__(self,dataframe=None,transParams={}):
        dataframe = None
        if dataframe is not None:
            self.setData(dataframe,transParams)

    def setData(self,dataframe,transParams={}):
        if(type(transParams) is not dict):
            print(self.layerName + ".setData : Unsupported transParams!")
            return
        if dataframe is None:
            self.assignProps = json.dumps(transParams,ensure_ascii=False)
        elif (type(dataframe) is pandas.core.frame.DataFrame):
            json_str = "["
            dataframeDic = dataframe.to_dict(orient='records')
            for dicElement in dataframeDic:
                json_str += json.dumps(transData(dicElement,transParams)) + ","
            json_str += "]"
            self.dataframe = json_str
            self.assignProps = json.dumps(transParams,ensure_ascii=False)
        elif(type(dataframe) is str):
            r = requests.get(dataframe)
            fileData = json.loads(r.text)
            for lineData in fileData:
                lineData = transData(lineData,transParams)
            self.dataframe = json.dumps(fileData)
            self.assignProps = json.dumps(transParams,ensure_ascii=False)
        elif(type(dataframe) is list):
            fileData = dataframe
            for lineData in fileData:
                lineData = transData(lineData,transParams)
            self.dataframe = json.dumps(fileData)
            self.assignProps = json.dumps(transParams,ensure_ascii=False)
        else:
            print(self.layerName + ".setData : Unsupported dataframe!")

    def setLayaerProps(self,assignProps):
        if(type(assignProps) is dict):
            self.assignProps = json.dumps(assignProps,ensure_ascii=False)
        else:
            print(self.layerName + ".setLayaerProps : Unsupported assignProps!")
