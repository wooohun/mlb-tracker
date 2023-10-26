'use client'

import PlayerHeader from "./player-header"
import * as ENUMS from '../enums'
import styles from './player-card.module.css'

export default function PlayerCard({setPageType, displayType, children}) {

    const summary = displayType == 'batting' ? ENUMS.batSummaryMetrics : ENUMS.pitchSummaryMetrics
    const playerRoles = Object.keys(children.averages)

    function handlePageTypeChange(e) {
        let target = e.target.innerHTML
        setPageType(target)
    }

    return (
        <div className='m-2 flex flex-wrap flex-col'>
            <PlayerHeader>{children}</PlayerHeader>
            <div className='table w-full'>
                <table className={styles.playerSummaryTable}>
                    <thead>
                        <tr key='headerRow' className={styles.playerSummaryTableHeader}>
                            <th key='header-start' className={styles.playerSummaryTableHeaderBox}>Season</th>
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
                            <td key='filler' className={styles.playerSummaryTableBox}>{children.seasons.length} Total </td>
                            <td key='filler' className={styles.playerSummaryTableBox}>Seasons:</td>
                            <td key='filler' className={styles.playerSummaryTableBox}></td>
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