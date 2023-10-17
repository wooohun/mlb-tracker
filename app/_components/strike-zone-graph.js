import React from 'react';
import {
  Chart as ChartJS,
  LinearScale,
  CategoryScale,
  PointElement,
  LineElement,
  Legend,
  Tooltip,
  LineController,
  BarController,
} from 'chart.js';
import { Chart } from 'react-chartjs-2';
import * as ENUMS from '../enums'
import styles from './visuals.module.css'

ChartJS.register(
    LinearScale,
    CategoryScale,
    PointElement,
    LineElement,
    Legend,
    Tooltip,
    LineController,
    BarController
  );

export default function StrikeZoneGraph({displayType, coords}) {
    
    const datasets = Object.entries(coords[displayType]['pitch_types'])
    const sz_dim = coords[displayType]['sz_dim']


    const graphData = [
        {
            type: 'line',
            label: '',
            data: [
                {x: sz_dim['top'], y: sz_dim['left']},
                {x: sz_dim['top'], y: sz_dim['right']},
                {x: sz_dim['bot'], y: sz_dim['right']},
                {x: sz_dim['bot'], y: sz_dim['left']}
            ],
            borderColor: 'rgb(0, 0, 0)',
            borderWidth: 2,
            fill: true
        }
    ]
    for (const [p_type, p_data] of datasets) {
        var data = {
            type: 'scatter',
            label: ENUMS.pitchTypes[p_type],
            data: p_data,
            backgroundColor: ENUMS.graphColors[p_type],
            
        }
        graphData.push(data)
    }

    return (
        <div className={styles.graph}>
            <Chart
                type='scatter'
                data={graphData}
                updateMode='resize'
            />
        </div>
    )
}