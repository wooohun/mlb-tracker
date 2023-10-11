import PitcherCard from "./pitcher-card"
import BatterCard from "./batter-card"

export default function PlayerCard({displayType, children}) {
    const data = children

    return displayType == 'batting' ? (
        <BatterCard>{data}</BatterCard>
    ) : (
        <PitcherCard>{data}</PitcherCard>
    )
}