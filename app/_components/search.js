'use client'
import { useState } from "react"
import { Combobox } from "@headlessui/react";
import searchResult from "./search-result";
import { Combo } from "next/font/google";


export default function Search({setPage}) {
    const [query, setQuery] = useState("")
    const [queryResults, setQueryResults] = useState([]);

    const handleSearch = (e) => {
        setQuery(e.target.value);
        if (e.target.value != "") {
            
        }
    }
    const filteredQuery = 
        query === ''
            ? 

    return (
        // <div>
        //     <div>
        //         <input 
        //             placeholder="Search..." 
        //             type="text" 
        //             value={query}
        //             onChange={handleSearch}
        //         />
        //         <button></button>
        //     </div>
        //     {queryResults.map((res) => (
        //         <searchResult key={res.id}>
        //             {res}
        //         </searchResult>
        //     ))}
        // </div>
        <Combobox value={queryResults} onChange={setQueryResults}>
            <Combobox.Input onChange={(e) => setQuery(e.target.value)}/>
            <Combobox.Options>

            </Combobox.Options>
        </Combobox>
    )
}