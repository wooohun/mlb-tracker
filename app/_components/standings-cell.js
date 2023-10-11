export default function StandingsCell(props) {
    const data = props.children
    return (
        <div>
            {data.map((team) => (
                <div key={team.id} className="grid grid-flow-row auto-rows-fr grid-cols-6 p-4 border-b-2 border-black last:border-b-0">
                    <div className="col-span-3">
                        <p>{team.market} {team.name}</p>
                    </div>
                    <div className="col-span-2">
                        {`(${team.win}-${team.loss})`}
                    </div>
                    <div>
                        {team.win_p}
                    </div>
                </div>
            ))}
        </div>
    )
}