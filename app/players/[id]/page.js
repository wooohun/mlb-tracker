export async function generateStaticParams({ params: { id }}) {
    const data = await fetch(`http://api.sportradar.us/mlb/trial/v7/en/players/${id}/profile.json?api_key=${process.env.API_KEY}}`)
    .then((res) => res.json())

    return data
}

export default async function PlayerInfo({ params }) {
    const data = params

    return (
        <main>
            <div>
                <h1>{data.full_name}</h1>
                <h3>{data.primary_position}</h3>
                <h4>{data.birthdate}</h4>
                <div>
                    <p>T: {data.throw_hand}/ B: {data.bat_hand}</p>
                </div>
            </div>
            <div>
                
            </div>
        </main>
    )
}