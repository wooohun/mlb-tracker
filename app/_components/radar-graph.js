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
import styles from './visuals.module.css'
import { useRef } from 'react';

Chart.register(
    RadialLinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
    Legend
);

export default function RadarGraph({displayType, statcast}) {

    const metric_labels = displayType == 'pitching' ? ENUMS.p_metric_labels : ENUMS.b_metric_labels

    const chartRef = useRef()

    const datasets = []
    for (const [p_type, p_data] of Object.entries(statcast[displayType]['pitch_types'])) {
        var metric_data = []
        if (Object.keys(p_data).includes('normalized')) {
            for (const [metric, val] of Object.entries(p_data['normalized'])){
                if (Object.keys(metric_labels).includes(metric)){
                    metric_data.push([metric_labels[metric], {'normalized': val, 'actual': p_data[metric]}])
                }
            }
        }
        datasets.push([p_type, Object.fromEntries(metric_data)])
    }

    const graphConfig = {
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let idx = context.dataIndex
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': '
                        }
                        if (idx !== '') {
                            label += context.dataset.data[idx]['actual']
                        }
                        return label
                    }
                }
            }
        },
        parsing: {
            key: 'normalized'
        },
        scales: {
            r: {
                type: 'radialLinear',
                axis: 'r',
                min: 0.0,
                max: 1.0,
                pointLabels: {
                    padding: 5,
                },
                ticks: {
                    count: 5,
                    stepSize: 0.2,
                    display: false,
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
            pointBorderColor: '#000',
            pointBorderRadius: 1,
            pointBorderWidth: 1,
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: ENUMS.graphColors[p_type][0],
        }
        graphData.push(dataset)
    }

    const finalData = {
        labels: Object.values(metric_labels),
        datasets: graphData
    }

    return (
        <div className={styles.graph}>
            <Radar
                ref={chartRef}
                data={finalData}
                options={graphConfig}
                updateMode='resize'
            />
        </div>
    )
}