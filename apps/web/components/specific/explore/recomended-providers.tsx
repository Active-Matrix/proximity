import Image from 'next/image';
import Link from 'next/link';

const RecomendedProviders = () => {
	const providers = [
		{
			id: 'tCV5HvjhrFj7UtCdECs74lthix7YbsZFHMvC53fkpBW1r2IO',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj7UtCdECs74lthix7YbsZFHMvC53fkpBW1r2IO',
		},
		{
			id: 'tCV5HvjhrFj779JC3c16RzKMGWPaoxlbmCA4V0N8Z3wUHTed',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj779JC3c16RzKMGWPaoxlbmCA4V0N8Z3wUHTed',
		},
		{
			id: 'tCV5HvjhrFj7ckBobqnNkxa7TBAh20FSOVg4Lldpt3eMjDKb',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj7ckBobqnNkxa7TBAh20FSOVg4Lldpt3eMjDKb',
		},
		{
			id: 'tCV5HvjhrFj7KMYiLGVPmdVsui3vJ1g7MYaA2LcfGqE5nlUo',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj7KMYiLGVPmdVsui3vJ1g7MYaA2LcfGqE5nlUo',
		},
		{
			id: 'tCV5HvjhrFj77j4bVgY16RzKMGWPaoxlbmCA4V0N8Z3wUHTe',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj77j4bVgY16RzKMGWPaoxlbmCA4V0N8Z3wUHTe',
		},
		{
			id: 'tCV5HvjhrFj7wYuhu4pRbcKf5Bzj6EXs14xoHqm3JwTk8aiV',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj7wYuhu4pRbcKf5Bzj6EXs14xoHqm3JwTk8aiV',
		},
		{
			id: 'tCV5HvjhrFj7OuuQmIs8U2XFd7vn9YBVWsxoaP4j3iD1byMr',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj7OuuQmIs8U2XFd7vn9YBVWsxoaP4j3iD1byMr',
		},
		{
			id: 'tCV5HvjhrFj70QUibYDrVW7IbkMm6Gnhdewja5PRCzAL3fDg',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj70QUibYDrVW7IbkMm6Gnhdewja5PRCzAL3fDg',
		},
		{
			id: 'tCV5HvjhrFj7Al0k2KoQ2M0UGsxT3Li1eYlgDhHwnmPkprWI',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj7Al0k2KoQ2M0UGsxT3Li1eYlgDhHwnmPkprWI',
		},
		{
			id: 'tCV5HvjhrFj7zmZOBBqwEZrYT1mnJ6XDvHc3A9yKM4tegq0S',
			url: 'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj7zmZOBBqwEZrYT1mnJ6XDvHc3A9yKM4tegq0S',
		},
	];

	return (
		<div className="grid grid-cols-5 gap-4">
			{providers.map((provider) => (
				<Link
					key={provider.id}
					href={`/provider/${provider.id}`}
					className="h-16 w-16 rounded-full bg-[#d9d9d988] center opacity-80 p-4"
				>
					<Image
						src={provider.url}
						alt="provider avatar"
						height={48}
						width={48}
						className="full object-center object-contain brightness-200 contrast-200 max-h-12 max-w-12"
					/>
				</Link>
			))}
		</div>
	);
};

export default RecomendedProviders;
