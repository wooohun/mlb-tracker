import Link from "next/link";
import { convertHeight, dateReformat, getAge } from "../util";
import styles from './player-card.module.css'

export default function PlayerHeader({ children }) {
    const positions = {
        'C': 'Catcher',
        'IF': 'Infield',
        '1B': 'First Base',
        '2B': 'Second Base',
        '3B': 'Third Base',
        'SS': 'Shortstop',
        'OF': 'Outfielder',
        'LF': 'Leftfielder',
        'CF': 'Centerfielder',
        'RF': 'Rightfielder',
        'P': 'Pitcher',
        'RP': 'Relief Pitcher',
        'SP': 'Starting Pitcher',
        'DH': 'Designated Hitter'
    }

    const data = children

    const height = convertHeight(data.ht)['imperial']

    if (data.position == 'IF' || data.position == 'OF') {
        var position = data.position;
    } else {
        var position = data.primary_position + ' / ' + data.position;
    }
    const age = getAge(data.birthDate)
    return (
        /* <---    Header Content split into Grid */
        
        <div className={styles.playerCardBox}>
            <div className={styles.playerNameBox}>
                {data.nameFull}
            </div>
            <div className={styles.playerInfoContainer}>
                <div className={styles.playerInfoBox}>
                    {position}
                </div>
                <div className={styles.playerInfoBox}>
                    Bats: {data.bats} / Throws: {data.throws}
                </div>
                <div className={styles.playerInfoBox}>
                    {height} / {data.wt} lbs
                </div>
                <div className={styles.playerInfoBox}>
                    Age: {age}
                </div>
            </div>
            <div className={styles.playerInfoContainer}>
                <div className={styles.playerInfoBox}>
                    Born: {data.birthCity}, {data.birthState}, {data.birthCountry} 
                </div>
                <div className={styles.playerInfoBox}>
                    {data.high_school}
                </div>
            </div>
        </div>
    )
}