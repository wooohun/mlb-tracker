export const metadata = {
    title: 'Current MLB Standings'
}

export default function Layout({children}) {
    return (
        <div className="flex min-h-screen flex-col items-center justify-between p-24">
            {children}
        </div>
    )
}