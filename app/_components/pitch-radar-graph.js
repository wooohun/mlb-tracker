'use client'
import {
    Chart,
    RadialLinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
    Legend,
  } from 'chart.js';
import { Radar } from "react-chartjs-2";
import * as ENUMS from '../enums';

Chart.register(
    RadialLinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
    Legend
);

export default function PitchRadarGraph({displayType, statcast}) {
    const data = statcast
      
    const datasets = []
    for (const [p_type, p_data] of Object.entries(data[displayType]['pitch_types'])) {
        var metric_data = []
        if (Object.keys(p_data).includes('normalized')) {
            for (const [metric, val] of Object.entries(p_data['normalized'])){
                if (Object.keys(ENUMS.pitch_labels).includes(metric)){
                    metric_data.push([ENUMS.pitch_labels[metric], val])
                }
            }
        }
        datasets.push([p_type, Object.fromEntries(metric_data)])
    }

    const graphConfig = {
        scales: {
            r: {
                type: 'radialLinear',
                axis: 'r',
                angleLines: {
                    display: false,
                },
                min: 0.0,
                max: 1.0,
                pointLabels: {
                    padding: 5,
                },
                ticks: {
                    count: 5,
                    stepSize: 0.2
                }
            }
        }
    }

    const graphData = []
    for (const [p_type, p_data] of datasets){
        var dataset = {
            label: ENUMS.pitchTypes[p_type],
            data: Object.values(p_data),
            fill: true,
            backgroundColor: ENUMS.graphColors[p_type][1],
            borderColor: ENUMS.graphColors[p_type][0],
            borderWidth: 2,
            pointBackgroundColor: ENUMS.graphColors[p_type][0],
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: ENUMS.graphColors[p_type][0],
        }
        console.log(dataset)
        graphData.push(dataset)
    }

    const finalData = {
        labels: Object.values(ENUMS.pitch_labels),
        datasets: graphData
    }

    return (
        <Radar
            datasetIdKey='id' 
            data={finalData}
            options={graphConfig}
        />
    )
}