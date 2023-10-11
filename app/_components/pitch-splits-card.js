'use client'

import PitchRadarGraph from "./pitch-radar-graph"
import DumbbellChart from "./dumbbell-chart"
import React, { useState } from 'react'

export default function PitchSplits({displayType, children}) {
    const data = children

    const pitch_labels = {
        'AVG_SPEED': 'Avg Speed',
        'AVG_SPIN': 'Avg Spin',
        'run_value': 'Run Value',
        'whiff_pct': 'Whiff %',
        'k_pct': 'K %',
        'est_ba': 'xBA',
    }

    const years = data.map(({year}) => year)
    const graphData = data.find(obj => obj.year)

    const [season, setSeason] = useState(years[0])

    function changeYear(year) {

    }

    return (
        <div>
            <div>
                <div>
                    <button>

                    </button>
                    <div>

                    </div>
                </div>
            </div>
            {/* <div className="flex flex-wrap">
                {Object.keys(pitch_labels).map(()=> (
                    <<div>
                        <DumbbellChart ></DumbbellChart>
                     </div>   >
                ))}
            </div> */}
            <PitchRadarGraph displayType={displayType} statcast={graphData}></PitchRadarGraph>
        </div>
    )
}