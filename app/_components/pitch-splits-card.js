'use client'

import React, { useState, useEffect, useCallback } from 'react'
import styles from './visuals.module.css'
import Dropdown from "./dropdown"
import PieGraph from "./pie-graph"
import StrikeZoneGraph from "./strike-zone-graph"
import RadarGraph from "./radar-graph"
import RankingGraph from './ranking-graph'

export default function PitchSplits({displayType, children}) {
    const statcast = children['statcast'].sort((a, b) => b.year - a.year)
    const strikeZone = children['coordinates'].sort((a, b) => b.year - a.year)
    const ranks = children['ranking'].sort((a, b) => b.year - a.year)
    const years = statcast.map((season) => season.year)
    
    const [season, setSeason] = useState(years[0])
    const [graphData, setGraphData] = useState(getStatcast(season))
    const [coordData, setCoordData] = useState(getCoords(season))
    const [rankingData, setRankingData] = useState(getRanks(season))

    function changeData(year) {
        setSeason(year);
        setGraphData(getStatcast(year));
        setCoordData(getCoords(year));
        setRankingData(getRanks(year))
    }

    function getStatcast(year) {
        return statcast.find((obj) => obj.year == year)
    }
    function getCoords(year) {
        return strikeZone.find((obj) => obj.year == year)
    }
    function getRanks(year) {
        return ranks.find((obj) => obj.year == year)
    }

    return (
        <div className={styles.visualsModule}>
            <div className={styles.visualsModuleHeader}>
                <Dropdown cur_year={season} onClick={changeData}>{years}</Dropdown>
                <div className='text-center p-0.5'>
                    Pitch Splits
                </div>
            </div>
            <div className={styles.visualsContainer}>
                <div className={styles.graphContainer}>
                    <PieGraph
                        displayType={displayType}
                        statcast={graphData}
                    />
                </div>
                <div className={styles.graphContainer}>
                    <RankingGraph
                        displayType={displayType}
                        rankings={rankingData}
                    />
                </div>
                <div className={styles.graphContainer}>
                    <RadarGraph
                        displayType={displayType} 
                        statcast={graphData}
                    />
                </div>
                <div className={styles.graphContainer}>
                    <StrikeZoneGraph
                        displayType={displayType}
                        coords={coordData}
                    />
                </div>
            </div>
        </div>
    )
}