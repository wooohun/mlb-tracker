import ScheduleCell from "@/app/_components/schedule-cell";

export default function DailySchedule({children}) {
    const data = children

    return (
        <div>
            {data.map((game) => (
                <ScheduleCell key={game.id}>{game}</ScheduleCell>
            ))}
        </div>
    )
}