CANVAS_SRC = """<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">

      function parseTimestamp(data) {
        const datePattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/;
        for (let i = 0; i < data.length; i++) {
          for (let j = 0; j < data[i].length; j++) {
            timeStr = data[i][j];
            if (datePattern.test(timeStr)) {
              data[i][j] = new Date(timeStr);
            }
          }
        }
        return data;
      }

      google.charts.load("current", {"packages":["corechart"]});
      google.charts.setOnLoadCallback(drawChart);
      function drawChart() {
\u1234chart_function\u4321
      }
    </script>
  </head>
  <body>
\u1234chart_div\u4321
  </body>
</html>"""


CHART_FUNCTION_SRC = """
        var data\u1234chart_id\u4321 = google.visualization.arrayToDataTable(parseTimestamp(\u1234data\u4321));
        var options\u1234chart_id\u4321 = {
          title: "\u1234title\u4321",
          hAxis: {
            slantedText: false
          },
          \u1234options\u4321
        };
        var chart\u1234chart_id\u4321 = new google.visualization.\u1234chart_type\u4321(document.getElementById("chart\u1234chart_id\u4321"));
        chart\u1234chart_id\u4321.draw(data\u1234chart_id\u4321, options\u1234chart_id\u4321);
"""

CHART_DIV_SRC = """
    <div id="chart\u1234chart_id\u4321" style="height: \u1234height\u4321px;"></div>
"""
