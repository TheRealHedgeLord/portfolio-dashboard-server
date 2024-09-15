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
          hAxis: {textPosition: 'none'}
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
