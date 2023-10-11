'use client'

import React, { useEffect, useRef } from 'react'
import * as d3 from 'd3'

const MARGIN = { top: 5, right: 5, bottom: 5, left: 5};

export default function DumbbellChart({ width, height, data}) {

    var svg = d3.select('#chart')
        .append("svg")

    return (
        <div id='chart'>
            <svg width={width} height={height}>
                <g>
                    
                </g>
            </svg>
        </div>
    )
}