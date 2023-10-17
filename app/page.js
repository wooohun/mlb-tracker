import { NextResponse } from "next/server"
import Link from "next/link";
import Standings from "./(standings)/standings/page";
import DailySchedule from "./(schedule)/daily/page";
import PlayerInfo from "./players/[id]/page";
import client from "@/middleware/mongoUtil";


export default async function Home() {
    const yyyy = new Date().getFullYear();

    var db = client.db('mlbDB')
    const standingsColl = await db.collection('standings')
    const standingsData = await standingsColl.findOne(
        {year: yyyy},
        {projection: {_id: 0}}
    )
    // const data = await getDailyBoxScores();
    // const dailySchedule = await getDailySchedule();
    return (
        <div className="flex h-full flex-row items-center justify-around p-24">
            <div className="basis-2/3">
                {/* <DailySchedule>{dailySchedule}</DailySchedule> */}
            </div>
            <div className="basis-1/4">
                <Standings>{standingsData}</Standings>
            </div>
            <div>
                <Link href={`/players/80de60c9-74e3-4a50-b128-b3dc7456a254`}>Ohtani</Link>
            </div>
        </div>
  )
}
