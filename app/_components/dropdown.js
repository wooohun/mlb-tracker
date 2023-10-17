import { useEffect } from 'react'
import styles from './visuals.module.css'
import { Menu } from '@headlessui/react'


export default function Dropdown( { onClick, cur_year, children } ) {
    
    function handleSeasonChange(e) {
        let target = e.target.innerHTML
        onClick(target)
    }
    return (
        <Menu as="div" className='relative'>
            <Menu.Button className={styles.dropdownButton}>
                {cur_year}
            </Menu.Button>
            <Menu.Items className='absolute z-1000 bg-white border-black border'>
                {children.map((year, idx) => (
                    <Menu.Item 
                        as='div' 
                        key={idx} 
                        className={styles.dropdownItem}
                    >
                        <button 
                            className={styles.dropdownItemContent}
                            onClick={handleSeasonChange}
                        >
                            {year}
                        </button>
                    </Menu.Item>
                ))}
            </Menu.Items>
        </Menu>
    )
}