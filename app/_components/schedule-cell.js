import { getGameSummary } from "../api/routes"
import MatchupCell from "./matchup-cell"

export default async function ScheduleCell({children}) {
    const data = children
    const gameInfo = await getGameSummary(data.id)

    const homeTeam = data.home
    const awayTeam = data.away
    
    return (
        <div className="border-2 border-black" key={data.id}>
            <MatchupCell game={gameInfo.game.home}>{homeTeam}</MatchupCell>
            <MatchupCell game={gameInfo.game.away}>{awayTeam}</MatchupCell>
        </div>
    )
}