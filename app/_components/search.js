'use client'
import { useState } from "react"
import searchResult from "./search-result";


export default function Search() {
    const [query, setQuery] = useState("")
    const [queryResults, setQueryResults] = useState([]);

    const handleSearch = (e) => {
        setQuery(e.target.value);
        if (e.target.value != "") {
            
        }
    }

    return (
        <div>
            <div>
                <input 
                    placeholder="Search..." 
                    type="text" 
                    value={query}
                    onChange={handleSearch}
                />
                <button></button>
            </div>
            {queryResults.map((res) => (
                <searchResult key={res.id}>
                    {res}
                </searchResult>
            ))}
        </div>
    )
}