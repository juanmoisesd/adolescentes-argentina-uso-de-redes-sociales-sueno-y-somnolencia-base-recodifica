document.addEventListener('DOMContentLoaded', function() {
    const DATA_URL = 'data/analysis_ready/dataset.csv';

    Papa.parse(DATA_URL, {
        download: true,
        header: true,
        dynamicTyping: true,
        complete: function(results) {
            const data = results.data.filter(d => d.id !== null);
            renderCharts(data);
        },
        error: function(err) {
            console.error("Error loading CSV:", err);
            // Fallback to static demo if CSV fails to load (common in local preview)
            const demoData = generateDemoData();
            renderCharts(demoData);
        }
    });
});

function renderCharts(data) {
    // 1. Sleep Duration Distribution
    const sleepLabels = ['<6h', '6-7h', '7-8h', '8-9h', '>9h'];
    const sleepCounts = [0, 0, 0, 0, 0];
    data.forEach(d => {
        if (d.sleep_duration < 6) sleepCounts[0]++;
        else if (d.sleep_duration < 7) sleepCounts[1]++;
        else if (d.sleep_duration < 8) sleepCounts[2]++;
        else if (d.sleep_duration < 9) sleepCounts[3]++;
        else sleepCounts[4]++;
    });

    new Chart(document.getElementById('sleepDistChart'), {
        type: 'bar',
        data: {
            labels: sleepLabels,
            datasets: [{
                label: 'Estudiantes',
                data: sleepCounts,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 1
            }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });

    // 2. Screen Use Distribution
    const screenLabels = ['0-2h', '2-4h', '4-6h', '6-8h', '>8h'];
    const screenCounts = [0, 0, 0, 0, 0];
    data.forEach(d => {
        if (d.screen_use < 2) screenCounts[0]++;
        else if (d.screen_use < 4) screenCounts[1]++;
        else if (d.screen_use < 6) screenCounts[2]++;
        else if (d.screen_use < 8) screenCounts[3]++;
        else screenCounts[4]++;
    });

    new Chart(document.getElementById('screenDistChart'), {
        type: 'pie',
        data: {
            labels: screenLabels,
            datasets: [{
                data: screenCounts,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)'
                ]
            }]
        },
        options: { responsive: true }
    });

    // 3. Sleep vs Performance (Scatter)
    const scatterData = data.map(d => ({ x: d.sleep_duration, y: d.academic_performance }));
    new Chart(document.getElementById('sleepPerformanceChart'), {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Relación Sueño/Nota',
                data: scatterData,
                backgroundColor: 'rgba(255, 99, 132, 1)'
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Horas de Sueño' } },
                y: { title: { display: true, text: 'Rendimiento (1-10)' } }
            }
        }
    });

    // 4. Screen vs Sleep (Trend)
    // Sort data by screen use for a better trend visualization or just use scatter
    const screenSleepData = data.map(d => ({ x: d.screen_use, y: d.sleep_duration }));
    new Chart(document.getElementById('screenSleepChart'), {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Uso Pantalla vs Sueño',
                data: screenSleepData.map(d => ({ ...d, r: 8 })),
                backgroundColor: 'rgba(153, 102, 255, 0.6)'
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Horas Pantalla' } },
                y: { title: { display: true, text: 'Horas Sueño' } }
            }
        }
    });
}

function generateDemoData() {
    // Just in case CSV isn't available during testing/local
    return Array.from({ length: 20 }, (_, i) => ({
        id: i,
        sleep_duration: 5 + Math.random() * 5,
        screen_use: Math.random() * 10,
        academic_performance: 4 + Math.random() * 6
    }));
}
