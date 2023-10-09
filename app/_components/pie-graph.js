'use-client'

import { Chart } from "chart.js/auto"
import { useEffect, useRef } from "react"

function updateData(chart, label, newData) {
    removeData(chart);
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(newData);
    })
    chart.update();
}

function removeData(chart){
    chart.data.labels.pop();
    chart.data.datasets.forEach((dataset) => {
        dataset.data.pop();
    })
}

export default function PieChart( {children} ) {
    const data = children

    const pitchLabels = []
    const pitchData = []
    const bgColor = []
    for (let pitch in data) {
        pitchLabels.push(pitch.type)
        pitchData.push(pitch.release_speed.count)
        const randomColor = Math.floor(Math.random()*16777215).toString(16)
        bgColor.push('#' + randomColor)
    }

    const config = {
        label: pitchLabels,
        datasets: [{
            data: pitchData,
            backgroundColor: bgColor,
            hoverOffset: 4
        }],
        borderWidth: 1
    }
    const canvas = useRef()

    useEffect(() => {
        const ctx = canvas.current;

        let chartStatus = Chart.getChart('myChart')
        if (chartStatus != undefined) {
            chartStatus.destroy();
        }

        const chart = new Chart(ctx, {
            type: 'pie',
            data: config,
            options: {
                responsive: true,

            }
        })
    })

    return (
        <div className="pieChartContainer">
            <canvas ref={canvas}></canvas>
        </div>
    )
}