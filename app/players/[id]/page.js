import client from "@/middleware/mongoUtil";
import PlayerProfile from "@/app/_components/player-profile";

async function GET(player_id){
    var db = await client.db('mlbDB');
    const playerColl = await db.collection('playerProfiles')
    const playerData = await playerColl.findOne(
        {id: player_id},
        {projection: {_id: 0}}
    )

    return playerData
}


export default async function PlayerInfo({ params }) {
    const player_id = params.id;
    
    const data = await GET(player_id)
    return (
        <PlayerProfile>{data}</PlayerProfile>
    )
}