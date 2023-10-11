'use client'

import LeagueStandings from './league/page';
import React, { useState, useEffect } from 'react'

export default function Standings({ children }) {
    const leagues = children.leagues;

    const [league, setLeagues] = useState(leagues[0]);

    function handleClick(league) {
        setLeagues(league);
    }

    return (
        <div className='flex flex-col justify-evenly box-border text-center'>
            <div className='flex flex-row'>
                {leagues.map((l) => (
                    <div key={l.id} className='flex grow border-2 border-black'>
                        <button onClick={() => handleClick(l)} className='grow'>{l.alias}</button>
                    </div>
                ))}
            </div>
            <LeagueStandings key={league.id}>{league.divisions}</LeagueStandings>
        </div>
    )
}