def getHtml():
    html_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <title>pyharmovis</title>
        <script type="text/javascript" src="{{widgetCdnPath}}"></script>
    </head>
    <body>
        <div id="app">
        </div>
        <script>
            const mapboxApiKey = "{{mapboxApiKey}}"
            {% if movesbase %}const movesbase = {{movesbase}};{% endif %}
            {% if depotsBase %}const depotsBase = {{depotsBase}};{% endif %}
            {% if viewport %}const viewport = {{viewport}};{% endif %}
            const container = document.getElementById('app')
            const widget = new HarmoVisWidget()
            widget.create({
                container,
                mapboxApiKey,
                {% if movesbase %}movesbase,{% endif %}
                {% if depotsBase %}depotsBase,{% endif %}
                {% if viewport %}viewport,{% endif %}
            })
        </script>
    </body>
    </html>
    """
    return html_str
