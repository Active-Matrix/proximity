'use client';
import SearchBar from '@/components/shared/search-bar/search-bar';
import { useSearchStore } from '@/stores/search-store';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect } from 'react';

const TopicSearch = () => {
	const router = useRouter();
	const { setQuery, query } = useSearchStore();
	const searchParams = useSearchParams();

	useEffect(() => {
		const newQuery = searchParams.get('q') || '';
		if (query !== newQuery) setQuery(newQuery);
	}, [searchParams, setQuery, query]);

	return (
		<SearchBar
			icon="chevron"
			onContainerClick={() => router.push('/explore')}
			readonly={true}
		/>
	);
};

export default TopicSearch;
