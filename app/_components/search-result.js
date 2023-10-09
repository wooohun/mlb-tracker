export default function searchResult({children}){
    const data = children

    return (
        <div>
            <div>
                {data.first_name} {data.last_name}
                <div>
                    {data.team.name} {data.team.market}
                </div>
            </div>
            <div>
                {data.primary_position}
            </div>
        </div>
    )
}