export function StandingsCell(props) {
    const data = props.children
    return (
        <div className="">
            {data.map((team) => (
                <div className="grid grid-cols-3 gap-12 p-4">
                    <div className="col-span-2">
                        <p>{team.market} {team.name}</p>
                    </div>
                    <div>
                        W/L Here
                    </div>
                </div>
            ))}
        </div>
    )
}