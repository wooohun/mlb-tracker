'use client'

import RadarGraph from "./radar-graph"
import React, { useState } from 'react'
import styles from './visuals.module.css'
import Dropdown from "./dropdown"
import PieGraph from "./pie-graph"

export default function PitchSplits({displayType, children}) {
    const data = children.sort((a, b) => b.year - a.year)

    const years = data.map((season) => season.year)
    const [season, setSeason] = useState(data[0].year)
    const [graphData, setGraphData] = useState(getSeason(season))

    function changeSeason(year) {
        setSeason(year);
        changeData();
    }
    function changeData(){
        setGraphData(getSeason(season));
    }
    function getSeason(year) {
        return data.find((obj) => obj.year == year)
    }

    return (
        <div className={styles.visualsModule}>
            <div className={styles.visualsModuleHeader}>
                <Dropdown cur_year={season} onClick={changeSeason}>{years}</Dropdown>
                <div className='text-center p-0.5'>
                    Pitch Splits
                </div>
            </div>
            <div className={styles.visualsContainer}>
                <div className={styles.graphContainer}>
                    <RadarGraph
                        displayType={displayType} 
                        statcast={graphData}
                    />
                </div>
                <div className={styles.graphContainer}>
                    <PieGraph
                        displayType={displayType}
                        statcast={graphData}
                    />
                </div>
            </div>
        </div>
    )
}