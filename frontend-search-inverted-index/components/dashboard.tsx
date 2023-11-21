import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from "@nextui-org/table";
import { Link } from "@nextui-org/link";
import { useEffect, useState } from 'react'

type Track = {
    track_id: string,
    similarity: number
}

type Response = {
    code: number,
    results: Track[],
    time: number
}

type Row = {
    title: string,
    author: string,
    lyrics: string,
    similarity: number,
    spotify_link: string
}

const SPOTIFY_TOKEN = "poner api de SPOTIFY aqui"

export default function Dashboard({
    query,
    k,
    language
}: {
    query: string,
    k: number,
    language: string
}) {
    const [data, setData] = useState<Row[]>([])
    const [time, setTime] = useState<number>(0)

    useEffect(() => {
        setData([])
        setTime(0)
        fetch("http://localhost:8000/search", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "query": query,
                "k": k,
                "language": language
            })
        })
            .then(response => response.json())
            .then((_data : Response) => {
                setTime(_data.time);
                _data.results.forEach(async (element: Track) => {
                    const res = await fetch(`https://api.spotify.com/v1/tracks/${element.track_id}`, {
                        method: 'GET',
                        headers: {
                            Authorization: `Bearer ${SPOTIFY_TOKEN}`,
                            'Content-Type': 'application/json'
                        }
                    })
                    const dt = await res.json()
                    setData((prev : Row[]) => {

                        const newRow : Row = {
                            title: dt.name,
                            author: dt.artists[0].name,
                            lyrics: "",
                            similarity: element.similarity,
                            spotify_link: dt.external_urls.spotify
                        }

                        const ordered = [...prev, newRow].sort((a, b) => b.similarity - a.similarity)

                        return ordered;
                    })
                });
            })
    }, [query, k, language])

    return (
        <div className="w-full flex flex-col gap-2">
            <Table aria-label="Example static collection table">
                <TableHeader>
                    <TableColumn>Title</TableColumn>
                    <TableColumn>Author</TableColumn>
                    <TableColumn>Lyrics</TableColumn>
                    <TableColumn>Similarity</TableColumn>
                    <TableColumn>Spotify Link</TableColumn>
                </TableHeader>
                <TableBody emptyContent="Searching...">
                    {
                        data.length ? data.map((item, index) => (
                            <TableRow key={index}>
                                <TableCell>{item.title}</TableCell>
                                <TableCell>{item.author}</TableCell>
                                <TableCell>{item.lyrics}</TableCell>
                                <TableCell>{item.similarity}</TableCell>
                                <TableCell><Link isExternal href={item.spotify_link} underline="hover" showAnchorIcon>{item.spotify_link}</Link></TableCell>
                            </TableRow>
                        )) : []
                    }
                </TableBody>
            </Table>
            <span className={time ? "text-small text-end text-default-400 mr-5" : "hidden"}>{`Search in ${time} seconds.`}</span>
        </div>
    )
}