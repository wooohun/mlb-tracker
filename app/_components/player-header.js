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

    const bday = dateReformat(data.birthdate)
    const debut = dateReformat(data.pro_debut)

    const height = convertHeight(data.height)['imperial']

    // if (data.position == 'IF' || data.position == 'OF') {
    //     var position = positions[data.primary_position];
    // } else {
    //     var position = positions[data.primary_position] + ' and ' + positions[data.position];
    // }

    if (data.position == 'IF' || data.position == 'OF') {
        var position = data.position;
    } else {
        var position = data.primary_position + ' / ' + data.position;
    }
    const age = getAge(data.birthdate)
    return (
        /* <---    Header Content split into Grid */
        /*
            <div>
                <div>
                    <div>
                    </div>
                </div>
            </div>
        */
            <div className={styles.playerCardBox}>
                <div className={styles.playerNameBox}>
                    <h1 className={styles.playerName}>{data.preferred_name} {data.last_name}</h1>
                    <div>
                        <Link href={`teams/${data.team.id}`} className="hover:text-mlb-red">{data.team.market} {data.team.name}</Link>
                    </div>
                </div>
                <div className={styles.playerInfoBox}>
                    Age: {age}
                </div>
                <div className={styles.playerInfoBox}>
                    {height} / {data.weight}
                </div>
                <div className={styles.playerInfoBox}>
                    Bats: {data.bat_hand} / Throws: {data.throw_hand}
                </div>
                <div className={styles.playerInfoBox}>
                    {position}
                </div>
                <div className={styles.playerNumberBox}>
                    #{data.jersey_number}
                </div>
            </div>
    )
}