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
                <Link href={`/players/d3351c6e-12cf-4ab5-b651-ad23d49c4245`}>Kershaw</Link>
            </div>
        </div>
  )
}
