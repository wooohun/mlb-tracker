
export async function generateStaticParams() {
    const url = `http://api.sportradar.us/mlb/trial/v7/en/teams/${id}/profile.json?api_key=${process.env.API_KEY}`
    const teamData = await fetch(url).then((res) => res.json())

    return teamData.map((team) => ({
        playerId: team.players.id
    }))
}

// async function getTeamData(id) {
//     const url = `http://api.sportradar.us/mlb/trial/v7/en/teams/${id}/profile.json?api_key=${process.env.API_KEY}`
//     const res = await fetch(url)
//     if (!res.ok) {
//         throw new Error(`Error: ${res.statusText}`);
//     }

//     return res.json()
// }


export default async function Page({ params }) {
    const team = await getTeamData(id)
    return (
        <main>
            <div>
                <h2>{team.market} {team.name}</h2>
                <h1>{team.abbr}</h1>
                <div>
                    <p>
                        {team.league.name}
                    </p>
                </div>
            </div>
        </main>
    )
}