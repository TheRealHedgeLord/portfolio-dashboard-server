GOOGLE_CHART_HTML = """<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable(\u1234data\u4321);
        var options = {
          title: '\u1234title\u4321',
          hAxis: {textPosition: 'none'},
          \u1234options\u4321
        };
        var chart = new google.visualization.\u1234chart_type\u4321(document.getElementById('chart'));
        chart.draw(data, options);
      }
    </script>
  </head>
  <body>
    <div id="chart" style="height: \u1234height\u4321px;"></div>
  </body>
</html>"""

CANVAS_SRC = """<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
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
        var data\u1234chart_id\u4321 = google.visualization.arrayToDataTable(\u1234data\u4321);
        var options\u1234chart_id\u4321 = {
          title: "\u1234title\u4321",
          hAxis: {textPosition: "none"},
          \u1234options\u4321
        };
        var chart\u1234chart_id\u4321 = new google.visualization.\u1234chart_type\u4321(document.getElementById("chart\u1234chart_id\u4321"));
        chart\u1234chart_id\u4321.draw(data\u1234chart_id\u4321, options\u1234chart_id\u4321);
"""

CHART_DIV_SRC = """
    <div id="chart\u1234chart_id\u4321" style="height: \u1234height\u4321px;"></div>
"""
