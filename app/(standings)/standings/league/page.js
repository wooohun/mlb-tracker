import StandingsCell from "@/app/_components/standings-cell"

export default function LeagueStandings(props) {
    const data = props.children
    return (
        <div className="border-x-2 border-black last:border-b-2">
            {data.map((division) => (
                <div key={division.id}>
                    <div className="p-1 text-lg bg-black text-white">
                        {division.name}
                    </div>
                    <StandingsCell>{division.teams}</StandingsCell>
                </div>
            ))}
        </div>
    )
}