'use client';

import Image from 'next/image';
import { Popup } from '@/types/popup';
import { CalendarDays, MapPin } from 'lucide-react';

interface FeedItemProps {
	popup: Popup;
}

export default function FeedItem({ popup }: FeedItemProps) {
	return (
		<div className="bg-white border text-black border-gray-200 rounded-lg overflow-hidden mb-6 shadow-sm">
			{/* Header */}
			<div className="p-3 flex items-center">
				<div className="h-8 w-8 rounded-full bg-gradient-to-tr from-yellow-400 to-fuchsia-600 p-[2px]">
					<div className="h-full w-full rounded-full bg-white flex items-center justify-center text-xs font-bold overflow-hidden">
						IMG
					</div>
				</div>
				<div className="ml-3">
					<p className="font-semibold text-sm">{popup.source}</p>
					<p className="text-xs text-gray-500">Suggested for you</p>
				</div>
			</div>

			{/* Image */}
			<div className="relative aspect-square w-full">
				<Image
					src={popup.image_url}
					alt={popup.title}
					fill
					className="object-cover"
				/>
			</div>

			{/* Actions (Like/Comment/Share placeholder) */}
			<div className="p-3">
				<div className="flex justify-between mb-2">
					<div className="flex space-x-4">
						<button className="hover:opacity-50">
							<svg aria-label="Like" className="w-6 h-6" fill="none" height="24" role="img" viewBox="0 0 24 24" width="24"><path d="M16.792 3.904A4.989 4.989 0 0 1 21.5 9.122c0 3.072-2.652 4.956-5.197 7.222-2.512 2.243-3.865 3.469-4.303 3.752-.477-.309-2.143-1.823-4.303-3.752C5.141 14.072 2.5 12.167 2.5 9.122a4.989 4.989 0 0 1 4.708-5.218 4.21 4.21 0 0 1 3.675 1.941c.84 1.175.98 1.763 1.12 1.763s.278-.588 1.11-1.766a4.17 4.17 0 0 1 3.679-1.938m0-2a6.04 6.04 0 0 0-4.797 2.127 6.052 6.052 0 0 0-4.787-2.127A6.985 6.985 0 0 0 .5 9.122c0 3.61 2.55 5.827 5.015 7.97.283.246.569.494.853.747l1.027.918a44.998 44.998 0 0 0 3.518 3.018 2 2 0 0 0 2.174 0 45.263 45.263 0 0 0 3.626-3.115l.922-.824c.293-.26.59-.519.885-.774 2.334-2.025 4.98-4.32 4.98-7.94a6.985 6.985 0 0 0-6.708-7.218Z" fill="black"></path></svg>
						</button>
						<button className="hover:opacity-50">
							<svg aria-label="Comment" className="w-6 h-6" fill="none" height="24" role="img" viewBox="0 0 24 24" width="24"><title>Comment</title><path d="M20.656 17.008a9.993 9.993 0 1 0-3.59 3.615L22 22Z" fill="none" stroke="black" strokeLinejoin="round" strokeWidth="2"></path></svg>
						</button>
						<button className="hover:opacity-50">
							<svg aria-label="Share Post" className="w-6 h-6" fill="none" height="24" role="img" viewBox="0 0 24 24" width="24"><title>Share Post</title><line fill="none" stroke="black" strokeLinejoin="round" strokeWidth="2" x1="22" x2="9.218" y1="3" y2="10.083"></line><polygon fill="none" points="11.698 20.334 22 3.001 2 3.001 9.218 10.084 11.698 20.334" stroke="black" strokeLinejoin="round" strokeWidth="2"></polygon></svg>
						</button>
					</div>
					<button className="hover:opacity-50">
						<svg aria-label="Save" className="w-6 h-6" fill="none" height="24" role="img" viewBox="0 0 24 24" width="24"><title>Save</title><polygon fill="none" points="20 21 12 13.44 4 21 4 3 20 3 20 21" stroke="black" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"></polygon></svg>
					</button>
				</div>

				<p className="font-semibold text-sm mb-1">{popup.title}</p>
				<p className="text-sm text-gray-800 line-clamp-2 mb-2">
					{popup.description}
				</p>

				<div className="flex items-center text-xs text-gray-500 mb-1">
					<CalendarDays className="w-3 h-3 mr-1" />
					<span>{popup.start_date} ~ {popup.end_date}</span>
				</div>
				<div className="flex items-center text-xs text-gray-500">
					<MapPin className="w-3 h-3 mr-1" />
					<span>{popup.location}</span>
				</div>
			</div>
		</div>
	);
}
