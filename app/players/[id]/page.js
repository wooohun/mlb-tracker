import { createEdgeRouter } from "next-connect";
import client from "@/middleware/mongoUtil";
import PlayerCard from "@/app/_components/player-card";

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
        <main>
            <div className="flex flex-col h-screen bg-gray-100">
                <div className="grid grid-cols-5 h-full">
                    <div className="p-4 col-start-2 col-span-3">
                        <div className="my-2 h-full">
                            <PlayerCard>{data}</PlayerCard>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    )
}