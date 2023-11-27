import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from "@nextui-org/table";
import { Link } from "@nextui-org/link";
import { Button } from "@nextui-org/button";
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
    similarity: number,
    spotify_link: string
}

type KnnRow = {
    title: string,
    author: string,
    distance: number,
    spotify_link: string
}

const SPOTIFY_TOKEN = "BQBtM7RAJqN3w26nKcXVRYvT13fephNzpXH69iNaVuSAr_JFsx_6GhN3kTTRbdHovsgGnu1VK5y8ICvr9TMZuFjpQveooP5fEjqtm2KORDWAUHCZQ10"

export default function Dashboard({
    query,
    k,
    language,
    index
}: {
    query: string,
    k: number,
    language: string,
    index: string
}) {
    const [data, setData] = useState<Row[]>([])
    const [time, setTime] = useState<number>(0)

    const [knnResult, setKnnResult] = useState<KnnRow[]>([])
    const [knnTime, setKnnTime] = useState<number>(0)

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
                "language": language,
                "index": index
            })
        })
            .then(response => response.json())
            .then((_data: Response) => {
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
                    setData((prev: Row[]) => {

                        const newRow: Row = {
                            title: dt.name,
                            author: dt.artists[0].name,
                            similarity: element.similarity,
                            spotify_link: dt.external_urls.spotify
                        }

                        const ordered = [...prev, newRow].sort((a, b) => b.similarity - a.similarity)

                        return ordered;
                    })
                });
            })
    }, [query, k, language, index])

    const [notFound, setNotFound] = useState<boolean>(false)
    const [search, setSearch] = useState<Row>({
        title: "",
        author: "",
        similarity: 0,
        spotify_link: ""
    })

    const handleClick = (item: Row) => {
        const trackid = item.spotify_link.substring(31)
        setKnnResult([])
        setKnnTime(0)
        fetch("http://localhost:8080/search", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "trackid": trackid,
                "k": 5
            })
        })
            .then(response => response.json())
            .then((_data: Response) => {
                if (_data.code == 404) {
                    setNotFound(true)
                    return
                }

                setNotFound(false)
                setKnnTime(_data.time);
                setSearch(item)
                _data.results.forEach(async (element: any) => {
                    const res = await fetch(`https://api.spotify.com/v1/tracks/${element.track_id}`, {
                        method: 'GET',
                        headers: {
                            Authorization: `Bearer ${SPOTIFY_TOKEN}`,
                            'Content-Type': 'application/json'
                        }
                    })
                    const dt = await res.json()
                    setKnnResult((prev: KnnRow[]) => {

                        const newRow: KnnRow = {
                            title: dt.name,
                            author: dt.artists[0].name,
                            distance: element.distance,
                            spotify_link: dt.external_urls.spotify
                        }

                        const ordered = [...prev, newRow].sort((a, b) => a.distance - b.distance)

                        return ordered;
                    })
                });
            })
    }

    return (
        <div className="w-full flex flex-col gap-2">
            <Table aria-label="Example static collection table">
                <TableHeader>
                    <TableColumn>Title</TableColumn>
                    <TableColumn>Author</TableColumn>
                    <TableColumn>Similarity</TableColumn>
                    <TableColumn>Spotify Link</TableColumn>
                    <TableColumn>Search 5 NN</TableColumn>
                </TableHeader>
                <TableBody emptyContent="Searching...">
                    {
                        data.length ? data.map((item, index) => (
                            <TableRow key={index}>
                                <TableCell>{item.title}</TableCell>
                                <TableCell>{item.author}</TableCell>
                                <TableCell>{item.similarity}</TableCell>
                                <TableCell><Link isExternal href={item.spotify_link} underline="hover" showAnchorIcon>{item.spotify_link}</Link></TableCell>
                                <TableCell><Button color="primary" variant="bordered" onClick={() => handleClick(item)}>Search</Button></TableCell>
                            </TableRow>
                        )) : []
                    }
                </TableBody>
            </Table>
            <span className={time ? "text-small text-end text-default-400 mr-5" : "hidden"}>{`Search in ${time} seconds.`}</span>
            <h1 className="text-3xl font-semibold mt-5">{search.title ? `Results for "${search.title} - ${search.author}" using multidimensional index.` : ""}</h1>
            <Table aria-label="Results of Search">
                <TableHeader>
                    <TableColumn>Title</TableColumn>
                    <TableColumn>Author</TableColumn>
                    <TableColumn>Distance</TableColumn>
                    <TableColumn>Spotify Link</TableColumn>
                </TableHeader>
                <TableBody emptyContent={notFound ? "Now we don't have that song ):" : "Select a song to start multidimensional index search."}>
                    {
                        knnResult.length ? knnResult.map((item, index) => (
                            <TableRow key={index}>
                                <TableCell>{item.title}</TableCell>
                                <TableCell>{item.author}</TableCell>
                                <TableCell>{item.distance}</TableCell>
                                <TableCell><Link isExternal href={item.spotify_link} underline="hover" showAnchorIcon>{item.spotify_link}</Link></TableCell>
                            </TableRow>
                        )) : []
                    }
                </TableBody>
            </Table>
            <span className={knnTime ? "text-small text-end text-default-400 mr-5" : "hidden"}>{`Search in ${knnTime} ms.`}</span>
        </div>
    )
}