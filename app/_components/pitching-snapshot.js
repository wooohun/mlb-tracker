'use client'

import PieChart from "./pie-graph"

export default function PitchingSnapshot({ children }) {
    const data = children
    const pitchTypes = data.totals.statcast_metrics.pitching.pitch_types
    
    // var pitchTypeData = {
    //     labels: [],

    // }
    // for (let i=0; i < pitchTypes.length; i++){
    //     pitchTypeData[labels].push(pitchTypes[i][])
    // }

    // for (let pitch of pitchTypes) {
    //     pitchTypeData[labels].push(pitch.type)
    // }
    return (
        <div>
            <div>
                <PieChart>{pitchTypes}</PieChart>
            </div>
        </div>
    )
}