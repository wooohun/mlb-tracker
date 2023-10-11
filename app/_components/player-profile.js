import PlayerCard from "./player-card"
import styles from './player-card.module.css'
import PitchSplits from "./pitch-splits-card"

export default function PlayerProfile(props) {
    const data = props.children

    const pageType = data.primary_position.includes('P') ? 'pitching' : 'batting'

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            <div className="container mx-auto h-screen">
                <div className="grid grid-cols-3 h-max my-2">
                    <div className={styles.playerProfileModule}>
                        <PlayerCard displayType={pageType}>{data}</PlayerCard>
                    </div>
                    <div className={styles.playerProfileModule}>
                        <PitchSplits displayType={pageType}>{data.statcast}</PitchSplits>
                    </div>
                </div>
            </div>
        </div>
    )
}