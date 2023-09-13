import Link from "next/link"
import styles from './schedule-cell.module.css'

export default function MatchupCell(props) {
    const data = props.children
    const gameInfo = props.game
    return (
        <div className="grid grid-cols-3 p-4">
            <div className="col-span-2">
                <Link href={`/teams/${data.id}`}>
                    {data.market} {data.name}
                </Link>
            </div>
            <div>
                {gameInfo.runs}
            </div>
        </div>
    )
}