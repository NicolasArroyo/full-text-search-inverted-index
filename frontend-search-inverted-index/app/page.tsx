'use client'
import { Input } from "@nextui-org/input";
import { Select, SelectItem } from "@nextui-org/select"
import { languages } from "@/components/languages";
import { useForm, SubmitHandler } from "react-hook-form"
import { Button } from "@nextui-org/button";

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

	const onSubmit: SubmitHandler<Inputs> = (data) => {
		console.log(data)
	}

	return (
		<div>
			<form action="" className="flex gap-5 items-center" onSubmit={handleSubmit(onSubmit)}>
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
		</div>
	);
}
