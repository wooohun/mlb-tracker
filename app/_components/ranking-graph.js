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
import * as ENUMS from '../enums';
import styles from './visuals.module.css';


ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
  );

export default function RankingGraph( {displayType, rankings}) {

    const metric_labels = displayType == 'pitching' ? ENUMS.pitchRankMetrics : ENUMS.batRankMetrics

    const data = Object.entries(rankings[displayType]).map((metric) => metric.rank)
    const labels = Object.keys(rankings[displayType]).map((metric) => metric_labels[metric])


    let width, height, gradient;
    function getGradient(ctx, chartArea) {
        const chartWidth = chartArea.right - chartArea.left;
        const chartHeight = chartArea.top - chartArea.bottom;

        if (!gradient || width !== chartWidth || height !== chartHeight) {
            width = chartWidth
            height = chartHeight

            gradient = ctx.createLinearGradient(0, chartArea.left, 0, chartArea.right);
            gradient.addColorStop(0, '#6495ED');
            gradient.addColorStop(0.25, '#7CFC00');
            gradient.addColorStop(0.5, '#FFFF00');
            gradient.addColorStop(0.75, '#FFAA33');
            gradient.addColorStop(1, '#FF5733');
        }
        return gradient
    }

    const graphData = {
        datasets: [{
            data: data,

        }]
    }

    const graphConfig = {
        indexAxis: 'y',
        barPercentage: .75,
        scales: {
            beginAtZero: true,
        },

    }
    const finalData = {
        labels: labels,
        data: graphData,
    }

    return (
        <div>
            <Bar
                updateMode='resize'
            />
        </div>
    )
}