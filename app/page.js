import { NextResponse } from "next/server"
import { getDailyBoxScores, getDailySchedule, getStandings } from "./api/routes";
import Link from "next/link";
import Standings from "./(standings)/standings/page";
import DailySchedule from "./(schedule)/daily/page";


export default async function Home() {

    // const data = await getDailyBoxScores();
    const dailySchedule = await getDailySchedule();
    const standings = await getStandings();
    return (
        <div className="flex min-h-screen flex-row items-center justify-around p-24">
            <div className="basis-2/3">
                <DailySchedule>{dailySchedule}</DailySchedule>
            </div>
            <div className="basis-1/4">
                <Standings>{standings}</Standings>
            </div>
        </div>
  )
}
