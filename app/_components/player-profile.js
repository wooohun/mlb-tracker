'use client'

import PlayerCard from "./player-card"
import styles from './player-card.module.css'
import PitchSplits from "./pitch-splits-card"
import { useState } from 'react'

export default function PlayerProfile(props) {
    const data = props.children
    data['seasons'].sort((a, b) => a.year - b.year);
    data['statcast'].sort((a, b) => a.year - b.year);
    

    const [pageType, setPageType] = useState(data.primary_position.includes('P') ? 'pitching' : 'batting')

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            <div className="container mx-auto h-screen">
                <div className="grid grid-cols-3 my-2">
                    <div className={styles.playerProfileModule}>
                        <PlayerCard displayType={pageType} setPageType={setPageType}>{data}</PlayerCard>
                    </div>
                    <div className={styles.playerProfileModule}>
                        <PitchSplits displayType={pageType}>{data}</PitchSplits>
                    </div>
                </div>
            </div>
        </div>
    )
}