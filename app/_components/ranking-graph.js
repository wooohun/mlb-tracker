import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import Annotation from 'chartjs-plugin-annotation';
import * as ENUMS from '../enums';
import styles from './visuals.module.css';


ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    Annotation
  );

export default function RankingGraph( {displayType, rankings}) {

    const data = Object.values(rankings[displayType]).map((metric) => metric.rank)
    const vals = Object.values(rankings[displayType]).map((metric) => metric.value)
    const labels = Object.keys(rankings[displayType]).map((metric) => Object.keys(ENUMS.rankMetrics).includes(metric) ? ENUMS.rankMetrics[metric] : metric)

    const graphData = [{
        label: '',
        data: data,
        backgroundColor: function(context){
            console.log(context)
            let res = [];
            for (let i = 0; i < context.dataset.data.length; i++) {
                const val = context.dataset.data[i]

                const h = (255 * (100 - val)) / 100

                res.push(`hsl(${h}, 100%, 58%)`)
            }

            return res
        },
        borderWidth: 1,

    }]
    const graphConfig = {
        indexAxis: 'y',
        barPercentage: .75,
        aspectRatio: 1,
        scales: {
            beginAtZero: true,
            x: {
                ticks: {
                    count: 5,
                    callback: function(value, index, ticks) {
                        let res;
                        if (value == 100) {
                            res = 'Amazing'
                        } else if (value == 75) {
                            res = 'Great'
                        } else if (value == 50 ) {
                            res = 'Good'
                        } else if (value == 25) {
                            res = 'Ok'
                        } else {
                            res = 'Poor'
                        }
                        return res;
                    },
                },
                border: {
                    display: false
                }
            },
            y: {
                grid: {
                    display: false
                },
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks:{
                    label: function(context) {
                        let idx = context.parsed.y
                        let label = labels[idx]

                        let res;
                        if (label) {
                            if (label.includes('%')){
                                let rounded = Math.round(vals[idx] * 1000) / 10
                                res = parseFloat(rounded.toFixed(2))
                            } else {
                                res = vals[idx]
                            }
                        }
                        return res
                    }
                }
            }
        }
    }
    const finalData = {
        labels: labels,
        datasets: graphData,
    }
    return (
        <div className={styles.rankGraph}>
            <Bar
                updateMode='resize'
                data={finalData}
                options={graphConfig}
            />
        </div>
    )
}