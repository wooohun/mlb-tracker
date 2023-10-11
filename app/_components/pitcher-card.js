import PlayerHeader from "./player-header"
import styles from './player-card.module.css'

export default function PitcherCard( {children} ) {
    const data = children

    const summary = [
        'Team',
        'Age',
        'W',
        'L',
        'ERA',
        'G',
        'GS',
        'IP',
        'SO',
        'WHIP',
        'WAR'
    ]

    return (
        <div className='m-2'>
            <PlayerHeader>{data}</PlayerHeader>
            <div className='table w-full mt-2'>
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
                        {data.seasons.map((season) => (
                            <tr key={season.year} className={styles.playerSummaryTableRow}>
                                <td className={styles.playerSummaryTableBox}>{season.year}</td>
                                {summary.map((metric) => (
                                    <td key={metric} className={styles.playerSummaryTableBox}>{season['pitching']['standard'][metric]}</td>
                                ))}
                            </tr>
                        ))}
                        <tr className={styles.playerSummaryOverallStats}>
                            <td className={styles.playerSummaryTableBox}></td>
                            <td className={styles.playerSummaryTableBox}></td>
                            <td className={styles.playerSummaryTableBox}></td>
                            {summary.map((metric) => {
                                if (Object.keys(data.averages['pitching']).includes(metric)){
                                    return (
                                        <td key={metric} className={styles.playerSummaryTableBox}>{data.averages['pitching'][metric]}</td>
                                    )
                                }
                            })}
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    )
}