import PlayerHeader from "./player-header"

export default function PlayerCard( {children} ) {
    const data = children

    return (
        <div>
            <PlayerHeader>{data}</PlayerHeader>
        </div>
    )
}