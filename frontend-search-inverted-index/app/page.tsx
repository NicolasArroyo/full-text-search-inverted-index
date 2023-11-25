'use client'
import { Input } from "@nextui-org/input";
import { Select, SelectItem } from "@nextui-org/select"
import { languages } from "@/components/languages";
import { useForm, SubmitHandler } from "react-hook-form"
import { Button } from "@nextui-org/button";
import Dashboard from "@/components/dashboard";
import { useState } from "react";
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from "@nextui-org/table";

type Inputs = {
	query: string
	topk: number
	lang: string
}

export default function Home() {

	const {
		register,
		handleSubmit,
		watch,
		formState: { errors },
	} = useForm<Inputs>()

	const [data, setData] = useState<Inputs>({
		query: "",
		topk: 0,
		lang: ""
	});

	const onSubmit: SubmitHandler<Inputs> = (_data) => {
		setData(_data);
	}

	return (
		<div>
			<form action="" className="flex gap-5 items-center mb-10" onSubmit={handleSubmit(onSubmit)}>
				<Input
					isRequired
					type="text"
					label="Query"
					placeholder="Good Kid"
					{...register("query")}
				/>

				<Input
					isRequired
					type="number"
					label="Top K"
					placeholder="5"
					className="max-w-[100px]"
					{...register("topk")}
				/>

				<Select
					isRequired
					label="Select the language"
					className="max-w-xs"
					{...register("lang")}
				>
					{Object.keys(languages).map((lang) => (
						<SelectItem key={languages[lang as keyof typeof languages]} value={languages[lang as keyof typeof languages]}>
							{lang}
						</SelectItem>
					))}
				</Select>

				<Button
					color="primary"
					type="submit"
				>Search</Button>
			</form>
			<div className="w-full flex justify-center items-center">
				{data.query != "" ?
					<Dashboard query={data.query} k={data.topk} language={data.lang} />
					: <Table aria-label="Results of Search">
						<TableHeader>
							<TableColumn>Title</TableColumn>
							<TableColumn>Author</TableColumn>
							<TableColumn>Similarity</TableColumn>
							<TableColumn>Spotify Link</TableColumn>
						</TableHeader>
						<TableBody emptyContent={"Haz tu primera busqueda."}>{[]}</TableBody>
					</Table>
				}
			</div>
		</div>
	);
}
