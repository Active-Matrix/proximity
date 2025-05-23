'use client';
import NewsCard, {
	NewsCardProps,
} from '@/components/shared/news-card/news-card';
import NewsCardSkeleton from '@/components/shared/news-card/news-card-skeleton';
import { useEffect, useState } from 'react';

const SearchResultsGrid = () => {
	const [news, setNews] = useState<NewsCardProps[] | 'loading'>([]);

	useEffect(() => {
		setNews('loading');
		// simulate loading
		setTimeout(() => {
			setNews([
				{
					image:
						'https://ko77xaoqa4.ufs.sh/f/tCV5HvjhrFj7IdoJ5zuQoRFHJr4sv5UPGOuXKthkE83bW0i1',
					title:
						'SpaceX letter criticizes FAA for “systemic challenges” in launch licensing',
					publishedAt: '12 hours ago',
					reads: '43k',
					slug: 'spacex-letter-criticizes-faa-for-systemic-challenges-in-launch-licensing-2vg45',
					source: {
						name: 'CNN',
						image: '',
						url: 'https://www.cnn.com/',
					},
				},
				{
					image:
						'https://utfs.io/f/tCV5HvjhrFj78ppsNbrmDKZ6LVIqCe2WQuHiMNX41BYwsvEd',
					title: 'India eyes record year for space with 10 planned launches',
					publishedAt: '5 hours ago',
					source: {
						name: 'CNN',
						image: '',
						url: 'https://www.cnn.com/',
					},					reads: '28k',
					slug: 'india-eyes-record-year-for-space-with-10-planned-launches-245626',
				},
				{
					image:
						'https://utfs.io/f/tCV5HvjhrFj7e9NgBZxqDOE9pI4s2uQrfZnahoL6R8vM03SV',
					title: 'Lockheed Martin challenges narrative on GPS vulnerability',
					publishedAt: '12 hours ago',
					source: {
						name: 'CNN',
						image: '',
						url: 'https://www.cnn.com/',
					},					reads: '43k',
					slug: 'lockheed-martin-challenges-narrative-on-gps-vulnerability-2456256',
				}
			]);
		}, 1000);
	}, []);

	return (
		<section className="gap-6 pb-6 grid grid-cols-1 w-full h-full">
			{news === 'loading'
				? Array.from({ length: 5 }).map((_, i) => <NewsCardSkeleton key={i} />)
				: news.map((news) => (
						<NewsCard
							key={news.slug}
							slug={news.slug}
							title={news.title}
							image={news.image}
							publishedAt={news.publishedAt}
							source={news.source}
							reads={news.reads}
						/>
					))}
		</section>
	);
};

export default SearchResultsGrid;
