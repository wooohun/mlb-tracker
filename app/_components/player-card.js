'use client'

import PlayerHeader from "./player-header"
import * as ENUMS from '../enums'
import styles from './player-card.module.css'
import { useState } from "react"


export default function PlayerCard({setPageType, displayType, children}) {

    const summary = displayType == 'batting' ? ENUMS.batSummaryMetrics : ENUMS.pitchSummaryMetrics
    const playerRoles = Object.keys(children.averages)

    const [summaryData, setSummaryData] = useState(children[displayType])

    function handlePageTypeChange(e) {
        let target = e.target.innerHTML
        setPageType(target)
        setSummaryData(children[displayType])
    }

    return (
        <div className='m-2 flex flex-wrap flex-col'>
            <PlayerHeader>{children}</PlayerHeader>
            <div className='table w-full'>
                <table className={styles.playerSummaryTable}>
                    <thead>
                        <tr className={styles.playerSummaryTableHeader}>
                            <th className={styles.playerSummaryTableHeaderBox}>Season</th>
                            {summary.map((k, idx) => (
                                <th key={idx} className={styles.playerSummaryTableHeaderBox}>{k}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {children.seasons.map((season) => (
                            <tr key={season.year} className={styles.playerSummaryTableRow}>
                                <td className={styles.playerSummaryTableBox}>{season.year}</td>
                                {summary.map((metric) => (
                                    <td key={metric} className={styles.playerSummaryTableBox}>{season[displayType]['standard'][metric]}</td>
                                ))}
                            </tr>
                        ))}
                        <tr className={styles.playerSummaryOverallStats}>
                            <td className={styles.playerSummaryTableBox}>{children.seasons.length} Total </td>
                            <td className={styles.playerSummaryTableBox}>Seasons:</td>
                            <td className={styles.playerSummaryTableBox}></td>
                            {summary.map((metric) => {
                                if (Object.keys(children.averages[displayType]).includes(metric)){
                                    return (
                                        <td key={metric} className={styles.playerSummaryTableBox}>{children.averages[displayType][metric]}</td>
                                    )
                                }
                            })}
                        </tr>
                    </tbody>
                </table>
            </div>
            <div className="flex flex-row justify-evenly my-7">
                {playerRoles.map((role) => (
                    <div className="py-1 px-4 border-black border flex flex-initial">
                        <button
                            onClick={handlePageTypeChange}
                        >
                            {role}
                        </button>
                    </div>    
                ))}
            </div>
        </div>
    )
}