import PlayerHeader from "./player-header"
import styles from './player-card.module.css'

export default function PlayerCard( {children} ) {
    const data = children
    var displayFocus = 'batting'
    if (data.primary_position.includes('P')) {
        displayFocus = 'pitching'
    }

    const batting_standard = [
        'Team',
        'Age',
        'G',
        'PA',
        'AB',
        'AVG',
        'OBP',
        'SLG',
        'HR',
        'SO',
        'SB'
    ]

    const pitch_standard = [
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
        <div className='border-black border-2'>
            <PlayerHeader>{data}</PlayerHeader>
            <div className='table w-full'>
                <table className={styles.playerSummaryTable}>
                    <thead>
                        <tr className={styles.playerSummaryTableHeader}>
                            {Object.keys(data.seasons[0][displayFocus]['standard']).map((k, idx) => (
                                <th key={idx} className={styles.playerSummaryTableHeaderBox}>{k}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.seasons.map((season) => (
                            <tr key={season.year} className={styles.playersummaryTableRow}>
                                {Object.values(season[displayFocus]['standard']).map((metric, idx) => (
                                    <td key={idx} className={styles.playerSummaryTableBox}>{metric}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}