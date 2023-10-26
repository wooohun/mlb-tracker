'use client'

import React, { useRef } from 'react';
import {
  Chart as ChartJS,
  LinearScale,
  CategoryScale,
  LogarithmicScale,
  PointElement,
  LineElement,
  Legend,
  Tooltip,
  LineController,
} from 'chart.js';
import { Scatter } from 'react-chartjs-2';
import Annotation from 'chartjs-plugin-annotation';
import * as ENUMS from '../enums'
import styles from './visuals.module.css'

ChartJS.register(
    LinearScale,
    CategoryScale,
    LogarithmicScale,
    PointElement,
    LineElement,
    Legend,
    Tooltip,
    LineController,
    Annotation
);


export default function StrikeZoneGraph({displayType, coords}) {
    const datasets = Object.entries(coords[displayType]['pitch_types'])
    const sz_dim = coords[displayType]['sz_dim']
    const graphData = []
    for (const [p_type, p_data] of datasets) {
        var data = {
            label: ENUMS.pitchTypes[p_type],
            data: p_data,
            backgroundColor: ENUMS.graphColors[p_type][0],
        }
        graphData.push(data)
    }
    
    const graphOptions = {
        scales: {
            x: {
                min: -3, 
                max: 3,
                border: {
                    display: false,
                },
                grid: {
                    display: false,
                    drawTicks: false
                },
                ticks: {
                    display: false
                }
            },
            y: {
                min: 0,
                max: 5,
                border: {
                    display: false,
                },
                grid: {
                    display: false,
                    drawTicks: false
                },
                ticks: {
                    display: false
                }
            }
        },
        aspectRatio: 1,
        parsing: false,
        animation: false,
        plugins: {
            annotation: {
                annotations: {
                    box1: {
                        type: 'box',
                        xMin: sz_dim['left'],
                        xMax: sz_dim['right'],
                        yMin: sz_dim['bot'],
                        yMax: sz_dim['top'],
                        backgroundColor: 'rgba(0, 0, 0, 0)',
                        borderWidth: 4,
                    }
                }
            },
            tooltip: {
                enabled: false
            }
        },
        interaction: {
            mode: 'dataset'
        },
        onHover: (e, activeEls, chart) => {
            if (activeEls.length == 0) {
                chart.data.datasets.forEach((dataset, i) => {
                    chart.show(i)
                })
                chart.update();
                return;
            }
            const hoveredEl = chart.getElementsAtEventForMode(e, 'point', {
                intersect: false
            }, true)[0]

            chart.data.datasets.forEach((dataset, i) => {
                if (hoveredEl.datasetIndex == i) {
                    chart.show(i);
                } else {
                    chart.hide(i)
                }
            })
            chart.update();
          },
    }
    const finalData = {
        labels: Object.values(ENUMS.pitchTypes),
        datasets: graphData
    }
    return (
        <div className={styles.graph}>
            <Scatter
                data={finalData}
                updateMode='resize'
                options={graphOptions}
            />
        </div>
    )
}