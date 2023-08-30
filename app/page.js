import { NextResponse } from "next/server"
import { getDailyBoxScores, getStandings } from "./api/routes";
import Link from "next/link";
import Standings from "./(standings)/standings/page";


export default async function Home() {

    // const data = await getDailyBoxScores();
    const standings = await getStandings();
    return (
        <main className="flex min-h-screen flex-col items-center justify-between p-24">
            <div>
            </div>
            <div>
                <Standings>{standings}</Standings>
            </div>
        </main>
  )
}
