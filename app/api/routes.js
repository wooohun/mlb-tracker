// HELPER FUNCTIONS TO CALL SPECIFIC API ENDPOINTS


import { NextResponse } from "next/server";
import { revalidatePath } from "next/cache";


export function getDate(){
    const today = new Date();
    const dd = String(today.getDate()).padStart(2, '0');
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const yyyy = today.getFullYear();

    return { dd: dd, mm: mm, yyyy: yyyy };
}

export async function getDailyBoxScores() {
    let curDate = getDate();

    const url = `https://api.sportradar.us/mlb/trial/v7/en/games/${curDate.yyyy}/${curDate.mm}/${curDate.dd}/boxscore.json?api_key=${process.env.API_KEY}`

    const res = await fetch(url)

    if (!res.ok) {
        throw new Error(`Error: ${res.statusText}`);
    }

    return res.json()
}

export async function getStandings() {
    let curDate = getDate();

    const url = `https://api.sportradar.us/mlb/trial/v7/en/seasons/${curDate.yyyy}/REG/rankings.json?api_key=${process.env.API_KEY}`

    const res = await fetch(url);
    const data = await res.json();
    return data
}

export async function getDailySchedule() {
    let curDate = getDate();

    const url = `https://api.sportradar.us/mlb/trial/v7/en/games/${curDate.yyyy}/${curDate.mm}/${curDate.dd}/schedule.json?api_key=${process.env.API_KEY}`

    const data = await fetch(url).then((res) => res.json())

    const res = data.games.sort((a, b) => {

        first = Date.parse(a.scheduled)
        second = Date.parse(b.scheduled)

        if (first > second) {
            return 1;
        }
        if (first < second) {
            return -1;
        }
        return 0
    })

    return res
}