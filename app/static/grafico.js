google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);


/*
source.addEventListener("in-progress", function(event){
    chart_data = event.data.split(",").map(Number);
    var i;
    pres[0] = chart_data[0];
    pres[1] = chart_data[1];
    pres[2] = chart_data[2];
    temp[0] = chart_data[0];
    temp[1] = chart_data[3];
    humi[0] = chart_data[0];
    humi[1] = chart_data[4];
    data1.addRow(pres);
    data2.addRow(temp);
    data3.addRow(humi);
    var chart1 = new google.visualization.LineChart(document.getElementById('curve_chart1'));
    chart1.draw(data1, options1);
    var chart2 = new google.visualization.LineChart(document.getElementById('curve_chart2'));
    chart2.draw(data2, options2);
    var chart3 = new google.visualization.LineChart(document.getElementById('curve_chart3'));
    chart3.draw(data3, options3);
    if (data1.og["length"]>50){
        data1.removeRow(1)
        data2.removeRow(1)
        data3.removeRow(1)
    }
});
*/

function drawChart() {
    data1 = new google.visualization.DataTable();
    data2 = new google.visualization.DataTable();
    data3 = new google.visualization.DataTable();
    data1.addColumn('date', 'tempo');
    data1.addColumn('number', 'sensor');
    data1.addColumn('number', 'setpoint');
    data2.addColumn('date', 'tempo');
    data2.addColumn('number', '°C');
    data3.addColumn('date', 'tempo');
    data3.addColumn('number', '%');
    options1 = {
        pointSize: 2,
        //width: 700,
        //height: 200,
        hAxis: {
            title: 'Tempo',
            gridlines: {
              count: -1
            }
        },
        vAxis: {
            title: 'mBar',
            ticks: [920,935,950,965,980]
        },
        title: "Gráfico da Pressão",
        crosshair: {
            color: '#000',
            trigger: 'selection'
        },
        legend: {position:"top"}
    };
    options2 = {
        pointSize: 2,
        hAxis: {
            title: 'Tempo',
            gridlines: {
              count: -1
            }
        },
        vAxis: {
            title: '°C',
            ticks: [0, 10, 20, 30, 40]
        },
        //width: 700,
        //height: 200,
        title: "Gráfico da Temperatura",
        crosshair: {
            color: '#000',
            trigger: 'selection'
        },
        legend: {position:"top"}
    };
    options3 = {
        pointSize: 2,
        hAxis: {
            title: 'Tempo',
            gridlines: {
              count: -1
            }
        },
        vAxis: {
            title: '#',
            ticks: [10, 30, 50, 70, 90]
        },
        //width: 700,
        //height: 200,
        title: "Gráfico da Umidade",
        crosshair: {
            color: '#000',
            trigger: 'selection'
        },
        legend: {position:"top"}
    };
    var chart1 = new google.visualization.LineChart(document.getElementById('curve_chart1'));
    var chart2 = new google.visualization.LineChart(document.getElementById('curve_chart2'));
    var chart3 = new google.visualization.LineChart(document.getElementById('curve_chart3'));
    chart1.draw(data1, options1);
    chart2.draw(data2, options2);
    chart3.draw(data3, options3);
    var nome = $("#nm").val()
    if (nome == "parado"){
        $.post('http://127.0.0.1:5000/_get_grafico_ponto',{
            nome:nome
        }, function(data) {
            graf=JSON.parse(data);
            pres[0] = new Date(graf[0]["data_registro"]);
            pres[1] = parseFloat(graf[0]["pressao"]);
            pres[2] = parseFloat(graf[0]["setpoint"]);
            temp[0] = new Date(graf[0]["data_registro"]);
            temp[1] = parseFloat(graf[0]["temperatura"]);
            humi[0] = new Date(graf[0]["data_registro"]);
            humi[1] = parseFloat(graf[0]["UR"]);
            data1.addRow(pres);
            data2.addRow(temp);
            data3.addRow(humi);
            var chart1 = new google.visualization.LineChart(document.getElementById('curve_chart1'));
            chart1.draw(data1, options1);
            var chart2 = new google.visualization.LineChart(document.getElementById('curve_chart2'));
            chart2.draw(data2, options2);
            var chart3 = new google.visualization.LineChart(document.getElementById('curve_chart3'));
            chart3.draw(data3, options3);
        });
    } else {
        $.post('http://127.0.0.1:5000/_get_grafico',{
            nome:nome
        }, function(data) {
            graf=JSON.parse(data);
            for(var i=0 in graf.length) {
                pres[0] = new Date(graf[i]["data_registro"]);
                pres[1] = parseFloat(graf[i]["pressao"]);
                pres[2] = parseFloat(graf[i]["setpoint"]);
                temp[0] = new Date(graf[i]["data_registro"]);
                temp[1] = parseFloat(graf[i]["temperatura"]);
                humi[0] = new Date(graf[i]["data_registro"]);
                humi[1] = parseFloat(graf[i]["UR"]);
                data1.addRow(pres);
                data2.addRow(temp);
                data3.addRow(humi);
            }
            var chart1 = new google.visualization.LineChart(document.getElementById('curve_chart1'));
            chart1.draw(data1, options1);
            var chart2 = new google.visualization.LineChart(document.getElementById('curve_chart2'));
            chart2.draw(data2, options2);
            var chart3 = new google.visualization.LineChart(document.getElementById('curve_chart3'));
            chart3.draw(data3, options3);
        });
    }
}