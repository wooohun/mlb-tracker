import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';
import * as ENUMS from '../enums'
import styles from './visuals.module.css'

ChartJS.register(ArcElement, Tooltip, Legend);

export default function PieGraph( {displayType, statcast} ) {
    const data = Object.entries(statcast[displayType]['pitch_types']) 

    const dataset = []
    const labels = []
    const bgColor = []
    const borderColor = []

    for (const [p_type, p_vals] of data) {
        dataset.push(p_vals['total'])
        labels.push(ENUMS.pitchTypes[p_type])
        bgColor.push(ENUMS.graphColors[p_type][1])
        borderColor.push(ENUMS.graphColors[p_type][0])
    }

    const graphData = [{
        label: '# of Pitches',
        data: dataset,
        backgroundColor: bgColor,
        borderColor: borderColor,
        borderWidth: 1
    }]

    const finalData = {
        labels: labels,
        datasets: graphData
    }
    return (
        <div className={styles.graph}>
            <Pie
                datasetIdKey='id'
                data={finalData}
                updateMode='resize'
            />
        </div>
    )
}